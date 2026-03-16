# 🖥 Mapa Mental — CLI Tools & Terminal Mastery

## ⏱ Tiempo estimado: 8–12 horas

```
                      ╔══════════════════════════╗
                      ║    CLI  TOOLS  &         ║
                      ║    TERMINAL  MASTERY     ║
                      ╚════════════╤═════════════╝
                                   │
       ┌──────────────┬────────────┼──────────┬────────────────┐
       ▼              ▼            ▼          ▼                ▼
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
  ├── Python básico-intermedio
  │   ├── Scripts y módulos
  │   ├── sys, os, subprocess
  │   └── Manejo de strings y formato
  ├── Terminal básica
  │   ├── Navegación: cd, ls, cat, grep
  │   ├── Redirección: >, >>, <
  │   └── Piping: comando1 | comando2
  └── Conceptos generales
      ├── Procesos y señales
      └── Variables de entorno (PATH, HOME)
```

## 🔑 Conceptos Clave

```
  Conceptos Clave
  ├── Piping y Streams
  │   ├── stdin  (fd 0) → entrada estándar
  │   ├── stdout (fd 1) → salida estándar
  │   ├── stderr (fd 2) → salida de errores
  │   ├── Pipe: stdout de uno → stdin de otro
  │   └── Filosofía Unix: hacer una cosa bien
  ├── Códigos ANSI / Escape Sequences
  │   ├── Colores: \033[31m (rojo), \033[32m (verde)...
  │   ├── Estilos: negrita, subrayado, parpadeo
  │   ├── Cursor: mover, ocultar, limpiar línea
  │   └── Reset: \033[0m
  ├── Señales (Signals)
  │   ├── SIGINT  (Ctrl+C) → interrumpir
  │   ├── SIGTERM → terminar gracefully
  │   ├── SIGTSTP (Ctrl+Z) → suspender
  │   └── signal.signal() en Python
  ├── ASCII Art
  │   ├── Texto decorativo con caracteres
  │   ├── Librerías: pyfiglet, art
  │   └── Cowsay: mensajes con vacas ASCII
  └── Animaciones en Terminal
      ├── Limpiar y redibujar (clear + print)
      ├── Spinners y barras de progreso
      ├── Frames por segundo con time.sleep()
      └── Secuencias ANSI para mover cursor
```

## 🗺 Ruta de Estudio

```
  ① Streams y piping
  │   ├── → Leer de stdin, escribir a stdout/stderr
  │   ├── → Crear filtros tipo Unix (cat, grep, wc)
  │   └── → Encadenar tus herramientas con pipes
  │
  ② Códigos ANSI
  │   ├── → Colorear texto en la terminal
  │   ├── → Mover el cursor, limpiar pantalla
  │   └── → Crear una paleta de colores propia
  │
  ③ Fortune y Cowsay
  │   ├── → Implementar fortune (frases aleatorias)
  │   ├── → Implementar cowsay (ASCII art + mensaje)
  │   └── → Combinar: fortune | cowsay
  │
  ④ Animaciones en terminal
  │   ├── → Spinner simple con \r y ANSI
  │   ├── → Barra de progreso ASCII
  │   ├── → Animación tipo Matrix (lluvia de caracteres)
  │   └── → Loop de renderizado con framerate fijo
  │
  ⑤ System info (neofetch-like)
  │   ├── → Leer info del sistema: OS, CPU, RAM, uptime
  │   ├── → Formatear con colores y ASCII art
  │   └── → Mostrar logo del OS en ASCII
  │
  ⑥ Herramientas propias
      ├── → Crear CLI completa con argparse / click
      ├── → Subcomandos, flags, opciones
      ├── → Empaquetar y distribuir (pip install)
      └── → Escribir man page o --help detallado
```

## 📚 Recursos

```
  Recursos
  ├── ANSI Escape Codes — referencia completa
  │   └── gist.github.com/fnky/458719343aabd01cfb17a3a4f7296797
  ├── Python docs — argparse, sys, os, signal
  ├── "The Linux Command Line" — William Shotts (libro)
  ├── pyfiglet — generador de ASCII art
  └── rich (Python) — librería para terminal bonita
```

## 🚀 Siguientes Pasos

```
  Después de dominar CLI Tools →
  ├── Rust CLI tools
  │   ├── clap (argument parsing)
  │   └── Herramientas: ripgrep, bat, fd, exa
  ├── Go CLI tools
  │   ├── cobra (framework de CLIs)
  │   └── Herramientas: fzf, lazygit, glow
  ├── ncurses
  │   ├── Librería C para interfaces en terminal
  │   └── Ventanas, paneles, entrada de teclado
  └── TUI Frameworks (interfaces de texto)
      ├── Textual (Python) — framework TUI moderno
      ├── Bubbletea (Go) — framework funcional TUI
      ├── Ratatui (Rust) — framework TUI
      └── Blessed / Ink (Node.js)
```

---

> **💡 Consejo:** La terminal es tu lienzo. Cada carácter es un píxel.
> Con códigos ANSI puedes crear interfaces sorprendentemente ricas.
> Empieza con algo simple (colorear texto) y ve subiendo de complejidad.
