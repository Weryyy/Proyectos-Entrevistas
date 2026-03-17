# 🗺️ Mapa Mental — Módulo 12: Servidor HTTP Concurrente en C

```
                    ┌─────────────────────────────────────┐
                    │   Servidor HTTP Concurrente en C    │
                    └─────────────────────────────────────┘
                                     │
           ┌─────────────────────────┼─────────────────────────┐
           │                         │                         │
    ┌──────▼──────┐          ┌───────▼───────┐        ┌───────▼───────┐
    │  Sockets    │          │  Thread Pool  │        │  HTTP Parser  │
    │   POSIX     │          │               │        │               │
    └──────┬──────┘          └───────┬───────┘        └───────┬───────┘
           │                         │                         │
    ┌──────▼──────┐          ┌───────▼───────┐        ┌───────▼───────┐
    │ socket()    │          │ pthread_create │        │ Request line  │
    │ bind()      │          │ mutex         │        │ GET/POST      │
    │ listen()    │          │ cond_wait     │        │ Headers       │
    │ accept()    │          │ work_queue    │        │ Body          │
    │ send/recv() │          │ graceful stop │        │ Status codes  │
    └─────────────┘          └───────────────┘        └───────────────┘

PREREQUISITOS:
  → Programación en C (punteros, structs, malloc/free)
  → Sockets TCP/IP básicos
  → Concurrencia: hilos, mutex, variables de condición

CONCEPTOS CLAVE:
  → TCP three-way handshake → accept() retorna fd por conexión
  → Cada fd de cliente se encola → thread pool lo procesa
  → Parse HTTP: "GET /ruta HTTP/1.1\r\n\r\n"
  → Respuesta: "HTTP/1.1 200 OK\r\nContent-Length: N\r\n\r\n<body>"

SIGUIENTES PASOS:
  → TLS con OpenSSL (HTTPS)
  → HTTP/2 con multiplexing
  → io_uring para I/O asíncrono sin hilos
  → epoll para decenas de miles de conexiones (C10K)
```
