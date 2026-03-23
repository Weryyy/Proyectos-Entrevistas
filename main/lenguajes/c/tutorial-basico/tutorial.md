# 🔵 Tutorial de C (C17)

Guía de referencia rápida para el lenguaje C, orientada a los módulos de este repositorio (módulos 5 y 12).

---

## 📋 Índice

1. [Fundamentos de C17](#1-fundamentos-de-c17)
2. [Punteros y memoria dinámica](#2-punteros-y-memoria-dinámica)
3. [Structs y tipos definidos por el usuario](#3-structs-y-tipos-definidos-por-el-usuario)
4. [Manejo de errores](#4-manejo-de-errores)
5. [Entrada/Salida (stdio y POSIX)](#5-entradasalida-stdio-y-posix)
6. [Concurrencia con pthreads](#6-concurrencia-con-pthreads)
7. [Sockets TCP/IP](#7-sockets-tcpip)
8. [Makefile](#8-makefile)
9. [Testing con assert](#9-testing-con-assert)
10. [Recursos](#10-recursos)

---

## 1. Fundamentos de C17

```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>   // bool, true, false (C99+)
#include <stdint.h>    // uint32_t, int64_t, etc.
#include <string.h>

// Constantes con enum (preferir a #define para tipos)
typedef enum {
    ESTADO_OK    = 0,
    ESTADO_ERROR = 1,
    ESTADO_LLENO = 2,
} Estado;

// Macros útiles
#define MAX(a, b)      ((a) > (b) ? (a) : (b))
#define ARRAY_LEN(arr) (sizeof(arr) / sizeof((arr)[0]))

int main(void) {
    uint32_t n = 42;
    bool activo = true;

    printf("n = %u, activo = %s\n", n, activo ? "sí" : "no");
    return EXIT_SUCCESS;   // 0
}
```

---

## 2. Punteros y memoria dinámica

```c
#include <stdlib.h>
#include <string.h>

// Puntero básico
int x = 10;
int *px = &x;
printf("%d\n", *px);   // desreferenciar → 10

// malloc / calloc / realloc / free
int *arr = malloc(10 * sizeof(int));
if (!arr) { perror("malloc"); exit(EXIT_FAILURE); }

memset(arr, 0, 10 * sizeof(int));  // inicializar a cero

arr = realloc(arr, 20 * sizeof(int));   // ampliar
if (!arr) { perror("realloc"); exit(EXIT_FAILURE); }

free(arr);
arr = NULL;   // buena práctica: evita use-after-free

// strdup — duplicar cadena en heap
char *copia = strdup("hola mundo");
free(copia);
```

---

## 3. Structs y tipos definidos por el usuario

```c
#include <stdint.h>

// Struct con typedef
typedef struct {
    char    hostname[256];
    uint16_t puerto;
    bool     ssl_activo;
} Servidor;

// Inicialización designada (C99+)
Servidor s = {
    .hostname   = "192.168.1.10",
    .puerto     = 8006,
    .ssl_activo = true,
};

// Pasar struct por puntero (eficiente)
void imprimir_servidor(const Servidor *srv) {
    printf("%s:%u (ssl=%s)\n", srv->hostname, srv->puerto,
           srv->ssl_activo ? "sí" : "no");
}

// Lista enlazada
typedef struct Nodo {
    int           valor;
    struct Nodo  *siguiente;
} Nodo;

Nodo *nuevo_nodo(int v) {
    Nodo *n = malloc(sizeof(Nodo));
    if (!n) return NULL;
    n->valor     = v;
    n->siguiente = NULL;
    return n;
}
```

---

## 4. Manejo de errores

```c
#include <errno.h>
#include <string.h>
#include <stdio.h>

// errno + perror / strerror
FILE *f = fopen("config.txt", "r");
if (!f) {
    fprintf(stderr, "[ERROR] No se puede abrir config.txt: %s\n",
            strerror(errno));
    return EXIT_FAILURE;
}

// Patrón: retornar código de error desde funciones
typedef enum { OK = 0, ERR_MEMORIA = -1, ERR_SOCKET = -2 } Resultado;

Resultado crear_socket(int *fd_out) {
    int fd = socket(AF_INET, SOCK_STREAM, 0);
    if (fd < 0) return ERR_SOCKET;
    *fd_out = fd;
    return OK;
}
```

---

## 5. Entrada/Salida (stdio y POSIX)

```c
#include <stdio.h>
#include <unistd.h>
#include <fcntl.h>

// Leer fichero completo
char *leer_fichero(const char *ruta, size_t *longitud) {
    FILE *f = fopen(ruta, "rb");
    if (!f) return NULL;

    fseek(f, 0, SEEK_END);
    long tam = ftell(f);
    rewind(f);

    char *buf = malloc(tam + 1);
    if (!buf) { fclose(f); return NULL; }

    fread(buf, 1, tam, f);
    buf[tam] = '\0';
    if (longitud) *longitud = (size_t)tam;

    fclose(f);
    return buf;
}

// Descriptores POSIX
int fd = open("datos.bin", O_RDONLY);
char buffer[4096];
ssize_t leidos = read(fd, buffer, sizeof(buffer));
close(fd);
```

---

## 6. Concurrencia con pthreads

```c
#include <pthread.h>
#include <stdio.h>

// Mutex
pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;
int contador_global = 0;

void *incrementar(void *arg) {
    for (int i = 0; i < 1000; i++) {
        pthread_mutex_lock(&mutex);
        contador_global++;
        pthread_mutex_unlock(&mutex);
    }
    return NULL;
}

int main(void) {
    pthread_t hilos[4];

    for (int i = 0; i < 4; i++)
        pthread_create(&hilos[i], NULL, incrementar, NULL);

    for (int i = 0; i < 4; i++)
        pthread_join(hilos[i], NULL);

    pthread_mutex_destroy(&mutex);
    printf("Contador: %d (esperado: 4000)\n", contador_global);
    return 0;
}
// Compilar: gcc -o demo demo.c -lpthread
```

---

## 7. Sockets TCP/IP

```c
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>

// Servidor TCP mínimo
int fd = socket(AF_INET, SOCK_STREAM, 0);

// Reutilizar puerto tras reinicio
int opt = 1;
setsockopt(fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

struct sockaddr_in addr = {
    .sin_family      = AF_INET,
    .sin_addr.s_addr = INADDR_ANY,
    .sin_port        = htons(8080),
};
bind(fd, (struct sockaddr *)&addr, sizeof(addr));
listen(fd, 128);   // backlog

while (1) {
    struct sockaddr_in cliente;
    socklen_t len = sizeof(cliente);
    int conn = accept(fd, (struct sockaddr *)&cliente, &len);
    // manejar conn en hilo separado
    close(conn);
}
close(fd);
```

---

## 8. Makefile

```makefile
CC      = gcc
CFLAGS  = -std=c17 -Wall -Wextra -Wpedantic -O2
LDFLAGS = -lpthread

SRC  = http_server.c main.c
OBJ  = $(SRC:.c=.o)
BIN  = servidor

.PHONY: all clean test

all: $(BIN)

$(BIN): $(OBJ)
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)

%.o: %.c
	$(CC) $(CFLAGS) -c -o $@ $<

test: test_servidor
	./test_servidor

test_servidor: test_servidor.c http_server.c
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)

clean:
	rm -f $(OBJ) $(BIN) test_servidor
```

---

## 9. Testing con assert

```c
#include <assert.h>
#include <stdio.h>
#include <string.h>

// Función a testear
int sumar(int a, int b) { return a + b; }

// Tests
void test_sumar_positivos(void) {
    assert(sumar(2, 3) == 5);
    printf("[OK] test_sumar_positivos\n");
}

void test_sumar_negativos(void) {
    assert(sumar(-1, -1) == -2);
    printf("[OK] test_sumar_negativos\n");
}

void test_sumar_cero(void) {
    assert(sumar(0, 0) == 0);
    printf("[OK] test_sumar_cero\n");
}

int main(void) {
    test_sumar_positivos();
    test_sumar_negativos();
    test_sumar_cero();
    printf("\n✅ Todos los tests pasaron.\n");
    return 0;
}
// Compilar: gcc -std=c17 -o test_sumar test_sumar.c
// Ejecutar: ./test_sumar
```

---

## 10. Recursos

- [cppreference — referencia C17](https://en.cppreference.com/w/c)
- [The C Programming Language (K&R)](https://en.wikipedia.org/wiki/The_C_Programming_Language)
- [Beej's Guide to Network Programming](https://beej.us/guide/bgnet/)
- [Beej's Guide to C Programming](https://beej.us/guide/bgc/)
- [pthreads tutorial — LLNL](https://hpc-tutorials.llnl.gov/posix/)
