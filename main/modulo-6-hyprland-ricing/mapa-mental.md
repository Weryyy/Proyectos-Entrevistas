# 🎨 Mapa Mental — Desktop Customization (Ricing) & Hyprland

## ⏱ Tiempo estimado: 15–25 horas

```
                     ╔═══════════════════════════╗
                     ║  DESKTOP CUSTOMIZATION    ║
                     ║  (RICING) & HYPRLAND      ║
                     ╚════════════╤══════════════╝
                                  │
       ┌──────────────┬───────────┼───────────┬────────────────┐
       ▼              ▼           ▼           ▼                ▼
 ┌───────────┐ ┌────────────┐ ┌────────┐ ┌──────────┐  ┌────────────┐
 │PREREQUISI-│ │ CONCEPTOS  │ │  RUTA  │ │ RECURSOS │  │ SIGUIENTES │
 │   TOS     │ │   CLAVE    │ │  DE    │ │          │  │   PASOS    │
 └─────┬─────┘ └─────┬──────┘ │ESTUDIO │ └────┬─────┘  └─────┬──────┘
       │              │        └───┬────┘      │              │
       ▼              ▼            ▼           ▼              ▼
```

---

## 📋 Prerequisitos

```
  Prerequisitos
  ├── Linux básico
  │   ├── Navegación por terminal
  │   ├── Gestión de paquetes (pacman/apt)
  │   └── Permisos y sistema de archivos
  ├── Terminal
  │   ├── Editores: vim / nano
  │   ├── Shell scripting básico (bash)
  │   └── Variables de entorno
  └── Conocimientos opcionales pero útiles
      ├── C++ básico (para plugins)
      ├── Git (para dotfiles)
      └── QML / CSS (para widgets)
```

## 🔑 Conceptos Clave

```
  Conceptos Clave
  ├── Wayland vs X11
  │   ├── X11: protocolo legacy, display server
  │   ├── Wayland: protocolo moderno, más seguro
  │   └── Hyprland es un compositor Wayland
  ├── Compositor (Window Manager)
  │   ├── Gestiona ventanas y su disposición
  │   ├── Tiling: ventanas organizadas automáticamente
  │   └── Animaciones y efectos visuales
  ├── Plugins C++
  │   ├── Hyprland soporta plugins nativos
  │   ├── API del compositor
  │   └── Compilar contra las cabeceras de Hyprland
  ├── IPC (Inter-Process Communication)
  │   ├── hyprctl — controlar Hyprland vía CLI
  │   ├── Sockets UNIX
  │   └── Automatizar acciones del escritorio
  ├── QML (Qt Modeling Language)
  │   ├── Declarativo para UIs
  │   ├── Widgets personalizados
  │   └── Integración con datos del sistema
  ├── 9-slice Scaling
  │   ├── Técnica para escalar bordes de ventanas
  │   ├── Esquinas fijas, bordes estirables
  │   └── Común en temas y decoraciones
  └── Rope Physics (simulación de cuerda)
      ├── Animaciones basadas en física
      ├── Movimiento orgánico de elementos
      └── Implementación con puntos y restricciones
```

## 🗺 Ruta de Estudio

```
  ① Instalar Arch Linux
  │   ├── → archinstall o instalación manual
  │   └── → Configurar drivers de GPU (mesa/nvidia)
  │
  ② Configurar Hyprland
  │   ├── → Instalar: hyprland, waybar, wofi, kitty
  │   ├── → Archivo: ~/.config/hypr/hyprland.conf
  │   └── → Keybindings, monitores, workspaces
  │
  ③ Dotfiles y tematización
  │   ├── → Gestionar con Git (bare repo o stow)
  │   ├── → Temas GTK/Qt, iconos, cursores
  │   └── → Wallpapers con hyprpaper / swww
  │
  ④ Plugins de Hyprland
  │   ├── → Instalar hyprpm (plugin manager)
  │   ├── → Explorar: borders-plus-plus, hyprtrails
  │   └── → Crear un plugin básico en C++
  │
  ⑤ Widgets personalizados
  │   ├── → Eww o AGS para barras/widgets
  │   ├── → Integrar info del sistema (batería, CPU, RAM)
  │   └── → Notificaciones con dunst / mako
  │
  ⑥ Pulir el escritorio
      ├── → Animaciones fluidas
      ├── → Esquema de colores coherente
      ├── → Screenshots y compartir en r/unixporn
      └── → Documentar tu setup
```

## 📚 Recursos

```
  Recursos
  ├── Hyprland Wiki — wiki.hyprland.org
  ├── Arch Wiki — wiki.archlinux.org
  ├── r/unixporn — reddit.com/r/unixporn (inspiración)
  ├── Hyprland GitHub — github.com/hyprwm/Hyprland
  └── ArchWiki — Wayland, Sway, Hyprland
```

## 🚀 Siguientes Pasos

```
  Después de dominar Hyprland Ricing →
  ├── NixOS
  │   └── → Configuración declarativa del sistema completo
  ├── Sway (compositor Wayland alternativo)
  ├── AwesomeWM (compositor X11 con Lua)
  ├── Crear tu propio compositor
  │   ├── → wlroots (librería base para compositors)
  │   └── → Smithay (compositor en Rust)
  └── Contribuir a Hyprland
      ├── → Reportar bugs
      └── → Crear y publicar plugins
```

---

> **💡 Consejo:** El ricing es un arte iterativo. No intentes lograr el
> escritorio perfecto de una vez. Empieza funcional, luego ve añadiendo
> detalles. Y siempre versiona tus dotfiles con Git.
