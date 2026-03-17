/*
 * http_server.h — Servidor HTTP/1.1 concurrente con thread pool
 * Módulo 12: The Anthropic Gauntlet
 *
 * Interfaz pública del servidor. Todo el código que use el servidor
 * solo necesita incluir este archivo.
 */

#ifndef HTTP_SERVER_H
#define HTTP_SERVER_H

#include <stddef.h>
#include <pthread.h>

/* ── Constantes de configuración ─────────────────────────────────────── */
#define HTTP_SERVER_MAX_WORKERS     64
#define HTTP_SERVER_QUEUE_CAPACITY  256
#define HTTP_SERVER_BUFFER_SIZE     8192
#define HTTP_SERVER_MAX_PATH        1024
#define HTTP_SERVER_MAX_METHOD      16
#define HTTP_SERVER_MAX_VERSION     16
#define HTTP_SERVER_BACKLOG         128

/* ── Códigos de estado HTTP soportados ───────────────────────────────── */
#define HTTP_200_OK            200
#define HTTP_400_BAD_REQUEST   400
#define HTTP_404_NOT_FOUND     404
#define HTTP_500_INTERNAL      500

/* ─────────────────────────────────────────────────────────────────────── */
/* Estructuras de datos                                                     */
/* ─────────────────────────────────────────────────────────────────────── */

/*
 * HttpRequest — Representa una petición HTTP parseada.
 * El servidor rellena esta estructura al parsear cada petición entrante.
 */
typedef struct {
    char method[HTTP_SERVER_MAX_METHOD];   /* "GET", "POST", etc. */
    char path[HTTP_SERVER_MAX_PATH];       /* "/index.html", "/api/v1/..." */
    char version[HTTP_SERVER_MAX_VERSION]; /* "HTTP/1.1" */
    int  keep_alive;                       /* 1 si el cliente pide Keep-Alive */
} HttpRequest;

/*
 * WorkItem — Una tarea pendiente en la cola del thread pool.
 * Cada conexión aceptada genera un WorkItem con el file descriptor del cliente.
 */
typedef struct WorkItem {
    int              client_fd;  /* File descriptor de la conexión TCP */
    struct WorkItem *next;       /* Puntero al siguiente elemento en la cola */
} WorkItem;

/*
 * ThreadPool — El pool de hilos worker.
 *
 * Arquitectura:
 *   ┌──────────────────────────────────────────────────────────────┐
 *   │  Thread Main                                                  │
 *   │   accept() → encola WorkItem → señaliza cond_not_empty       │
 *   └──────────────────────────────────────────────────────────────┘
 *                          │   cola (FIFO protegida por mutex)
 *   ┌──────────────────────▼───────────────────────────────────────┐
 *   │  Worker 1  Worker 2  ...  Worker N                            │
 *   │  Esperan en cond_wait hasta que haya trabajo                  │
 *   │  Desencolan → procesan HTTP request → envían respuesta        │
 *   └──────────────────────────────────────────────────────────────┘
 */
typedef struct {
    pthread_t        threads[HTTP_SERVER_MAX_WORKERS];
    int              num_workers;

    /* Cola de trabajo (FIFO enlazada) */
    WorkItem        *queue_head;
    WorkItem        *queue_tail;
    int              queue_size;

    /* Sincronización */
    pthread_mutex_t  mutex;
    pthread_cond_t   cond_not_empty;  /* Señaliza que hay trabajo disponible */
    pthread_cond_t   cond_not_full;   /* Señaliza que hay espacio en la cola  */

    /* Control de ciclo de vida */
    int              running;         /* 1 = activo, 0 = apagando */

    /* Referencia al servidor (para el handler) */
    void            *server;
} ThreadPool;

/*
 * HttpServer — El servidor HTTP completo.
 */
typedef struct {
    int         listen_fd;           /* Socket de escucha */
    int         port;
    ThreadPool  pool;
    char        www_root[HTTP_SERVER_MAX_PATH]; /* Directorio raíz de archivos */
    int         running;
} HttpServer;

/* ─────────────────────────────────────────────────────────────────────── */
/* API pública                                                               */
/* ─────────────────────────────────────────────────────────────────────── */

/*
 * http_server_init — Inicializa el servidor HTTP.
 *
 * Crea el socket de escucha, el pool de hilos y configura los parámetros.
 *
 * Parámetros:
 *   server       — Puntero a HttpServer a inicializar
 *   port         — Puerto TCP (ej: 8080)
 *   num_workers  — Número de hilos worker en el pool
 *   www_root     — Directorio raíz para servir archivos (NULL = directorio actual)
 *
 * Retorna: 0 en éxito, -1 en error (errno establecido)
 */
int http_server_init(HttpServer *server, int port, int num_workers,
                     const char *www_root);

/*
 * http_server_run — Inicia el bucle principal de aceptación de conexiones.
 *
 * Bloquea hasta que http_server_stop() es llamado desde otro hilo o señal.
 *
 * Retorna: 0 en salida normal, -1 en error
 */
int http_server_run(HttpServer *server);

/*
 * http_server_stop — Solicita el apagado graceful del servidor.
 *
 * Señaliza todos los workers para que terminen después de completar
 * sus peticiones en curso.
 */
void http_server_stop(HttpServer *server);

/*
 * http_server_destroy — Libera todos los recursos del servidor.
 *
 * Debe llamarse después de http_server_stop() cuando el servidor
 * ya no está en ejecución.
 */
void http_server_destroy(HttpServer *server);

/* ── Funciones internas (también expuestas para testing unitario) ──── */

/*
 * http_parse_request — Parsea la línea de petición HTTP.
 *
 * Parsea una cadena como "GET /index.html HTTP/1.1\r\n" en sus componentes.
 *
 * Retorna: 0 en éxito, -1 si el formato es inválido
 */
int http_parse_request(const char *raw, HttpRequest *req);

/*
 * http_get_content_type — Retorna el MIME type basado en la extensión del archivo.
 */
const char *http_get_content_type(const char *path);

/*
 * http_send_response — Envía una respuesta HTTP completa por el socket.
 *
 * Retorna: bytes enviados, -1 en error
 */
int http_send_response(int fd, int status_code, const char *content_type,
                       const char *body, size_t body_len);

/*
 * thread_pool_init — Inicializa el pool de hilos.
 * thread_pool_submit — Añade una tarea a la cola.
 * thread_pool_destroy — Espera a que terminen todos los workers y libera recursos.
 */
int  thread_pool_init(ThreadPool *pool, int num_workers, void *server);
int  thread_pool_submit(ThreadPool *pool, int client_fd);
void thread_pool_destroy(ThreadPool *pool);

#endif /* HTTP_SERVER_H */
