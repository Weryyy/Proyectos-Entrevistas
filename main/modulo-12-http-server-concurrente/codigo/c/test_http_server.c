/*
 * test_http_server.c — Tests unitarios para el servidor HTTP
 * Módulo 12: The Anthropic Gauntlet
 *
 * Compila con: make test
 * Corre con:   ./test_http_server
 */

#include "http_server.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>

/* ── Macro de test ────────────────────────────────────────────────────── */
#define TEST(name) \
    do { printf("  %-50s", name); fflush(stdout); } while(0)
#define PASS() \
    do { printf("OK\n"); } while(0)
#define FAIL(msg) \
    do { printf("FAIL: %s\n", msg); assert(0); } while(0)

/* ─────────────────────────────────────────────────────────────────────── */
/* Tests del parser HTTP                                                     */
/* ─────────────────────────────────────────────────────────────────────── */

static void test_parse_get_basic(void)
{
    TEST("parse: GET /index.html HTTP/1.1");
    HttpRequest req;
    const char *raw = "GET /index.html HTTP/1.1\r\nHost: localhost\r\n\r\n";
    assert(http_parse_request(raw, &req) == 0);
    assert(strcmp(req.method,  "GET")          == 0);
    assert(strcmp(req.path,    "/index.html")  == 0);
    assert(strcmp(req.version, "HTTP/1.1")     == 0);
    PASS();
}

static void test_parse_get_root(void)
{
    TEST("parse: GET / HTTP/1.0");
    HttpRequest req;
    assert(http_parse_request("GET / HTTP/1.0\r\n\r\n", &req) == 0);
    assert(strcmp(req.method, "GET")     == 0);
    assert(strcmp(req.path,   "/")       == 0);
    assert(strcmp(req.version,"HTTP/1.0")== 0);
    PASS();
}

static void test_parse_post(void)
{
    TEST("parse: POST /api/data HTTP/1.1");
    HttpRequest req;
    assert(http_parse_request("POST /api/data HTTP/1.1\r\n\r\n", &req) == 0);
    assert(strcmp(req.method, "POST") == 0);
    assert(strcmp(req.path, "/api/data") == 0);
    PASS();
}

static void test_parse_keep_alive_http11(void)
{
    TEST("parse: keep-alive implícito en HTTP/1.1");
    HttpRequest req;
    assert(http_parse_request("GET / HTTP/1.1\r\nHost: x\r\n\r\n", &req) == 0);
    assert(req.keep_alive == 1);  /* HTTP/1.1 tiene keep-alive por defecto */
    PASS();
}

static void test_parse_keep_alive_explicit(void)
{
    TEST("parse: Connection: keep-alive explícito");
    HttpRequest req;
    const char *raw = "GET / HTTP/1.0\r\nConnection: keep-alive\r\n\r\n";
    assert(http_parse_request(raw, &req) == 0);
    assert(req.keep_alive == 1);
    PASS();
}

static void test_parse_connection_close(void)
{
    TEST("parse: Connection: close → keep_alive=0");
    HttpRequest req;
    const char *raw = "GET / HTTP/1.1\r\nConnection: close\r\n\r\n";
    assert(http_parse_request(raw, &req) == 0);
    assert(req.keep_alive == 0);
    PASS();
}

static void test_parse_invalid_empty(void)
{
    TEST("parse: string vacío → error -1");
    HttpRequest req;
    assert(http_parse_request("", &req) == -1);
    PASS();
}

static void test_parse_invalid_null(void)
{
    TEST("parse: NULL → error -1");
    assert(http_parse_request(NULL, NULL) == -1);
    PASS();
}

static void test_parse_incomplete(void)
{
    TEST("parse: línea incompleta (solo método) → error -1");
    HttpRequest req;
    assert(http_parse_request("GET\r\n", &req) == -1);
    PASS();
}

/* ─────────────────────────────────────────────────────────────────────── */
/* Tests del detector de MIME types                                          */
/* ─────────────────────────────────────────────────────────────────────── */

static void test_mime_html(void)
{
    TEST("mime: .html → text/html");
    const char *ct = http_get_content_type("/foo/bar.html");
    assert(strncmp(ct, "text/html", 9) == 0);
    PASS();
}

static void test_mime_css(void)
{
    TEST("mime: .css → text/css");
    assert(strcmp(http_get_content_type("style.css"), "text/css") == 0);
    PASS();
}

static void test_mime_js(void)
{
    TEST("mime: .js → application/javascript");
    assert(strcmp(http_get_content_type("/app.js"), "application/javascript") == 0);
    PASS();
}

static void test_mime_json(void)
{
    TEST("mime: .json → application/json");
    assert(strcmp(http_get_content_type("data.json"), "application/json") == 0);
    PASS();
}

static void test_mime_png(void)
{
    TEST("mime: .png → image/png");
    assert(strcmp(http_get_content_type("logo.png"), "image/png") == 0);
    PASS();
}

static void test_mime_unknown(void)
{
    TEST("mime: sin extensión → application/octet-stream");
    assert(strcmp(http_get_content_type("archivo_sin_extension"),
                  "application/octet-stream") == 0);
    PASS();
}

static void test_mime_uppercase(void)
{
    TEST("mime: .HTML mayúscula → text/html (case insensitive)");
    const char *ct = http_get_content_type("INDEX.HTML");
    assert(strncmp(ct, "text/html", 9) == 0);
    PASS();
}

/* ─────────────────────────────────────────────────────────────────────── */
/* Tests del thread pool                                                     */
/* ─────────────────────────────────────────────────────────────────────── */

static void test_threadpool_init_destroy(void)
{
    TEST("threadpool: init con 4 workers y destroy limpio");
    HttpServer srv;
    memset(&srv, 0, sizeof(srv));
    srv.running = 1;

    ThreadPool pool;
    assert(thread_pool_init(&pool, 4, &srv) == 0);
    thread_pool_destroy(&pool);
    PASS();
}

static void test_threadpool_invalid_workers(void)
{
    TEST("threadpool: 0 workers → init retorna -1");
    ThreadPool pool;
    assert(thread_pool_init(&pool, 0, NULL) == -1);
    PASS();
}

static void test_threadpool_too_many_workers(void)
{
    TEST("threadpool: workers > MAX → init retorna -1");
    ThreadPool pool;
    assert(thread_pool_init(&pool, HTTP_SERVER_MAX_WORKERS + 1, NULL) == -1);
    PASS();
}

/* ─────────────────────────────────────────────────────────────────────── */
/* main                                                                      */
/* ─────────────────────────────────────────────────────────────────────── */

int main(void)
{
    printf("\n=== Tests: http_server ===\n\n");

    printf("── Parser HTTP ──────────────────────────────────────────────\n");
    test_parse_get_basic();
    test_parse_get_root();
    test_parse_post();
    test_parse_keep_alive_http11();
    test_parse_keep_alive_explicit();
    test_parse_connection_close();
    test_parse_invalid_empty();
    test_parse_invalid_null();
    test_parse_incomplete();

    printf("\n── Tipos MIME ───────────────────────────────────────────────\n");
    test_mime_html();
    test_mime_css();
    test_mime_js();
    test_mime_json();
    test_mime_png();
    test_mime_unknown();
    test_mime_uppercase();

    printf("\n── Thread Pool ──────────────────────────────────────────────\n");
    test_threadpool_init_destroy();
    test_threadpool_invalid_workers();
    test_threadpool_too_many_workers();

    printf("\n✅ Todos los tests pasaron.\n\n");
    return 0;
}
