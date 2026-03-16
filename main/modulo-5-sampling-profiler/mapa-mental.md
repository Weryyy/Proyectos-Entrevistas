# 🔬 Mapa Mental — Sampling Profiler & Stack Analysis

## ⏱ Tiempo estimado: 12–18 horas

```
                     ╔═══════════════════════════╗
                     ║   SAMPLING  PROFILER  &   ║
                     ║    STACK  ANALYSIS        ║
                     ╚════════════╤══════════════╝
                                  │
       ┌──────────────┬───────────┼───────────┬────────────────┐
       ▼              ▼           ▼           ▼                ▼
 ┌───────────┐ ┌────────────┐ ┌────────┐ ┌──────────┐  ┌────────────┐
 │PREREQUISI-│ │ CONCEPTOS  │ │  RUTA  │ │ RECURSOS │  │ SIGUIENTES │
 │   TOS     │ │   CLAVE    │ │  DE    │ │          │  │   PASOS    │
 └─────┬─────┘ └─────┬──────┘ │ESTUDIO │ └────┬─────┘  └─────┬──────┘
       │              │        └───┬────┘      │              │
       ▼              ▼            ▼           ▼              ▼
```

---

## 📋 Prerequisitos

```
  Prerequisitos
  ├── Lenguaje C
  │   ├── Punteros y memoria
  │   ├── Structs
  │   └── Compilación (gcc, Makefile)
  ├── Conceptos de Call Stack
  │   ├── Qué es la pila de llamadas
  │   ├── Push / Pop de frames
  │   └── Return address y base pointer
  └── Memoria y Sistema Operativo
      ├── Stack vs Heap
      ├── Registros del CPU (RSP, RBP, RIP)
      └── Señales POSIX (SIGPROF, SIGALRM)
```

## 🔑 Conceptos Clave

```
  Conceptos Clave
  ├── Call Stack (pila de llamadas)
  │   ├── Secuencia de funciones activas
  │   ├── LIFO: la última llamada está arriba
  │   └── Cada función tiene un "frame"
  ├── Stack Frames
  │   ├── Variables locales
  │   ├── Dirección de retorno
  │   ├── Base pointer (RBP)
  │   └── Argumentos de la función
  ├── Sampling (muestreo)
  │   ├── Capturar el stack trace periódicamente
  │   ├── Frecuencia: ~100-1000 Hz
  │   ├── Bajo overhead vs instrumentación
  │   └── Estadísticamente representativo
  ├── Diffing (comparación)
  │   ├── Comparar dos perfiles (antes/después)
  │   ├── Identificar regresiones de rendimiento
  │   └── Delta de tiempo por función
  ├── Chrome Tracing Format
  │   ├── JSON con eventos tipo B/E (Begin/End)
  │   ├── Visualizable en chrome://tracing
  │   └── Campos: name, cat, ph, ts, pid, tid
  └── Flame Graphs
      ├── Visualización de call stacks apilados
      ├── Ancho = tiempo en esa función
      └── Lectura: de abajo (raíz) hacia arriba
```

## 🗺 Ruta de Estudio

```
  ① Call Stack — entender la base
  │   ├── → Qué sucede al llamar una función en C
  │   └── → Dibujar el stack frame manualmente
  │
  ② Stack Frames — estructura interna
  │   ├── → Examinar con GDB: info frame, backtrace
  │   └── → Entender RBP, RSP, dirección de retorno
  │
  ③ Sampling — captura periódica
  │   ├── → Usar señales (SIGPROF / setitimer)
  │   ├── → Recorrer el stack con backtrace()
  │   └── → Almacenar muestras en estructura de datos
  │
  ④ Diffing — comparar perfiles
  │   ├── → Construir histograma de funciones
  │   └── → Calcular deltas entre dos ejecuciones
  │
  ⑤ Visualización
      ├── → Generar JSON en Chrome Tracing Format
      ├── → Abrir en chrome://tracing o Perfetto
      └── → Generar flame graphs con herramientas
```

## 📚 Recursos

```
  Recursos
  ├── Brendan Gregg — "Flame Graphs" (brendangregg.com)
  ├── Google — Chrome Trace Event Format (docs)
  ├── man backtrace(3) — documentación Linux
  ├── GDB manual — inspección de stack frames
  └── Perfetto UI — ui.perfetto.dev (visualizador)
```

## 🚀 Siguientes Pasos

```
  Después de dominar Sampling Profiler →
  ├── perf (Linux profiler nativo)
  │   ├── perf record / perf report
  │   └── Hardware performance counters
  ├── Valgrind
  │   ├── Callgrind (profiling de instrucciones)
  │   └── Massif (profiling de memoria)
  ├── dtrace (profiling dinámico)
  ├── Flame Graphs avanzados (Brendan Gregg)
  │   ├── Off-CPU flame graphs
  │   └── Differential flame graphs
  └── eBPF (Extended Berkeley Packet Filter)
      ├── bpftrace
      └── BCC tools
```

---

> **💡 Consejo:** Un profiler por muestreo es como tomar fotos del call stack
> cada milisegundo. Si una función aparece en muchas fotos, es donde tu
> programa pasa más tiempo. Simple pero poderoso.
