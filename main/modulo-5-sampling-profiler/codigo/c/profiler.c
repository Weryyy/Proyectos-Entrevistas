/*
 * ============================================================================
 *  Módulo 5: El Detective de Código — Sampling Profiler
 * ============================================================================
 *
 *  Este archivo implementa un sampling profiler que reconstruye la línea de
 *  tiempo de ejecución de un programa a partir de muestras periódicas del
 *  call stack.
 *
 *  CONCEPTO CLAVE: Stack Diffing
 *  ─────────────────────────────
 *  Comparamos muestras consecutivas del stack desde la raíz. Donde divergen,
 *  las funciones anteriores terminaron y las nuevas comenzaron. Es como
 *  comparar fotogramas consecutivos de una cámara de seguridad para detectar
 *  movimiento.
 *
 *  Ejemplo:
 *    Muestra 1: [main, procesar, calcular]
 *    Muestra 2: [main, procesar, ordenar]
 *                       ↑ divergencia en índice 2
 *    → calcular() TERMINÓ, ordenar() INICIÓ
 *
 * ============================================================================
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "profiler.h"

/* ─────────────────────────────────────────────────────────────────────────────
 * find_divergence_point: Encuentra dónde dos stacks difieren
 * ─────────────────────────────────────────────────────────────────────────────
 *
 * Compara dos muestras del stack frame por frame, empezando desde la raíz
 * (índice 0, que típicamente es main()). Retorna el primer índice donde
 * los nombres de función difieren.
 *
 * Si los stacks son idénticos hasta donde ambos tienen frames, retorna
 * el mínimo de sus profundidades (es decir, el punto donde uno es más
 * profundo que el otro, o ambas profundidades si son iguales).
 *
 * Ejemplo visual:
 *   prev: [main, foo, bar]     (depth=3)
 *   curr: [main, foo, baz]     (depth=3)
 *   Comparación: main==main ✓, foo==foo ✓, bar!=baz ✗
 *   Resultado: divergencia en índice 2
 */
int find_divergence_point(const StackSample *prev, const StackSample *curr)
{
    /* Determinamos hasta dónde podemos comparar: el mínimo de ambas
     * profundidades, ya que no podemos comparar frames que no existen */
    int min_depth = prev->depth < curr->depth ? prev->depth : curr->depth;

    for (int i = 0; i < min_depth; i++) {
        /* Comparamos los nombres de función frame por frame.
         * En un profiler real, también compararíamos direcciones de memoria
         * o program counters, pero para nuestra simulación educativa,
         * los nombres de función son suficientes. */
        if (strcmp(prev->frames[i].function_name,
                   curr->frames[i].function_name) != 0) {
            return i;
        }
    }

    /* Si llegamos aquí, todos los frames comparados coinciden.
     * La divergencia está en min_depth (donde un stack tiene más frames
     * que el otro, o ambos terminan al mismo punto). */
    return min_depth;
}

/* ─────────────────────────────────────────────────────────────────────────────
 * add_event: Agrega un evento a la línea de tiempo
 * ─────────────────────────────────────────────────────────────────────────────
 *
 * Función auxiliar que inserta un nuevo evento (inicio o fin de función)
 * en el arreglo de eventos de la línea de tiempo.
 *
 * Verificamos que no excedamos la capacidad máxima para evitar
 * desbordamientos de buffer — ¡seguridad ante todo!
 */
void add_event(Timeline *timeline, const char *func_name, EventType type,
               double timestamp, int depth)
{
    if (timeline->event_count >= MAX_EVENTS) {
        fprintf(stderr, "⚠️  Advertencia: se alcanzó el límite máximo de eventos (%d)\n",
                MAX_EVENTS);
        return;
    }

    TimelineEvent *event = &timeline->events[timeline->event_count];
    strncpy(event->function_name, func_name, MAX_FUNCTION_NAME - 1);
    event->function_name[MAX_FUNCTION_NAME - 1] = '\0';
    event->type = type;
    event->timestamp = timestamp;
    event->depth = depth;
    timeline->event_count++;
}

/* ─────────────────────────────────────────────────────────────────────────────
 * reconstruct_timeline: El corazón del profiler
 * ─────────────────────────────────────────────────────────────────────────────
 *
 * Este es el algoritmo principal. Reconstruye la línea de tiempo de ejecución
 * comparando muestras consecutivas del stack.
 *
 * ALGORITMO:
 * ──────────
 * 1. Para la PRIMERA muestra: todos los frames son EVENT_START
 *    (asumimos que todas esas funciones acaban de iniciar)
 *
 * 2. Para cada par consecutivo (prev, curr):
 *    a) Encontrar punto de divergencia
 *    b) Frames en prev desde divergencia hasta la cima → EVENT_END
 *       (emitidos en orden inverso: la más profunda termina primero)
 *    c) Frames en curr desde divergencia hasta la cima → EVENT_START
 *       (emitidos en orden: la más superficial inicia primero)
 *
 * 3. Para la ÚLTIMA muestra: los frames restantes son EVENT_END
 *
 * ¿POR QUÉ ORDEN INVERSO PARA LOS ENDS?
 * Porque en un call stack, la función más profunda (la que está en la cima)
 * debe terminar ANTES que la función que la llamó. Es como una pila de
 * platos: el último que pusiste es el primero que quitas.
 *
 * EJEMPLO DETALLADO:
 *   prev: [main, procesar, calcular, sumar]  (t=0.0)
 *   curr: [main, procesar, ordenar]           (t=0.1)
 *
 *   Divergencia en índice 2 (calcular != ordenar)
 *
 *   ENDs (de prev, índices 3→2, inverso):
 *     EVENT_END sumar    t=0.1  depth=3
 *     EVENT_END calcular t=0.1  depth=2
 *
 *   STARTs (de curr, índices 2→2):
 *     EVENT_START ordenar t=0.1  depth=2
 */
Timeline reconstruct_timeline(const StackSample *samples, int sample_count)
{
    Timeline timeline;
    memset(&timeline, 0, sizeof(Timeline));

    /* Caso borde: sin muestras, no hay nada que reconstruir */
    if (sample_count <= 0) {
        return timeline;
    }

    /* ── PASO 1: Primera muestra ──
     * Todos los frames de la primera muestra se consideran como inicios.
     * No tenemos información previa, así que asumimos que todas estas
     * funciones comenzaron en el timestamp de la primera muestra. */
    const StackSample *first = &samples[0];
    for (int i = 0; i < first->depth; i++) {
        add_event(&timeline, first->frames[i].function_name,
                  EVENT_START, first->timestamp, i);
    }

    /* Caso especial: si solo hay una muestra, emitir también los ENDs */
    if (sample_count == 1) {
        for (int i = first->depth - 1; i >= 0; i--) {
            add_event(&timeline, first->frames[i].function_name,
                      EVENT_END, first->timestamp, i);
        }
        return timeline;
    }

    /* ── PASO 2: Comparar muestras consecutivas ──
     * Aquí es donde ocurre la magia del diffing.
     * Para cada par (prev, curr), detectamos qué funciones terminaron
     * y cuáles comenzaron. */
    for (int s = 1; s < sample_count; s++) {
        const StackSample *prev = &samples[s - 1];
        const StackSample *curr = &samples[s];

        /* Encontrar dónde los stacks divergen */
        int div_point = find_divergence_point(prev, curr);

        /* Emitir EVENT_END para funciones que terminaron en prev.
         * Recorremos desde la cima del stack (más profunda) hasta el
         * punto de divergencia, porque las funciones más profundas
         * terminan primero (LIFO — Last In, First Out). */
        for (int i = prev->depth - 1; i >= div_point; i--) {
            add_event(&timeline, prev->frames[i].function_name,
                      EVENT_END, curr->timestamp, i);
        }

        /* Emitir EVENT_START para funciones que comenzaron en curr.
         * Recorremos desde el punto de divergencia hacia la cima,
         * porque las funciones más superficiales inician primero
         * (la función padre se llama antes que la hija). */
        for (int i = div_point; i < curr->depth; i++) {
            add_event(&timeline, curr->frames[i].function_name,
                      EVENT_START, curr->timestamp, i);
        }
    }

    /* ── PASO 3: Última muestra ──
     * Las funciones que están en la última muestra aún están "activas".
     * Las cerramos todas con EVENT_END en orden inverso. */
    const StackSample *last = &samples[sample_count - 1];
    for (int i = last->depth - 1; i >= 0; i--) {
        add_event(&timeline, last->frames[i].function_name,
                  EVENT_END, last->timestamp, i);
    }

    return timeline;
}

/* ─────────────────────────────────────────────────────────────────────────────
 * print_timeline: Imprime la línea de tiempo de forma legible
 * ─────────────────────────────────────────────────────────────────────────────
 *
 * Muestra cada evento con indentación proporcional a la profundidad del
 * call stack, facilitando la visualización de la jerarquía de llamadas.
 *
 * Ejemplo de salida:
 *   [0.000s] ▶ START main()
 *   [0.000s]   ▶ START procesar()
 *   [0.000s]     ▶ START calcular()
 *   [0.100s]     ■ END   calcular()
 *   [0.100s]     ▶ START ordenar()
 *   [0.200s]     ■ END   ordenar()
 *   [0.200s]   ■ END   procesar()
 *   [0.200s] ■ END   main()
 */
void print_timeline(const Timeline *timeline)
{
    printf("\n╔══════════════════════════════════════════════════════════════╗\n");
    printf("║           LÍNEA DE TIEMPO RECONSTRUIDA                     ║\n");
    printf("╚══════════════════════════════════════════════════════════════╝\n\n");

    for (int i = 0; i < timeline->event_count; i++) {
        const TimelineEvent *event = &timeline->events[i];

        /* Imprimir timestamp con formato fijo */
        printf("[%7.3fs] ", event->timestamp);

        /* Indentación según la profundidad (2 espacios por nivel) */
        for (int d = 0; d < event->depth; d++) {
            printf("  ");
        }

        /* Símbolo y tipo de evento */
        if (event->type == EVENT_START) {
            printf("▶ START %s()\n", event->function_name);
        } else {
            printf("■ END   %s()\n", event->function_name);
        }
    }

    printf("\nTotal de eventos: %d\n", timeline->event_count);
}

/* ─────────────────────────────────────────────────────────────────────────────
 * export_chrome_tracing_json: Exporta en formato Chrome Tracing
 * ─────────────────────────────────────────────────────────────────────────────
 *
 * Chrome Tracing es un formato JSON que permite visualizar líneas de tiempo
 * en chrome://tracing. Cada evento tiene:
 *   - "name": nombre de la función
 *   - "ph": fase ("B" = begin, "E" = end)
 *   - "ts": timestamp en microsegundos
 *   - "pid": ID del proceso (usamos 1)
 *   - "tid": ID del thread (usamos 1)
 *
 * Esto genera archivos que puedes abrir directamente en Chrome para
 * obtener una visualización interactiva profesional de la ejecución.
 */
int export_chrome_tracing_json(const Timeline *timeline, const char *filename)
{
    FILE *fp = fopen(filename, "w");
    if (!fp) {
        fprintf(stderr, "Error: no se pudo abrir '%s' para escritura\n", filename);
        return -1;
    }

    fprintf(fp, "{\"traceEvents\": [\n");

    for (int i = 0; i < timeline->event_count; i++) {
        const TimelineEvent *event = &timeline->events[i];

        /* Convertir tipo de evento a fase de Chrome Tracing:
         * "B" (Begin) para EVENT_START, "E" (End) para EVENT_END */
        const char *phase = (event->type == EVENT_START) ? "B" : "E";

        /* Convertir timestamp de segundos a microsegundos (×1,000,000)
         * ya que Chrome Tracing espera microsegundos */
        long long ts_us = (long long)(event->timestamp * 1000000.0);

        fprintf(fp, "  {\"name\": \"%s\", \"ph\": \"%s\", \"ts\": %lld, "
                     "\"pid\": 1, \"tid\": 1}",
                event->function_name, phase, ts_us);

        /* Agregar coma después de cada evento excepto el último */
        if (i < timeline->event_count - 1) {
            fprintf(fp, ",");
        }
        fprintf(fp, "\n");
    }

    fprintf(fp, "]}\n");
    fclose(fp);

    printf("\n✅ Timeline exportada a '%s' (compatible con chrome://tracing)\n",
           filename);
    return 0;
}

/* ─────────────────────────────────────────────────────────────────────────────
 * Funciones auxiliares para construir muestras de demostración
 * ─────────────────────────────────────────────────────────────────────────────
 *
 * En un profiler real, estas muestras vendrían de señales del sistema
 * operativo (como SIGPROF en Linux) que interrumpen el programa a
 * intervalos regulares y capturan el call stack.
 *
 * Para esta demo educativa, construimos las muestras manualmente para
 * simular una ejecución típica de un programa.
 */

/* Agrega un frame a una muestra del stack */
static void add_frame(StackSample *sample, const char *func_name, int line)
{
    if (sample->depth >= MAX_STACK_DEPTH) return;
    strncpy(sample->frames[sample->depth].function_name, func_name,
            MAX_FUNCTION_NAME - 1);
    sample->frames[sample->depth].function_name[MAX_FUNCTION_NAME - 1] = '\0';
    sample->frames[sample->depth].line_number = line;
    sample->depth++;
}

/* ─────────────────────────────────────────────────────────────────────────────
 * PUNTO DE ENTRADA: Demostración del Sampling Profiler
 * ─────────────────────────────────────────────────────────────────────────────
 *
 * Cuando compilamos con -DTESTING, no incluimos main() aquí porque
 * el archivo de tests define su propio main().
 */
#ifndef TESTING

int main(void)
{
    printf("╔══════════════════════════════════════════════════════════════╗\n");
    printf("║  🔍 Módulo 5: El Detective de Código — Sampling Profiler   ║\n");
    printf("╚══════════════════════════════════════════════════════════════╝\n\n");

    /* ── Construir muestras simuladas ──
     *
     * Simulamos la siguiente ejecución de un programa:
     *
     * t=0.0s: main() → procesar_datos() → leer_archivo()
     * t=0.1s: main() → procesar_datos() → parsear_json()
     * t=0.2s: main() → procesar_datos() → parsear_json() → validar_campo()
     * t=0.3s: main() → procesar_datos() → transformar()
     * t=0.4s: main() → exportar_resultados() → escribir_csv()
     * t=0.5s: main() → exportar_resultados() → escribir_csv() → flush_buffer()
     *
     * Esto simula un programa que lee datos, los parsea, transforma,
     * y finalmente exporta resultados.
     */

    StackSample samples[6];
    memset(samples, 0, sizeof(samples));

    /* Muestra 0 (t=0.0s): Leyendo un archivo */
    samples[0].timestamp = 0.0;
    add_frame(&samples[0], "main", 10);
    add_frame(&samples[0], "procesar_datos", 25);
    add_frame(&samples[0], "leer_archivo", 42);

    /* Muestra 1 (t=0.1s): Parseando JSON */
    samples[1].timestamp = 0.1;
    add_frame(&samples[1], "main", 10);
    add_frame(&samples[1], "procesar_datos", 30);
    add_frame(&samples[1], "parsear_json", 55);

    /* Muestra 2 (t=0.2s): Validando un campo dentro del parseo */
    samples[2].timestamp = 0.2;
    add_frame(&samples[2], "main", 10);
    add_frame(&samples[2], "procesar_datos", 30);
    add_frame(&samples[2], "parsear_json", 60);
    add_frame(&samples[2], "validar_campo", 78);

    /* Muestra 3 (t=0.3s): Transformando datos */
    samples[3].timestamp = 0.3;
    add_frame(&samples[3], "main", 10);
    add_frame(&samples[3], "procesar_datos", 35);
    add_frame(&samples[3], "transformar", 90);

    /* Muestra 4 (t=0.4s): Exportando resultados */
    samples[4].timestamp = 0.4;
    add_frame(&samples[4], "main", 10);
    add_frame(&samples[4], "exportar_resultados", 100);
    add_frame(&samples[4], "escribir_csv", 115);

    /* Muestra 5 (t=0.5s): Haciendo flush del buffer */
    samples[5].timestamp = 0.5;
    add_frame(&samples[5], "main", 10);
    add_frame(&samples[5], "exportar_resultados", 105);
    add_frame(&samples[5], "escribir_csv", 120);
    add_frame(&samples[5], "flush_buffer", 130);

    printf("📸 Se crearon %d muestras simuladas del call stack\n", 6);
    printf("   Simulando: lectura → parseo → transformación → exportación\n\n");

    /* ── Reconstruir la línea de tiempo ── */
    printf("🔎 Reconstruyendo línea de tiempo mediante stack diffing...\n");
    Timeline timeline = reconstruct_timeline(samples, 6);

    /* ── Imprimir resultado ── */
    print_timeline(&timeline);

    /* ── Exportar como JSON para Chrome Tracing ── */
    export_chrome_tracing_json(&timeline, "trace_output.json");

    printf("\n💡 Tip: Abre chrome://tracing y carga trace_output.json para\n");
    printf("   ver una visualización interactiva de la línea de tiempo.\n\n");

    return 0;
}

#endif /* TESTING */
