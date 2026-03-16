# 🧝 Módulo 6: El Artesano del Escritorio — Hyprland Ricing (Rivendell)

## Resumen Técnico

### ¿Qué es Hyprland?

**Hyprland** es un compositor dinámico de ventanas en mosaico (*tiling*) para el
protocolo **Wayland**. Escrito en C++, es conocido por sus animaciones fluidas,
amplia personalización y sistema de plugins.

A diferencia de los gestores de ventanas tradicionales de X11, Hyprland actúa
simultáneamente como **compositor** y **gestor de ventanas** — no necesita un
compositor externo como `picom`. Esto le permite tener control total sobre el
renderizado, las animaciones y los efectos visuales.

Características clave:

- **Tiling dinámico**: las ventanas se organizan automáticamente sin solaparse
- **Animaciones nativas**: transiciones suaves entre workspaces, apertura/cierre de ventanas
- **Sistema de plugins**: extensible mediante plugins en C++ que se cargan en tiempo de ejecución
- **Configuración en caliente**: los cambios en `hyprland.conf` se aplican instantáneamente
- **Protocolo IPC**: comunicación con scripts externos vía socket Unix

### ¿Qué es Wayland?

Wayland **NO** es un servidor ni un programa — es un **protocolo** que define cómo el
compositor y las aplicaciones cliente se comunican entre sí. El compositor es el
"servidor de pantalla" que gestiona directamente la entrada (teclado, ratón), la
salida (monitores) y el renderizado.

En Wayland:
- El **compositor** (ej. Hyprland) = el programa que implementa el protocolo
- Los **clientes** (ej. Firefox, Kitty) = las aplicaciones que dibujan sus ventanas
- El **protocolo** = las reglas de comunicación entre ambos

### Wayland vs X11 — Arquitectura comparada

**X11** es un protocolo con más de 40 años de antigüedad. Utiliza una arquitectura
cliente-servidor donde el **X Server** actúa como intermediario entre las aplicaciones
y el hardware. Esto genera varios problemas:

- **Seguridad**: cualquier aplicación puede espiar las ventanas de otras (keyloggers triviales)
- **Tearing**: sincronización de frames deficiente sin compositor externo
- **Complejidad**: código legacy masivo, extensiones sobre extensiones (XRandR, XInput, GLX...)
- **Rendimiento**: doble buffering ineficiente al pasar por el intermediario

**Wayland** elimina el intermediario — el compositor habla directamente con el kernel
mediante **KMS/DRM** (para pantalla) y **libinput** (para entrada). Cada aplicación
renderiza en su propio buffer y el compositor los compone en la imagen final.

```
╔═══════════════════════════════════════════════════════════════╗
║                    ARQUITECTURA X11                          ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║   ┌──────────┐  ┌──────────┐  ┌──────────┐                   ║
║   │  App 1   │  │  App 2   │  │  App 3   │   Clientes        ║
║   └────┬─────┘  └────┬─────┘  └────┬─────┘                   ║
║        │              │              │                         ║
║        ▼              ▼              ▼                         ║
║   ┌──────────────────────────────────────┐                    ║
║   │           X SERVER (Xorg)            │   Intermediario    ║
║   │  • Gestiona ventanas                 │                    ║
║   │  • Recibe input del kernel           │                    ║
║   │  • Reenvía eventos a apps            │                    ║
║   └───────────────┬──────────────────────┘                    ║
║                   │                                           ║
║                   ▼                                           ║
║   ┌──────────────────────────────────────┐                    ║
║   │     COMPOSITOR EXTERNO (picom)       │   Otro proceso     ║
║   │  • Efectos, transparencias           │                    ║
║   │  • VSync, anti-tearing               │                    ║
║   └───────────────┬──────────────────────┘                    ║
║                   │                                           ║
║                   ▼                                           ║
║   ┌──────────────────────────────────────┐                    ║
║   │         KERNEL (KMS/DRM)             │   Hardware         ║
║   └──────────────────────────────────────┘                    ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝

╔═══════════════════════════════════════════════════════════════╗
║                  ARQUITECTURA WAYLAND                        ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║   ┌──────────┐  ┌──────────┐  ┌──────────┐                   ║
║   │  App 1   │  │  App 2   │  │  App 3   │   Clientes        ║
║   │ (buffer) │  │ (buffer) │  │ (buffer) │   (cada uno       ║
║   └────┬─────┘  └────┬─────┘  └────┬─────┘    renderiza      ║
║        │              │              │          su buffer)     ║
║        └──────────────┼──────────────┘                        ║
║                       │                                       ║
║                       ▼                                       ║
║   ┌──────────────────────────────────────┐                    ║
║   │   COMPOSITOR (Hyprland/Sway/etc)     │   TODO en uno      ║
║   │  • Gestiona ventanas                 │                    ║
║   │  • Compone los buffers               │                    ║
║   │  • Efectos y animaciones             │                    ║
║   │  • Recibe input directamente         │                    ║
║   └───────────────┬──────────────────────┘                    ║
║                   │                                           ║
║          ┌────────┴────────┐                                  ║
║          ▼                 ▼                                   ║
║   ┌────────────┐  ┌──────────────┐                            ║
║   │  KMS/DRM   │  │   libinput   │   Kernel directo           ║
║   │ (pantalla) │  │  (teclado,   │                            ║
║   │            │  │    ratón)    │                            ║
║   └────────────┘  └──────────────┘                            ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
```

Ventajas de Wayland:
- **Seguridad**: aislamiento entre aplicaciones (una app no puede capturar otra)
- **Rendimiento**: sin intermediario, renderizado directo
- **VSync nativo**: sin tearing por diseño
- **Simplicidad**: una sola pieza (compositor) en vez de múltiples componentes

### ¿Qué es "ricing"?

El **ricing** es el arte de personalizar la apariencia visual y el flujo de trabajo
de un escritorio Linux. Desde los bordes de las ventanas hasta las barras de estado,
pasando por animaciones, fondos de pantalla, esquemas de colores y tipografías.

El término proviene del mundo automovilístico: **R.I.C.E.** — *Race Inspired Cosmetic
Enhancements* (mejoras cosméticas inspiradas en carreras). En el contexto de Linux,
se refiere a hacer que tu escritorio se vea único y espectacular, a menudo compartiendo
los resultados en comunidades como [r/unixporn](https://www.reddit.com/r/unixporn/).

El ricing implica dominar:
- **Compositor/WM**: Hyprland, Sway, i3, bspwm
- **Barra de estado**: Waybar, Polybar, EWW
- **Terminal**: Kitty, Alacritty, WezTerm
- **Shell**: Zsh + Starship, Fish
- **Colores y fuentes**: pywal, esquemas personalizados, Nerd Fonts
- **Notificaciones**: Mako, Dunst
- **Widgets**: Conky, EWW, Quickshell

---

## Contexto — Proyecto Rivendell

Este módulo está basado en la entrada ganadora de **zacoons** en la **4ta Competición
de Hyprland Ricing**. El tema **"Rivendell"** se inspira en la ciudad élfica de Tolkien
— una estética elegante, orgánica y fantástica.

### Innovaciones técnicas clave

1. **Bordes de ventana personalizados**: implementados mediante *9-slice scaling*, una
   técnica que permite escalar imágenes decorativas sin distorsión. Se logra con un
   plugin de Hyprland escrito en C++.

2. **Efectos de sonido por IPC**: el compositor emite eventos mediante su protocolo IPC
   (Inter-Process Communication) cada vez que se abre, cierra o cambia una ventana.
   Un script en Bash escucha estos eventos y reproduce efectos de sonido temáticos.

3. **Widgets Quickshell con parallax**: la barra de estado y widgets se implementan
   con **Quickshell** (framework QML para shells de Wayland), incluyendo efectos de
   parallax que responden al movimiento del cursor.

4. **Herramienta de screenshot con física de cuerdas**: una herramienta de captura de
   pantalla donde la selección se comporta como una cuerda con física realista,
   implementada con integración de Verlet.

### Referencias

- **Código fuente**: [codeberg.org/zacoons/rivendell-hyprdots](https://codeberg.org/zacoons/rivendell-hyprdots)
- **Video demostración**: [youtube.com/watch?v=DxEKF0cuEzc](https://www.youtube.com/watch?v=DxEKF0cuEzc)

---

## Sub-módulos

| # | Sub-módulo | Concepto | Lenguaje |
|---|-----------|----------|----------|
| 6.1 | **El Arquitecto de Bordes** | 9-slice scaling, plugins C++ | C++ |
| 6.2 | **El Sentido del Oído** | IPC, eventos de ventana, sonidos | Bash/Shell |
| 6.3 | **Pergaminos Digitales** | Quickshell, QML, widgets | QML |
| 6.4 | **Física de Cuerdas** | Rope physics, integración de Verlet | Python |

Cada sub-módulo se encuentra en `codigo/` y contiene su propio `README.md` con
explicaciones técnicas detalladas, código comentado y ejercicios.

---

## Requisitos del Sistema

### Sistema operativo

- Una distribución de **Linux** (se recomienda **Arch Linux**)
- Si no tienes Arch instalado, consulta la guía completa en [`guia-arch-linux/`](guia-arch-linux/tutorial-arch-linux.md)
- Una GPU con soporte para Wayland (la mayoría de GPUs modernas de AMD, Intel y NVIDIA ≥ 500 series)

### Hyprland

- **hyprland-git** (última versión desde git, necesaria para soporte de plugins)
- Se instala desde el AUR: `yay -S hyprland-git`

### Dependencias principales

```bash
# Compositor y shell
hyprland-git          # Compositor Wayland (versión git)
quickshell            # Framework QML para shells Wayland

# Herramientas del sistema
socat                 # Comunicación con el socket IPC de Hyprland
sox                   # Reproducción de efectos de sonido
pipewire              # Servidor de audio moderno
wireplumber           # Session manager para PipeWire

# Captura y pantalla
grim                  # Captura de pantalla en Wayland
slurp                 # Selector de región en Wayland

# Interfaz
waybar                # Barra de estado para Wayland
mako                  # Demonio de notificaciones (alternativa: dunst)

# Gestión de sesión
swayidle              # Gestión de inactividad
swaylock              # Bloqueo de pantalla
```

### ¿Sin Linux? Modo Docker

Para aprender sin una instalación completa de Linux, los sub-módulos de **C++** (6.1)
y **Python** (6.4) pueden ejecutarse en contenedores Docker. Cada uno incluye un
`Dockerfile` con todo lo necesario.

```bash
# Ejemplo: ejecutar el sub-módulo de C++
cd codigo/6.1-el-arquitecto-de-bordes/
docker build -t modulo-6-1 .
docker run -it modulo-6-1
```

> ⚠️ Los sub-módulos 6.2 (Bash/IPC) y 6.3 (Quickshell/QML) requieren un entorno
> Wayland real con Hyprland ejecutándose, por lo que no pueden funcionar en Docker.

---

## Estructura del Módulo

```
modulo-6-hyprland-ricing/
├── README.md                          ← Estás aquí
├── guia-arch-linux/
│   └── tutorial-arch-linux.md         ← Guía completa de instalación
└── codigo/
    ├── 6.1-el-arquitecto-de-bordes/   ← Plugin C++ de bordes (9-slice)
    │   ├── README.md
    │   ├── src/
    │   └── Dockerfile
    ├── 6.2-el-sentido-del-oido/       ← Script IPC + sonidos
    │   ├── README.md
    │   ├── scripts/
    │   └── sounds/
    ├── 6.3-pergaminos-digitales/      ← Widgets Quickshell/QML
    │   ├── README.md
    │   └── qml/
    └── 6.4-fisica-de-cuerdas/         ← Herramienta screenshot
        ├── README.md
        ├── src/
        └── Dockerfile
```

---

## Cómo empezar

### Paso 1: Prepara tu entorno Linux

Si aún no tienes Arch Linux (o una distribución compatible), sigue la
[Guía Completa de Arch Linux](guia-arch-linux/tutorial-arch-linux.md). La guía
cubre desde la instalación base hasta la configuración de Hyprland.

### Paso 2: Configura Hyprland

Una vez en Arch Linux, instala Hyprland y sus dependencias:

```bash
# Instalar yay (AUR helper) si no lo tienes
git clone https://aur.archlinux.org/yay.git
cd yay && makepkg -si

# Instalar Hyprland y herramientas esenciales
yay -S hyprland-git waybar mako kitty wofi \
       grim slurp pipewire wireplumber \
       swayidle swaylock socat sox
```

Inicia Hyprland desde la TTY:

```bash
Hyprland
```

### Paso 3: Trabaja los sub-módulos en orden

Los sub-módulos están diseñados para seguirse en secuencia:

1. **6.1 — El Arquitecto de Bordes**: aprende C++ aplicado a plugins de compositor.
   Entenderás cómo Hyprland carga extensiones y cómo funciona el 9-slice scaling.

2. **6.2 — El Sentido del Oído**: aprende IPC y scripting en Bash. Conectarás
   eventos del compositor con acciones del sistema.

3. **6.3 — Pergaminos Digitales**: aprende QML y diseño de widgets. Crearás
   interfaces visuales que se integran con el compositor.

4. **6.4 — Física de Cuerdas**: aprende simulación física en Python. Implementarás
   una herramienta interactiva con física de cuerdas.

---

## Lore

> *Eres un artesano élfico de Rivendell. Tu misión es transformar un escritorio
> Linux común en una obra maestra visual digna de la Tierra Media.*
>
> *Cada sub-módulo te enseña una técnica ancestral de los elfos:*
>
> *En **El Arquitecto de Bordes**, aprenderás a forjar marcos ornamentales para
> las ventanas de cristal — como los arcos tallados que adornan los salones de
> Elrond.*
>
> *En **El Sentido del Oído**, despertarás los sonidos del valle — cada ventana
> que se abre resonará como las campanas de plata de Rivendell.*
>
> *En **Pergaminos Digitales**, crearás pergaminos mágicos que flotan sobre el
> escritorio — widgets que muestran información con la elegancia de la escritura
> Tengwar.*
>
> *En **Física de Cuerdas**, dominarás las leyes de la naturaleza para crear una
> herramienta de captura que se comporta como las cuerdas élficas de la Lothlórien
> — flexibles, elegantes, y con voluntad propia.*
>
> *Al completar los cuatro módulos, habrás transformado un escritorio vacío en
> Rivendell — el Último Hogar Acogedor al este del Mar.*

---

## Navegación

| ← Anterior | Inicio | Siguiente → |
|:-----------:|:------:|:-----------:|
| [Módulo 5: Sampling Profiler](../modulo-5-sampling-profiler/) | [README principal](../../README.md) | — |
