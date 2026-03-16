#ifndef PROFILER_H
#define PROFILER_H

#include <stddef.h>

#define MAX_STACK_DEPTH 64
#define MAX_FUNCTION_NAME 128
#define MAX_SAMPLES 1024
#define MAX_EVENTS 2048

// Representa un frame individual del call stack
typedef struct {
    char function_name[MAX_FUNCTION_NAME];
    int line_number;
} StackFrame;

// Representa una muestra (snapshot) del call stack tomada en un momento dado
typedef struct {
    StackFrame frames[MAX_STACK_DEPTH];
    int depth;            // número de frames en esta muestra
    double timestamp;     // momento en que se tomó la muestra (segundos)
} StackSample;

// Tipo de evento de ejecución de función (inicio o fin)
typedef enum {
    EVENT_START,
    EVENT_END
} EventType;

// Representa un evento en la línea de tiempo (una función inició o terminó)
typedef struct {
    char function_name[MAX_FUNCTION_NAME];
    EventType type;
    double timestamp;
    int depth;            // profundidad en el call stack
} TimelineEvent;

// Representa la línea de tiempo reconstruida completa
typedef struct {
    TimelineEvent events[MAX_EVENTS];
    int event_count;
} Timeline;

// === Funciones Principales ===

// Encuentra el punto de divergencia entre dos muestras consecutivas del stack.
// Compara frame por frame desde la raíz (índice 0).
// Retorna el índice donde los stacks difieren por primera vez.
int find_divergence_point(const StackSample *prev, const StackSample *curr);

// Reconstruye una línea de tiempo a partir de un arreglo de muestras del stack.
// Compara muestras consecutivas para determinar eventos de inicio/fin de funciones.
Timeline reconstruct_timeline(const StackSample *samples, int sample_count);

// Agrega un evento a la línea de tiempo
void add_event(Timeline *timeline, const char *func_name, EventType type, double timestamp, int depth);

// Imprime la línea de tiempo en formato legible para humanos
void print_timeline(const Timeline *timeline);

// Exporta la línea de tiempo como JSON compatible con chrome://tracing.
// Retorna 0 en éxito, -1 en error.
int export_chrome_tracing_json(const Timeline *timeline, const char *filename);

#endif
