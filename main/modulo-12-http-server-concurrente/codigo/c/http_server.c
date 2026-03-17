/*
 * http_server.c — Servidor HTTP/1.1 concurrente con thread pool
 * Módulo 12: The Anthropic Gauntlet
 *
 * Implementación completa del servidor. Solo usa la API POSIX estándar:
 *   - Sockets:   socket, bind, listen, accept, send, recv, close
 *   - Hilos:     pthread_create, pthread_join, pthread_mutex_*, pthread_cond_*
 *   - Archivos:  open, read, stat (para servir archivos estáticos)
 *
 * Arquitectura:
 *   hilo_principal:  accept() → encolar fd → señal cond_not_empty
 *   hilo_worker[i]:  esperar cond → desencolar fd → parsear HTTP → responder
 */

#define _GNU_SOURCE

#include "http_server.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>
#include <errno.h>
#include <time.h>

/* Sockets */
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>

/* Archivos */
#include <sys/stat.h>
#include <fcntl.h>

/* ─────────────────────────────────────────────────────────────────────── */
/* Tabla de tipos MIME                                                       */
/* ─────────────────────────────────────────────────────────────────────── */

typedef struct { const char *ext; const char *mime; } MimeEntry;

static const MimeEntry MIME_TABLE[] = {
    {".html", "text/html; charset=utf-8"},
    {".htm",  "text/html; charset=utf-8"},
    {".css",  "text/css"},
    {".js",   "application/javascript"},
    {".json", "application/json"},
    {".png",  "image/png"},
    {".jpg",  "image/jpeg"},
    {".jpeg", "image/jpeg"},
    {".gif",  "image/gif"},
    {".ico",  "image/x-icon"},
    {".txt",  "text/plain; charset=utf-8"},
    {".md",   "text/plain; charset=utf-8"},
    {NULL,    NULL},
};

const char *http_get_content_type(const char *path)
{
    const char *dot = strrchr(path, '.');
    if (dot) {
        for (int i = 0; MIME_TABLE[i].ext; i++) {
            if (strcasecmp(dot, MIME_TABLE[i].ext) == 0)
                return MIME_TABLE[i].mime;
        }
    }
    return "application/octet-stream";
}

/* ─────────────────────────────────────────────────────────────────────── */
/* Parser HTTP                                                               */
/* ─────────────────────────────────────────────────────────────────────── */

/*
 * Parsea la primera línea de la petición HTTP:
 *   "GET /ruta HTTP/1.1\r\n"
 *
 * También detecta la cabecera "Connection: keep-alive".
 */
int http_parse_request(const char *raw, HttpRequest *req)
{
    if (!raw || !req) return -1;
    memset(req, 0, sizeof(*req));

    /* Parsear línea de petición */
    int n = sscanf(raw, "%15s %1023s %15s",
                   req->method, req->path, req->version);
    if (n != 3) return -1;

    /* Detectar keep-alive */
    const char *ka = strcasestr(raw, "Connection:");
    if (ka) {
        req->keep_alive = (strcasestr(ka, "keep-alive") != NULL) ? 1 : 0;
    }
    /* HTTP/1.1 tiene keep-alive por defecto */
    if (strcmp(req->version, "HTTP/1.1") == 0 && ka == NULL)
        req->keep_alive = 1;

    return 0;
}

/* ─────────────────────────────────────────────────────────────────────── */
/* Respuestas HTTP                                                           */
/* ─────────────────────────────────────────────────────────────────────── */

static const char *status_text(int code)
{
    switch (code) {
        case 200: return "OK";
        case 400: return "Bad Request";
        case 404: return "Not Found";
        case 500: return "Internal Server Error";
        default:  return "Unknown";
    }
}

/*
 * Construye y envía una respuesta HTTP completa:
 *
 *   HTTP/1.1 <status_code> <status_text>\r\n
 *   Content-Type: <content_type>\r\n
 *   Content-Length: <body_len>\r\n
 *   Connection: close\r\n
 *   \r\n
 *   <body>
 */
int http_send_response(int fd, int status_code, const char *content_type,
                       const char *body, size_t body_len)
{
    char header[HTTP_SERVER_BUFFER_SIZE];
    int hlen = snprintf(header, sizeof(header),
        "HTTP/1.1 %d %s\r\n"
        "Content-Type: %s\r\n"
        "Content-Length: %zu\r\n"
        "Connection: close\r\n"
        "\r\n",
        status_code, status_text(status_code),
        content_type ? content_type : "text/plain",
        body_len);

    if (hlen < 0 || hlen >= (int)sizeof(header)) return -1;

    /* Enviar cabeceras */
    if (send(fd, header, hlen, MSG_NOSIGNAL) < 0) return -1;

    /* Enviar cuerpo (puede ser NULL) */
    if (body && body_len > 0) {
        if (send(fd, body, body_len, MSG_NOSIGNAL) < 0) return -1;
    }

    return hlen + (int)body_len;
}

/* ─────────────────────────────────────────────────────────────────────── */
/* Handler de peticiones HTTP                                                */
/* ─────────────────────────────────────────────────────────────────────── */

static void handle_client(HttpServer *server, int client_fd)
{
    char buf[HTTP_SERVER_BUFFER_SIZE];
    ssize_t nread = recv(client_fd, buf, sizeof(buf) - 1, 0);
    if (nread <= 0) {
        close(client_fd);
        return;
    }
    buf[nread] = '\0';

    /* Parsear petición */
    HttpRequest req;
    if (http_parse_request(buf, &req) < 0) {
        static const char err[] = "Bad Request";
        http_send_response(client_fd, HTTP_400_BAD_REQUEST,
                           "text/plain", err, sizeof(err) - 1);
        close(client_fd);
        return;
    }

    /* Log */
    fprintf(stderr, "[%s] %s %s\n",
            server->running ? "INFO" : "STOP", req.method, req.path);

    /* Solo soportamos GET */
    if (strcmp(req.method, "GET") != 0) {
        static const char err[] = "Method Not Allowed";
        http_send_response(client_fd, 405, "text/plain", err, sizeof(err) - 1);
        close(client_fd);
        return;
    }

    /* Construir ruta del archivo */
    char filepath[HTTP_SERVER_MAX_PATH * 2];
    const char *root = server->www_root[0] ? server->www_root : ".";

    /* Seguridad básica: rechazar rutas con ".." */
    if (strstr(req.path, "..")) {
        static const char err[] = "Forbidden";
        http_send_response(client_fd, 403, "text/plain", err, sizeof(err) - 1);
        close(client_fd);
        return;
    }

    /* Ruta "/" → index.html */
    if (strcmp(req.path, "/") == 0)
        snprintf(filepath, sizeof(filepath), "%s/index.html", root);
    else
        snprintf(filepath, sizeof(filepath), "%s%s", root, req.path);

    /* Intentar abrir el archivo */
    int file_fd = open(filepath, O_RDONLY);
    if (file_fd < 0) {
        static const char err[] =
            "<html><body><h1>404 Not Found</h1></body></html>";
        http_send_response(client_fd, HTTP_404_NOT_FOUND,
                           "text/html", err, sizeof(err) - 1);
        close(client_fd);
        return;
    }

    /* Obtener tamaño del archivo */
    struct stat st;
    if (fstat(file_fd, &st) < 0 || !S_ISREG(st.st_mode)) {
        close(file_fd);
        static const char err[] = "Internal Server Error";
        http_send_response(client_fd, HTTP_500_INTERNAL,
                           "text/plain", err, sizeof(err) - 1);
        close(client_fd);
        return;
    }

    /* Enviar cabeceras */
    const char *mime = http_get_content_type(filepath);
    char header[HTTP_SERVER_BUFFER_SIZE];
    int hlen = snprintf(header, sizeof(header),
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: %s\r\n"
        "Content-Length: %lld\r\n"
        "Connection: close\r\n"
        "\r\n",
        mime, (long long)st.st_size);
    send(client_fd, header, hlen, MSG_NOSIGNAL);

    /* Enviar cuerpo del archivo en chunks */
    char chunk[4096];
    ssize_t bytes;
    while ((bytes = read(file_fd, chunk, sizeof(chunk))) > 0)
        send(client_fd, chunk, bytes, MSG_NOSIGNAL);

    close(file_fd);
    close(client_fd);
}

/* ─────────────────────────────────────────────────────────────────────── */
/* Thread Pool                                                               */
/* ─────────────────────────────────────────────────────────────────────── */

/*
 * Función principal de cada hilo worker.
 *
 * El worker espera en una variable de condición hasta que haya trabajo
 * en la cola. Cuando lo hay, lo desencola y procesa la petición HTTP.
 */
static void *worker_thread(void *arg)
{
    ThreadPool *pool = (ThreadPool *)arg;
    HttpServer *server = (HttpServer *)pool->server;

    for (;;) {
        pthread_mutex_lock(&pool->mutex);

        /* Esperar mientras la cola esté vacía y el servidor esté corriendo */
        while (pool->queue_size == 0 && pool->running)
            pthread_cond_wait(&pool->cond_not_empty, &pool->mutex);

        /* Verificar señal de apagado */
        if (!pool->running && pool->queue_size == 0) {
            pthread_mutex_unlock(&pool->mutex);
            return NULL;
        }

        /* Desencolar tarea (FIFO: sacar del head) */
        WorkItem *item = pool->queue_head;
        pool->queue_head = item->next;
        if (pool->queue_head == NULL)
            pool->queue_tail = NULL;
        pool->queue_size--;

        pthread_cond_signal(&pool->cond_not_full);
        pthread_mutex_unlock(&pool->mutex);

        /* Procesar la petición HTTP fuera del mutex */
        handle_client(server, item->client_fd);
        free(item);
    }
}

int thread_pool_init(ThreadPool *pool, int num_workers, void *server)
{
    if (num_workers <= 0 || num_workers > HTTP_SERVER_MAX_WORKERS)
        return -1;

    memset(pool, 0, sizeof(*pool));
    pool->num_workers = num_workers;
    pool->server = server;
    pool->running = 1;

    if (pthread_mutex_init(&pool->mutex, NULL) != 0) return -1;
    if (pthread_cond_init(&pool->cond_not_empty, NULL) != 0) return -1;
    if (pthread_cond_init(&pool->cond_not_full,  NULL) != 0) return -1;

    for (int i = 0; i < num_workers; i++) {
        if (pthread_create(&pool->threads[i], NULL, worker_thread, pool) != 0) {
            pool->running = 0;
            return -1;
        }
    }
    return 0;
}

/*
 * Añade un file descriptor de cliente a la cola de trabajo.
 * Bloquea si la cola está llena (back-pressure).
 */
int thread_pool_submit(ThreadPool *pool, int client_fd)
{
    WorkItem *item = malloc(sizeof(*item));
    if (!item) return -1;
    item->client_fd = client_fd;
    item->next = NULL;

    pthread_mutex_lock(&pool->mutex);

    /* Esperar si la cola está llena */
    while (pool->queue_size >= HTTP_SERVER_QUEUE_CAPACITY && pool->running)
        pthread_cond_wait(&pool->cond_not_full, &pool->mutex);

    if (!pool->running) {
        pthread_mutex_unlock(&pool->mutex);
        free(item);
        close(client_fd);
        return -1;
    }

    /* Encolar al final (FIFO) */
    if (pool->queue_tail)
        pool->queue_tail->next = item;
    else
        pool->queue_head = item;
    pool->queue_tail = item;
    pool->queue_size++;

    pthread_cond_signal(&pool->cond_not_empty);
    pthread_mutex_unlock(&pool->mutex);
    return 0;
}

void thread_pool_destroy(ThreadPool *pool)
{
    pthread_mutex_lock(&pool->mutex);
    pool->running = 0;
    pthread_cond_broadcast(&pool->cond_not_empty);
    pthread_mutex_unlock(&pool->mutex);

    for (int i = 0; i < pool->num_workers; i++)
        pthread_join(pool->threads[i], NULL);

    /* Liberar ítems pendientes en la cola */
    WorkItem *item = pool->queue_head;
    while (item) {
        WorkItem *next = item->next;
        close(item->client_fd);
        free(item);
        item = next;
    }

    pthread_mutex_destroy(&pool->mutex);
    pthread_cond_destroy(&pool->cond_not_empty);
    pthread_cond_destroy(&pool->cond_not_full);
}

/* ─────────────────────────────────────────────────────────────────────── */
/* HttpServer: init / run / stop / destroy                                   */
/* ─────────────────────────────────────────────────────────────────────── */

int http_server_init(HttpServer *server, int port, int num_workers,
                     const char *www_root)
{
    memset(server, 0, sizeof(*server));
    server->port = port;
    server->running = 1;

    if (www_root)
        strncpy(server->www_root, www_root, sizeof(server->www_root) - 1);

    /* Crear socket TCP */
    server->listen_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server->listen_fd < 0) return -1;

    /* Reutilizar el puerto inmediatamente después de reiniciar */
    int opt = 1;
    setsockopt(server->listen_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    /* Bind al puerto */
    struct sockaddr_in addr = {0};
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = INADDR_ANY;
    addr.sin_port = htons((uint16_t)port);

    if (bind(server->listen_fd, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
        close(server->listen_fd);
        return -1;
    }

    if (listen(server->listen_fd, HTTP_SERVER_BACKLOG) < 0) {
        close(server->listen_fd);
        return -1;
    }

    /* Inicializar el pool de hilos */
    if (thread_pool_init(&server->pool, num_workers, server) < 0) {
        close(server->listen_fd);
        return -1;
    }

    fprintf(stderr, "[INFO] Servidor iniciado en http://0.0.0.0:%d (workers=%d)\n",
            port, num_workers);
    return 0;
}

int http_server_run(HttpServer *server)
{
    struct sockaddr_in client_addr;
    socklen_t addr_len = sizeof(client_addr);

    while (server->running) {
        int client_fd = accept(server->listen_fd,
                               (struct sockaddr *)&client_addr, &addr_len);
        if (client_fd < 0) {
            if (!server->running) break;  /* Apagado normal */
            if (errno == EINTR) continue;
            perror("accept");
            continue;
        }

        /* Encolar la conexión en el thread pool */
        if (thread_pool_submit(&server->pool, client_fd) < 0) {
            /* Cola llena o servidor apagando */
            static const char busy[] = "HTTP/1.1 503 Service Unavailable\r\n\r\n";
            send(client_fd, busy, sizeof(busy) - 1, MSG_NOSIGNAL);
            close(client_fd);
        }
    }
    return 0;
}

void http_server_stop(HttpServer *server)
{
    server->running = 0;
    /* Interrumpir el accept() cerrando el socket de escucha */
    shutdown(server->listen_fd, SHUT_RDWR);
    close(server->listen_fd);
    server->listen_fd = -1;
}

void http_server_destroy(HttpServer *server)
{
    thread_pool_destroy(&server->pool);
    if (server->listen_fd >= 0) {
        close(server->listen_fd);
        server->listen_fd = -1;
    }
    fprintf(stderr, "[INFO] Servidor detenido.\n");
}

/* ─────────────────────────────────────────────────────────────────────── */
/* main — Punto de entrada cuando se compila como ejecutable                 */
/* ─────────────────────────────────────────────────────────────────────── */

#ifndef HTTP_SERVER_LIBRARY_MODE

#include <signal.h>

static HttpServer g_server;

static void sighandler(int sig)
{
    (void)sig;
    fprintf(stderr, "\n[INFO] Señal recibida, apagando...\n");
    http_server_stop(&g_server);
}

int main(int argc, char *argv[])
{
    int port = 8080;
    int workers = 4;
    const char *www_root = ".";

    if (argc >= 2) port    = atoi(argv[1]);
    if (argc >= 3) workers = atoi(argv[2]);
    if (argc >= 4) www_root = argv[3];

    signal(SIGINT,  sighandler);
    signal(SIGTERM, sighandler);
    signal(SIGPIPE, SIG_IGN);   /* Ignorar broken pipe al escribir al cliente */

    if (http_server_init(&g_server, port, workers, www_root) < 0) {
        perror("http_server_init");
        return 1;
    }

    http_server_run(&g_server);
    http_server_destroy(&g_server);
    return 0;
}

#endif /* HTTP_SERVER_LIBRARY_MODE */
