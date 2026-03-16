/*
 * ============================================================================
 *  Tests para el Sampling Profiler — Módulo 5
 * ============================================================================
 *
 *  Archivo de tests que verifica el correcto funcionamiento del profiler.
 *  Usa assert() para validaciones — sin dependencias externas.
 *
 *  Cada test está documentado con comentarios en español explicando
 *  qué escenario se está probando y por qué es importante.
 *
 * ============================================================================
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include "profiler.h"

/* Incluimos la implementación directamente para compilar como una sola unidad.
 * La flag -DTESTING evita que se compile el main() de profiler.c */
#include "profiler.c"

/* ── Contadores globales de tests ── */
static int tests_passed = 0;
static int tests_failed = 0;

/* Macro para reportar resultado de cada test */
#define RUN_TEST(test_func) do {                                        \
    printf("  Ejecutando: %-45s", #test_func "...");                    \
    test_func();                                                        \
    tests_passed++;                                                     \
    printf(" ✅ PASÓ\n");                                               \
} while(0)

/* ── Función auxiliar: construir un frame de stack ── */
static void set_frame(StackSample *sample, int index, const char *name, int line)
{
    strncpy(sample->frames[index].function_name, name, MAX_FUNCTION_NAME - 1);
    sample->frames[index].function_name[MAX_FUNCTION_NAME - 1] = '\0';
    sample->frames[index].line_number = line;
}

/* ── Función auxiliar: crear una muestra con frames ── */
static StackSample make_sample(double timestamp, int depth, const char *names[])
{
    StackSample s;
    memset(&s, 0, sizeof(s));
    s.timestamp = timestamp;
    s.depth = depth;
    for (int i = 0; i < depth; i++) {
        set_frame(&s, i, names[i], (i + 1) * 10);
    }
    return s;
}

/* ═══════════════════════════════════════════════════════════════════════════
 * TEST 1: Stacks idénticos → divergencia al final
 * ═══════════════════════════════════════════════════════════════════════════
 * Si dos muestras tienen exactamente los mismos frames, la divergencia
 * debería estar en el punto donde ambos stacks terminan (min_depth).
 * Esto significa que ninguna función cambió entre las dos muestras.
 */
static void test_find_divergence_identical_stacks(void)
{
    const char *names[] = {"main", "foo", "bar"};
    StackSample s1 = make_sample(0.0, 3, names);
    StackSample s2 = make_sample(0.1, 3, names);

    int div = find_divergence_point(&s1, &s2);

    /* La divergencia debe estar al final (índice 3 = profundidad completa)
     * porque todos los frames coinciden */
    assert(div == 3);
}

/* ═══════════════════════════════════════════════════════════════════════════
 * TEST 2: Stacks completamente diferentes → divergencia en 0
 * ═══════════════════════════════════════════════════════════════════════════
 * Si ni siquiera el primer frame coincide, la divergencia es en el
 * índice 0. En la práctica esto sería raro (normalmente main() está
 * siempre en la base), pero es un caso borde importante.
 */
static void test_find_divergence_completely_different(void)
{
    const char *names1[] = {"alpha", "beta", "gamma"};
    const char *names2[] = {"delta", "epsilon", "zeta"};
    StackSample s1 = make_sample(0.0, 3, names1);
    StackSample s2 = make_sample(0.1, 3, names2);

    int div = find_divergence_point(&s1, &s2);

    /* Divergencia inmediata en el primer frame */
    assert(div == 0);
}

/* ═══════════════════════════════════════════════════════════════════════════
 * TEST 3: Coincidencia parcial → divergencia en el punto correcto
 * ═══════════════════════════════════════════════════════════════════════════
 * Los stacks comparten un prefijo común (main → procesar) pero divergen
 * después. El profiler debe detectar exactamente dónde cambian.
 */
static void test_find_divergence_partial_match(void)
{
    const char *names1[] = {"main", "procesar", "calcular", "sumar"};
    const char *names2[] = {"main", "procesar", "ordenar"};
    StackSample s1 = make_sample(0.0, 4, names1);
    StackSample s2 = make_sample(0.1, 3, names2);

    int div = find_divergence_point(&s1, &s2);

    /* main y procesar coinciden, pero calcular != ordenar → divergencia en 2 */
    assert(div == 2);
}

/* ═══════════════════════════════════════════════════════════════════════════
 * TEST 4: Reconstrucción simple con 2-3 muestras
 * ═══════════════════════════════════════════════════════════════════════════
 * Caso básico: verificar que la reconstrucción genera los eventos
 * correctos para una secuencia simple de llamadas.
 *
 *   Muestra 0: [main, foo]       t=0.0
 *   Muestra 1: [main, bar]       t=1.0
 *   Muestra 2: [main, baz]       t=2.0
 *
 * Esperamos:
 *   START main   t=0.0
 *   START foo    t=0.0
 *   END   foo    t=1.0
 *   START bar    t=1.0
 *   END   bar    t=2.0
 *   START baz    t=2.0
 *   END   baz    t=2.0
 *   END   main   t=2.0
 */
static void test_reconstruct_simple_timeline(void)
{
    const char *s0_names[] = {"main", "foo"};
    const char *s1_names[] = {"main", "bar"};
    const char *s2_names[] = {"main", "baz"};

    StackSample samples[3];
    samples[0] = make_sample(0.0, 2, s0_names);
    samples[1] = make_sample(1.0, 2, s1_names);
    samples[2] = make_sample(2.0, 2, s2_names);

    Timeline tl = reconstruct_timeline(samples, 3);

    /* Verificar el número total de eventos:
     * - Primera muestra: 2 STARTs (main, foo)
     * - Diff 0→1: 1 END (foo), 1 START (bar)
     * - Diff 1→2: 1 END (bar), 1 START (baz)
     * - Última muestra: 2 ENDs (baz, main)
     * Total: 2 + 2 + 2 + 2 = 8 */
    assert(tl.event_count == 8);

    /* Verificar primer evento: START main */
    assert(tl.events[0].type == EVENT_START);
    assert(strcmp(tl.events[0].function_name, "main") == 0);

    /* Verificar segundo evento: START foo */
    assert(tl.events[1].type == EVENT_START);
    assert(strcmp(tl.events[1].function_name, "foo") == 0);

    /* Verificar que foo termina antes de que bar comience */
    assert(tl.events[2].type == EVENT_END);
    assert(strcmp(tl.events[2].function_name, "foo") == 0);
    assert(tl.events[3].type == EVENT_START);
    assert(strcmp(tl.events[3].function_name, "bar") == 0);

    /* Verificar último evento: END main */
    assert(tl.events[tl.event_count - 1].type == EVENT_END);
    assert(strcmp(tl.events[tl.event_count - 1].function_name, "main") == 0);
}

/* ═══════════════════════════════════════════════════════════════════════════
 * TEST 5: Reconstrucción compleja con llamadas anidadas
 * ═══════════════════════════════════════════════════════════════════════════
 * Caso más complejo donde las funciones se anidan a diferentes
 * profundidades, simulando una ejecución realista con funciones
 * que llaman a subfunciones.
 *
 *   Muestra 0: [main, A, B]        t=0.0
 *   Muestra 1: [main, A, B, C]     t=1.0  (C se añadió dentro de B)
 *   Muestra 2: [main, A]           t=2.0  (B y C terminaron)
 *   Muestra 3: [main, D]           t=3.0  (A terminó, D comenzó)
 */
static void test_reconstruct_complex_timeline(void)
{
    const char *s0[] = {"main", "A", "B"};
    const char *s1[] = {"main", "A", "B", "C"};
    const char *s2[] = {"main", "A"};
    const char *s3[] = {"main", "D"};

    StackSample samples[4];
    samples[0] = make_sample(0.0, 3, s0);
    samples[1] = make_sample(1.0, 4, s1);
    samples[2] = make_sample(2.0, 2, s2);
    samples[3] = make_sample(3.0, 2, s3);

    Timeline tl = reconstruct_timeline(samples, 4);

    /* Verificar que tenemos eventos razonables */
    assert(tl.event_count > 0);

    /* Verificar que el primer evento es START main */
    assert(tl.events[0].type == EVENT_START);
    assert(strcmp(tl.events[0].function_name, "main") == 0);
    assert(tl.events[0].depth == 0);

    /* Verificar que el último evento es END main */
    assert(tl.events[tl.event_count - 1].type == EVENT_END);
    assert(strcmp(tl.events[tl.event_count - 1].function_name, "main") == 0);
    assert(tl.events[tl.event_count - 1].depth == 0);

    /* Verificar que C aparece como START en algún momento
     * (fue detectado entre muestra 0 y 1) */
    int found_c_start = 0;
    for (int i = 0; i < tl.event_count; i++) {
        if (tl.events[i].type == EVENT_START &&
            strcmp(tl.events[i].function_name, "C") == 0) {
            found_c_start = 1;
            assert(tl.events[i].depth == 3);
            break;
        }
    }
    assert(found_c_start);

    /* Verificar que D aparece como START */
    int found_d_start = 0;
    for (int i = 0; i < tl.event_count; i++) {
        if (tl.events[i].type == EVENT_START &&
            strcmp(tl.events[i].function_name, "D") == 0) {
            found_d_start = 1;
            break;
        }
    }
    assert(found_d_start);
}

/* ═══════════════════════════════════════════════════════════════════════════
 * TEST 6: Caso borde — sin muestras
 * ═══════════════════════════════════════════════════════════════════════════
 * Si no hay muestras, la línea de tiempo debe estar vacía.
 * Esto verifica que el profiler maneja correctamente entradas vacías
 * sin crashear.
 */
static void test_empty_samples(void)
{
    Timeline tl = reconstruct_timeline(NULL, 0);
    assert(tl.event_count == 0);
}

/* ═══════════════════════════════════════════════════════════════════════════
 * TEST 7: Caso borde — una sola muestra
 * ═══════════════════════════════════════════════════════════════════════════
 * Con una sola muestra, solo podemos generar STARTs y ENDs inmediatos.
 * No hay pares consecutivos para hacer diffing, así que cada función
 * se marca como iniciada y terminada en el mismo timestamp.
 */
static void test_single_sample(void)
{
    const char *names[] = {"main", "init", "setup"};
    StackSample sample = make_sample(5.0, 3, names);

    Timeline tl = reconstruct_timeline(&sample, 1);

    /* 3 STARTs + 3 ENDs = 6 eventos */
    assert(tl.event_count == 6);

    /* Los primeros 3 deben ser STARTs */
    assert(tl.events[0].type == EVENT_START);
    assert(tl.events[1].type == EVENT_START);
    assert(tl.events[2].type == EVENT_START);

    /* Los últimos 3 deben ser ENDs (en orden inverso) */
    assert(tl.events[3].type == EVENT_END);
    assert(strcmp(tl.events[3].function_name, "setup") == 0);
    assert(tl.events[4].type == EVENT_END);
    assert(strcmp(tl.events[4].function_name, "init") == 0);
    assert(tl.events[5].type == EVENT_END);
    assert(strcmp(tl.events[5].function_name, "main") == 0);
}

/* ═══════════════════════════════════════════════════════════════════════════
 * TEST 8: Orden cronológico de eventos
 * ═══════════════════════════════════════════════════════════════════════════
 * Verifica que los timestamps de los eventos están en orden no decreciente.
 * Esto es crucial para que las visualizaciones (como Chrome Tracing)
 * funcionen correctamente.
 */
static void test_event_ordering(void)
{
    const char *s0[] = {"main", "alpha"};
    const char *s1[] = {"main", "beta"};
    const char *s2[] = {"main", "gamma"};

    StackSample samples[3];
    samples[0] = make_sample(0.0, 2, s0);
    samples[1] = make_sample(1.0, 2, s1);
    samples[2] = make_sample(2.0, 2, s2);

    Timeline tl = reconstruct_timeline(samples, 3);

    /* Verificar que cada evento tiene un timestamp >= al anterior */
    for (int i = 1; i < tl.event_count; i++) {
        assert(tl.events[i].timestamp >= tl.events[i - 1].timestamp);
    }
}

/* ═══════════════════════════════════════════════════════════════════════════
 * TEST 9: Exportación a Chrome Tracing JSON
 * ═══════════════════════════════════════════════════════════════════════════
 * Verifica que la función de exportación crea un archivo JSON válido.
 * Comprueba que el archivo existe y contiene las claves esperadas.
 */
static void test_chrome_tracing_export(void)
{
    const char *s0[] = {"main", "work"};
    const char *s1[] = {"main", "done"};

    StackSample samples[2];
    samples[0] = make_sample(0.0, 2, s0);
    samples[1] = make_sample(1.0, 2, s1);

    Timeline tl = reconstruct_timeline(samples, 2);

    const char *test_file = "test_trace_output.json";
    int result = export_chrome_tracing_json(&tl, test_file);

    /* Verificar que la exportación fue exitosa */
    assert(result == 0);

    /* Verificar que el archivo fue creado y tiene contenido */
    FILE *fp = fopen(test_file, "r");
    assert(fp != NULL);

    /* Leer el contenido y verificar estructura básica del JSON */
    char buffer[4096];
    size_t bytes_read = fread(buffer, 1, sizeof(buffer) - 1, fp);
    buffer[bytes_read] = '\0';
    fclose(fp);

    /* Verificar que contiene las claves esperadas de Chrome Tracing */
    assert(strstr(buffer, "traceEvents") != NULL);
    assert(strstr(buffer, "\"ph\"") != NULL);
    assert(strstr(buffer, "\"ts\"") != NULL);
    assert(strstr(buffer, "\"pid\"") != NULL);
    assert(strstr(buffer, "\"tid\"") != NULL);
    assert(strstr(buffer, "\"B\"") != NULL);  /* Begin events */
    assert(strstr(buffer, "\"E\"") != NULL);  /* End events */

    /* Limpiar archivo de test */
    remove(test_file);
}

/* ═══════════════════════════════════════════════════════════════════════════
 * PUNTO DE ENTRADA: Ejecutar todos los tests
 * ═══════════════════════════════════════════════════════════════════════════ */
int main(void)
{
    printf("\n╔══════════════════════════════════════════════════════════════╗\n");
    printf("║  🧪 Tests del Sampling Profiler — Módulo 5                  ║\n");
    printf("╚══════════════════════════════════════════════════════════════╝\n\n");

    RUN_TEST(test_find_divergence_identical_stacks);
    RUN_TEST(test_find_divergence_completely_different);
    RUN_TEST(test_find_divergence_partial_match);
    RUN_TEST(test_reconstruct_simple_timeline);
    RUN_TEST(test_reconstruct_complex_timeline);
    RUN_TEST(test_empty_samples);
    RUN_TEST(test_single_sample);
    RUN_TEST(test_event_ordering);
    RUN_TEST(test_chrome_tracing_export);

    printf("\n══════════════════════════════════════════════════════════════\n");
    printf("  Resultado: %d tests pasaron, %d tests fallaron\n",
           tests_passed, tests_failed);
    printf("══════════════════════════════════════════════════════════════\n");

    if (tests_failed > 0) {
        printf("  ❌ ALGUNOS TESTS FALLARON\n\n");
        return 1;
    }

    printf("  ✅ TODOS LOS TESTS PASARON\n\n");
    return 0;
}
