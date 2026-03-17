# 🌐 Módulo 12: Servidor HTTP Concurrente en C

## Descripción

Implementación de un servidor HTTP/1.1 concurrente en C utilizando **pthreads**
con un pool de hilos (thread pool), sin frameworks externos — solo la API POSIX.

El servidor soporta:
- Peticiones `GET` estáticas (archivos del sistema)
- Respuestas con códigos 200, 404 y 500
- Concurrencia mediante pool de hilos (configurable)
- Cabeceras HTTP básicas (Content-Type, Content-Length, Connection)
- Logging de peticiones a stderr

## Estructura

```
modulo-12-http-server-concurrente/
├── README.md
├── mapa-mental.md
├── notebook.ipynb
└── codigo/
    ├── c/
    │   ├── http_server.h       — Interfaz pública del servidor
    │   ├── http_server.c       — Implementación del servidor
    │   ├── test_http_server.c  — Tests con assert
    │   └── Makefile
    └── python/
        └── test_integration.py — Test de integración HTTP real
```

## Cómo ejecutar

```bash
# Compilar
cd codigo/c && make

# Ejecutar el servidor (puerto 8080, 4 hilos)
./http_server 8080 4

# En otra terminal, probar con curl
curl http://localhost:8080/
curl http://localhost:8080/index.html
```

## Conceptos clave

| Concepto | Descripción |
|----------|-------------|
| **Thread Pool** | N hilos worker pre-creados esperando en una cola de tareas |
| **Mutex + Condvar** | Sincronización para acceso seguro a la cola de tareas |
| **HTTP/1.1 Parsing** | Parseo manual de `GET /path HTTP/1.1\r\n` |
| **Socket API POSIX** | `socket()`, `bind()`, `listen()`, `accept()`, `send()`, `recv()` |
| **Keep-Alive** | Reutilización de conexiones TCP para múltiples requests |
