# Sub-módulo 6.2: El Sentido del Oído — IPC & Shell Scripting

## Descripción

Este sub-módulo enseña **Comunicación Entre Procesos (IPC)** aplicada a la
personalización de un compositor Wayland. El concepto: escuchar eventos del
compositor (abrir/cerrar ventanas, cambiar workspace) y reproducir sonidos
temáticos como respuesta.

---

## Fundamentos Técnicos

### ¿Qué es IPC (Inter-Process Communication)?

IPC es el conjunto de mecanismos que permiten a procesos independientes
intercambiar datos. En Unix/Linux los más comunes son:

| Mecanismo | Descripción | Ejemplo |
|-----------|-------------|---------|
| **Pipes** (`\|`) | Unidireccionales, anónimos | `ls \| grep txt` |
| **Named Pipes (FIFOs)** | Pipes con nombre en el filesystem | `mkfifo /tmp/mi_pipe` |
| **Unix Domain Sockets** | Bidireccionales, alto rendimiento | Archivos `.sock` |
| **Señales** | Notificaciones asíncronas | `kill -SIGUSR1 $PID` |
| **Shared Memory** | Memoria compartida entre procesos | `shmget`, `mmap` |

### Named Pipes (FIFOs)

```bash
# Crear una FIFO
mkfifo /tmp/eventos

# Proceso escritor (en una terminal):
echo "windowopenev>>kitty,Terminal" > /tmp/eventos

# Proceso lector (en otra terminal):
cat /tmp/eventos
# Output: windowopenev>>kitty,Terminal
```

Las FIFOs son bloqueantes: el escritor espera hasta que haya un lector, y
viceversa. Son perfectas para simular el flujo de eventos de un compositor.

### Unix Domain Sockets

Los sockets Unix son más potentes que las FIFOs:
- Bidireccionales
- Soportan múltiples clientes simultáneos
- Permiten paso de file descriptors entre procesos

Hyprland usa Unix Domain Sockets para su sistema IPC.

---

## Cómo Funciona Hyprland IPC

Hyprland expone **dos sockets Unix** por instancia:

```
$XDG_RUNTIME_DIR/hypr/$HYPRLAND_INSTANCE_SIGNATURE/
├── .socket.sock     # Socket de comandos (petición/respuesta)
└── .socket2.sock    # Socket de eventos (streaming unidireccional)
```

### Socket de Eventos (`.socket2.sock`)

Este socket emite eventos en tiempo real con el formato:

```
evento>>datos
```

#### Eventos principales:

| Evento | Datos | Cuándo |
|--------|-------|--------|
| `windowopenev` | `clase,título` | Se abre una ventana |
| `destroywindow` | `dirección` | Se cierra una ventana |
| `activewindow` | `clase,título` | Cambia la ventana activa |
| `workspace` | `nombre` | Cambia el workspace |
| `fullscreen` | `0\|1` | Entra/sale de pantalla completa |
| `monitoradded` | `nombre` | Se conecta un monitor |

### Escuchar eventos con `socat`

```bash
# Conectar al socket de eventos de Hyprland
SOCKET="$XDG_RUNTIME_DIR/hypr/$HYPRLAND_INSTANCE_SIGNATURE/.socket2.sock"
socat -U - UNIX-CONNECT:"$SOCKET"
```

El flag `-U` indica modo unidireccional (solo lectura). Los eventos llegan
línea por línea conforme ocurren en el compositor.

---

## Reproducción de Sonidos con `sox`

[SoX](http://sox.sourceforge.net/) (Sound eXchange) es la "navaja suiza" del
audio en línea de comandos:

```bash
# Reproducir un sonido (modo silencioso)
play -q /ruta/al/sonido.wav

# Reproducir con volumen reducido
play -q -v 0.5 /ruta/al/sonido.wav

# Alternativa con PipeWire
pw-play /ruta/al/sonido.wav
```

---

## El Concepto: Sonidos Temáticos

Inspirado en el proyecto **Rivendell** de zacoons:

| Evento | Ventana | Sonido | Concepto |
|--------|---------|--------|----------|
| Abrir ventana | Terminal (kitty/Alacritty) | `scroll_unfurl.wav` | Pergamino desenrollándose |
| Cerrar ventana | Terminal | `paper_crumple.wav` | Papel arrugándose |
| Abrir ventana | Firefox | `door_open.wav` | Puerta abriéndose |
| Cerrar ventana | Firefox | `door_close.wav` | Puerta cerrándose |
| Cambiar workspace | Cualquiera | `page_turn.wav` | Pasar página |

---

## Archivos del Sub-módulo

| Archivo | Descripción |
|---------|-------------|
| `ipc_event_system.sh` | Sistema IPC simulado completo (funciona en CI) |
| `hyprland_ipc_real.sh` | Script de referencia para Hyprland real |
| `test_ipc_events.sh` | Suite de tests con aserciones en Bash |

---

## Cómo Ejecutar

### Simulación (funciona en cualquier sistema Linux)

```bash
# Dar permisos de ejecución
chmod +x ipc_event_system.sh test_ipc_events.sh

# Ejecutar la demo interactiva
./ipc_event_system.sh

# Ejecutar los tests
./test_ipc_events.sh
```

### En un Sistema con Hyprland

```bash
chmod +x hyprland_ipc_real.sh

# Ejecutar manualmente
./hyprland_ipc_real.sh

# O añadir a hyprland.conf para arranque automático:
# exec-once = /ruta/a/hyprland_ipc_real.sh
```

---

## Conceptos Clave Aprendidos

1. **IPC con FIFOs**: Comunicación entre procesos usando named pipes
2. **Parsing de eventos**: Descomponer cadenas con formato estructurado
3. **Arrays asociativos en Bash**: Mapear eventos a acciones
4. **Traps y limpieza**: Gestión de recursos al estilo RAII
5. **Background processes**: Ejecutar listeners en segundo plano
6. **Pattern matching**: Wildcards para reglas genéricas
