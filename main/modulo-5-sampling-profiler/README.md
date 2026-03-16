# Módulo 5: El Detective de Código — Sampling Profiler

## 🧠 Concepto Técnico

Un **Sampling Profiler** es una herramienta que reconstruye la línea de tiempo de ejecución de un programa
tomando "muestras" (snapshots) periódicas del **call stack**. En lugar de instrumentar cada función
(lo cual añade overhead significativo), el profiler simplemente observa qué funciones están activas
en momentos regulares.

### ¿Cómo funciona el Stack Sampling?

El concepto clave es el **diffing de muestras consecutivas**: comparamos dos snapshots del call stack
desde la raíz (root) hacia arriba. Donde los stacks divergen, sabemos que las funciones anteriores
terminaron y nuevas funciones comenzaron.

```
Muestra 1 (t=0.0s)          Muestra 2 (t=0.1s)          Muestra 3 (t=0.2s)
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│ [0] main()      │ ══════  │ [0] main()      │ ══════  │ [0] main()      │
│ [1] procesar()  │ ══════  │ [1] procesar()  │         │ [1] exportar()  │
│ [2] calcular()  │         │ [2] ordenar()   │         │ [2] escribir()  │
│ [3] sumar()     │         │ [3] quicksort() │         │                 │
└─────────────────┘         └─────────────────┘         └─────────────────┘

Diff 1→2:                    Diff 2→3:
═══ Coinciden hasta [1]      ═══ Coinciden hasta [0]
✖ calcular() TERMINÓ         ✖ procesar() TERMINÓ
✖ sumar() TERMINÓ            ✖ ordenar() TERMINÓ
✚ ordenar() INICIÓ           ✖ quicksort() TERMINÓ
✚ quicksort() INICIÓ         ✚ exportar() INICIÓ
                              ✚ escribir() INICIÓ
```

### Algoritmo de Reconstrucción

```
Para cada par de muestras consecutivas (prev, curr):

  1. ENCONTRAR DIVERGENCIA:
     Comparar frame por frame desde la raíz (índice 0)
     hasta encontrar la primera diferencia → divergence_point

  2. EMITIR FINALES (EVENT_END):
     Todas las funciones en prev desde divergence_point hasta la cima
     terminaron → emitir EVENT_END en orden inverso (más profunda primero)

  3. EMITIR INICIOS (EVENT_START):
     Todas las funciones en curr desde divergence_point hasta la cima
     comenzaron → emitir EVENT_START en orden (más superficial primero)

Casos especiales:
  - Primera muestra: todos los frames son EVENT_START
  - Última muestra: todos los frames restantes son EVENT_END
```

### Línea de Tiempo Reconstruida

```
Tiempo →  0.0s          0.1s          0.2s          0.3s
          ├──────────────┼──────────────┼──────────────┤
main()    ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
procesar()  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓│
calcular()    ▓▓▓▓▓▓▓▓▓▓▓▓│             │
sumar()         ▓▓▓▓▓▓▓▓▓▓│             │
ordenar()                  ▓▓▓▓▓▓▓▓▓▓▓▓▓│
quicksort()                  ▓▓▓▓▓▓▓▓▓▓▓│
exportar()                               ▓▓▓▓▓▓▓▓▓▓▓▓
escribir()                                 ▓▓▓▓▓▓▓▓▓▓▓
```

### 📊 Tabla de Complejidad

| Operación                | Complejidad  | Descripción                                      |
|--------------------------|-------------|--------------------------------------------------|
| Encontrar divergencia    | O(d)        | d = profundidad máxima del stack                  |
| Reconstruir timeline     | O(n × d)    | n = número de muestras, d = profundidad máxima   |
| Exportar JSON            | O(e)        | e = número de eventos en la timeline              |

## 🚀 Lore: El Detective de Código

Eres un **detective de código** investigando crímenes de rendimiento. Tu sospechoso: un programa
que tarda demasiado en ejecutarse. ¿Pero qué función es la culpable?

No puedes seguir al sospechoso las 24 horas (eso sería instrumentación completa y ralentizaría
todo). En cambio, instalas **cámaras de seguridad** que toman fotos a intervalos regulares.

Cada foto captura quién está en la "escena del crimen" (el call stack): qué funciones están
activas en ese instante. Al comparar fotos consecutivas, puedes reconstruir la línea temporal:

> *"A las 0.0s, `main()` llamó a `procesar()`, que llamó a `calcular()`...*
> *A las 0.1s, `calcular()` ya terminó y ahora `procesar()` está en `ordenar()`...*
> *¡Ajá! `quicksort()` aparece en 15 de 20 fotos — ¡es el culpable del 75% del tiempo!"*

Este es exactamente cómo funcionan profilers reales como `perf` en Linux o el sampling profiler
de Chrome DevTools. La belleza es que el **overhead es mínimo**: solo tomas fotos, no modificas
el programa.

## ▶️ Cómo Compilar y Ejecutar

### Requisitos
- GCC con soporte para C17 (gcc 8+)
- Make

### Compilar todo
```bash
cd main/modulo-5-sampling-profiler/codigo/c/
make all
```

### Ejecutar la demo
```bash
make run
```

Esto ejecutará una simulación que:
1. Crea muestras de stack simuladas representando la ejecución de un programa
2. Reconstruye la línea de tiempo usando el algoritmo de diffing
3. Imprime la línea de tiempo en formato legible
4. Exporta un archivo JSON compatible con `chrome://tracing`

### Ejecutar los tests
```bash
make test
```

### Visualizar el resultado
Después de ejecutar la demo, se genera `trace_output.json`. Puedes visualizarlo:
1. Abre Chrome/Chromium
2. Navega a `chrome://tracing`
3. Carga el archivo `trace_output.json`
4. ¡Explora la línea de tiempo interactiva!

### Limpiar archivos compilados
```bash
make clean
```
