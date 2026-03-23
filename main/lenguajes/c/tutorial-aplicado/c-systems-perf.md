# ⚙️ C Aplicado: Sistemas Concurrentes y Alto Rendimiento

En este tutorial exploramos cómo C es la base de la infraestructura de red, basándonos en el **Módulo 12 (HTTP Server Concurrent)** y el **Módulo 5 (Sampling Profiler)**.

---

## 🏗️ C for Networking & Performance

### 1. Sockets y Multi-hilo (Módulo 12)
C nos permite hablar directamente el lenguaje del hardware. Los `pthreads` se usan para que cada cliente tenga su propio hilo de ejecución, permitiendo que un servidor web atienda miles de peticiones.

```c
// Creación de un socket TCP
int server_fd = socket(AF_INET, SOCK_STREAM, 0);
// Asociación a un puerto
bind(server_fd, (struct sockaddr *)&address, sizeof(address));
```

### 2. Gestión Manual de Memoria (Módulo 5)
A diferencia de Python, aquí somos responsables de cada byte. En el profiler, aprendimos a mapear la pila de ejecución para entender dónde se pierde tiempo.

---

## 🚀 Ampliación y Escalabilidad (Tecnología de última hora)

### Mejoras Modernas (2025-2026):
1. **io_uring**: Es la nueva interfaz de Linux para E/S asíncrona. En el Módulo 12, en lugar de `pthreads` o `select/epoll`, usar `io_uring` permitiría procesar millones de peticiones por segundo con un solo hilo.
2. **eBPF (Extended Berkeley Packet Filter)**: Para el Módulo 5, en lugar de un profiler manual, eBPF permite inyectar código directamente en el kernel para perfilar programas sin detenerlos y con impacto cero en el rendimiento.

### Cambios para Escalabilidad:
- **Zero-Copy Networking**: Implementar transferencias de archivos donde los datos no pasen de un buffer a otro, sino que se envíen directamente del disco al socket de red.
- **Rust Interop**: Para aplicaciones grandes, usar C para las funciones hiper-optimizadas y **Rust** para la lógica de negocio, evitando errores de memoria.
