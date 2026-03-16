# 🖥️ Módulo 7: The Terminal Playground — El Arte de los CLIs de Linux

> _"Eres un mago de la terminal, un hacker de la vieja escuela que domina el arte arcano de los flujos de datos. Tu terminal no es solo una herramienta — es un lienzo, un instrumento musical, un jardín. En este módulo, aprenderás las artes oscuras de los CLIs: cómo los datos fluyen como ríos entre programas, cómo pintar con colores invisibles sobre una pantalla negra, y cómo dar vida a criaturas ASCII que habitan en tu consola. Prepárate para transformar tu terminal en algo que ningún IDE podrá jamás replicar."_

---

## 📖 Inspiración

Este módulo está inspirado en dos fuentes principales:

1. **["The Art of Linux CLIs"](https://www.youtube.com/watch?v=KdoaiGTIBY4)** — Un vídeo que explora la belleza y el poder de las herramientas de línea de comandos en Linux. Desde `fortune | cowsay` hasta animaciones ASCII complejas, demuestra que la terminal es mucho más que un prompt negro con texto blanco.

2. **[Experiencia con Arch Linux](https://www.youtube.com/watch?v=uZDPXFQYz0Q)** — El viaje de instalar y personalizar Arch Linux desde cero, que obliga a entender cómo funciona realmente un sistema operativo y sus flujos de datos.

### 🎯 Objetivo

Aprender sobre **flujos de datos (streams)**, **manipulación de texto**, **códigos de escape ANSI** y **animaciones de terminal**, construyendo herramientas CLI reales e interactivas en Python.

---

## 🧠 Conceptos Técnicos Fundamentales

### 1. Piping (Tuberías) — La Filosofía Unix

El piping es el corazón de la filosofía Unix: **"Haz una cosa y hazla bien"**. Cada programa debe hacer una sola tarea, y el operador `|` (pipe) conecta la salida estándar (`stdout`) de un programa con la entrada estándar (`stdin`) del siguiente.

```
┌──────────────┐    pipe (|)    ┌──────────────┐    pipe (|)    ┌──────────────┐
│  Programa A  │───────────────▶│  Programa B  │───────────────▶│  Programa C  │
│              │   stdout → stdin│              │   stdout → stdin│              │
└──────────────┘                └──────────────┘                └──────────────┘
```

**Diagrama de File Descriptors (fd):**

```
                    ┌─────────────────────┐
   stdin  (fd 0) ──▶│                     │──▶ stdout (fd 1)
                    │   PROCESO / PROGRAMA │
                    │                     │──▶ stderr (fd 2)
                    └─────────────────────┘
```

- **fd 0 (stdin):** Entrada estándar — de dónde el programa lee datos (teclado por defecto).
- **fd 1 (stdout):** Salida estándar — donde el programa escribe sus resultados.
- **fd 2 (stderr):** Salida de error — donde el programa escribe mensajes de error.

**Ejemplo clásico:**

```bash
fortune | cowsay
```

```
 ________________________________________
/ El que no arriesga, no gana.           \
\ — Proverbio                            /
 ----------------------------------------
        \   ^__^
         \  (oo)\_______
            (__)\       )\/\
                ||----w |
                ||     ||
```

`fortune` genera una frase aleatoria (stdout) → el pipe `|` la redirige → `cowsay` la recibe (stdin) y la muestra dentro de una vaca ASCII (stdout).

**¿Por qué es poderoso?**

```bash
# Contar cuántos archivos .py hay en un proyecto
find . -name "*.py" | wc -l

# Buscar errores en logs y ordenarlos por frecuencia
cat /var/log/syslog | grep "ERROR" | sort | uniq -c | sort -rn | head -10

# Pipeline completo: generar, filtrar, transformar, contar
ps aux | grep python | awk '{print $2, $11}' | sort -k2
```

---

### 2. ANSI Escape Codes — Pintando la Terminal

Los códigos de escape ANSI permiten controlar colores, estilos y posición del cursor en la terminal. Todos comienzan con la secuencia de escape `\033[` (o equivalentemente `\x1b[` o `\e[`).

#### Tabla de Referencia Rápida — Colores

| Código | Color (Texto) | Código | Color (Fondo) |
|--------|---------------|--------|----------------|
| `\033[30m` | Negro | `\033[40m` | Negro |
| `\033[31m` | Rojo | `\033[41m` | Rojo |
| `\033[32m` | Verde | `\033[42m` | Verde |
| `\033[33m` | Amarillo | `\033[43m` | Amarillo |
| `\033[34m` | Azul | `\033[44m` | Azul |
| `\033[35m` | Magenta | `\033[45m` | Magenta |
| `\033[36m` | Cian | `\033[46m` | Cian |
| `\033[37m` | Blanco | `\033[47m` | Blanco |
| `\033[0m` | **Reset** | — | — |

#### Estilos de Texto

| Código | Efecto |
|--------|--------|
| `\033[1m` | **Negrita** |
| `\033[2m` | Tenue |
| `\033[3m` | _Cursiva_ |
| `\033[4m` | Subrayado |
| `\033[5m` | Parpadeo |
| `\033[7m` | Invertido |

#### Control del Cursor

| Código | Acción |
|--------|--------|
| `\033[H` | Mover cursor a la posición (0,0) — inicio |
| `\033[{n};{m}H` | Mover cursor a fila `n`, columna `m` |
| `\033[2J` | Limpiar toda la pantalla |
| `\033[K` | Limpiar desde el cursor hasta fin de línea |
| `\033[?25l` | Ocultar cursor |
| `\033[?25h` | Mostrar cursor |
| `\033[{n}A` | Mover cursor `n` líneas arriba |
| `\033[{n}B` | Mover cursor `n` líneas abajo |

**Ejemplo en Python:**

```python
# Texto rojo en negrita
print("\033[1;31m¡ALERTA! Algo salió mal.\033[0m")

# Fondo azul con texto blanco
print("\033[37;44m  Dashboard del Sistema  \033[0m")

# Limpiar pantalla y posicionar cursor
print("\033[2J\033[H", end="")  # Limpia y va al inicio
```

---

### 3. Signal Handling — Interceptando Señales del Sistema

Las señales son mecanismos de comunicación entre el sistema operativo y los procesos. Son fundamentales para crear CLIs robustos.

| Señal | Número | Disparada por | Acción por defecto |
|-------|--------|---------------|-------------------|
| `SIGINT` | 2 | `Ctrl+C` | Terminar proceso |
| `SIGTERM` | 15 | `kill PID` | Terminar proceso |
| `SIGKILL` | 9 | `kill -9 PID` | Terminar (no interceptable) |
| `SIGTSTP` | 20 | `Ctrl+Z` | Suspender proceso |
| `SIGWINCH` | 28 | Redimensionar terminal | — |

**Dato curioso:** El comando `sl` (locomotora que aparece cuando escribes mal `ls`) **intercepta SIGINT** para que no puedas cancelarlo con `Ctrl+C` — es parte de su castigo.

**Ejemplo en Python:**

```python
import signal
import sys

def manejador_salida(sig, frame):
    print("\n\033[33m¡No puedes escapar tan fácilmente!\033[0m")
    # Limpiar recursos antes de salir
    sys.exit(0)

# Registrar el manejador para SIGINT (Ctrl+C)
signal.signal(signal.SIGINT, manejador_salida)

# También podemos interceptar SIGTERM
signal.signal(signal.SIGTERM, manejador_salida)
```

---

### 4. Standard Streams — Redireccionamiento de Flujos

Cada proceso en Unix tiene tres flujos estándar. Podemos redirigirlos con operadores especiales:

```bash
# Redirigir stdout a un archivo (sobrescribe)
echo "Hola mundo" > salida.txt

# Redirigir stdout a un archivo (append / añadir)
echo "Línea nueva" >> salida.txt

# Redirigir stderr a un archivo
python3 script.py 2> errores.log

# Redirigir AMBOS (stdout + stderr) a un archivo
python3 script.py &> todo.log

# Redirigir stdout a un archivo Y stderr a otro
python3 script.py > salida.txt 2> errores.log

# Descartar stderr (enviarlo a /dev/null — el agujero negro)
python3 script.py 2>/dev/null

# Redirigir stderr a stdout (para que el pipe los capture ambos)
python3 script.py 2>&1 | grep "error"
```

**Diagrama de redirección:**

```
                              > archivo.txt     (stdout → archivo)
                             >> archivo.txt     (stdout → archivo, append)
  ┌─────────┐              2> errores.log      (stderr → archivo)
  │ Proceso  │─── stdout ──▶  | otro_programa  (stdout → stdin del siguiente)
  │          │─── stderr ──▶ 2>&1              (stderr → misma ruta que stdout)
  └─────────┘              &> todo.log         (ambos → archivo)
```

---

## 🏆 Retos del Módulo

| # | Reto | Concepto Clave | Descripción |
|---|------|----------------|-------------|
| 1 | **El Oráculo y el Mensajero** | Piping, JSON, arte ASCII | Clon moderno de `fortune \| cowsay`. Un programa genera frases sabias aleatorias desde un JSON y otro las envuelve en arte ASCII de un animal — conectados por pipes. |
| 2 | **El Castigador de Typos** | Señales, animación terminal | Locomotora ASCII estilo `sl` que cruza la terminal cuando cometes un error. Intercepta `SIGINT` para que no puedas cancelarla — debes esperar tu castigo completo. |
| 3 | **El Dashboard de Identidad** | Lectura de sistema, colores ANSI | Clon minimalista de `neofetch`: muestra info del sistema (OS, kernel, CPU, RAM, shell, uptime) con arte ASCII y colores, leyendo de `/proc` y variables de entorno. |
| 4 | **El Generador de Vida** | Recursividad, sleep, dibujo | Un bonsái ASCII que crece rama por rama en tu terminal, usando recursividad para generar las ramas y `time.sleep()` para animar el crecimiento en tiempo real. |

---

## 📁 Estructura de Carpetas

```
modulo-7-cli-terminal-playground/
├── README.md                          # ← Este archivo
├── guia-arch-uso/
│   └── guia-uso-arch.md               # Guía de uso diario de Arch Linux
├── reto-1-oraculo-mensajero/
│   ├── fortune_cowsay.py              # Programa principal (modo combinado)
│   ├── fortune.py                     # Generador de frases (stdout)
│   ├── cowsay.py                      # Envolvedor ASCII (stdin → stdout)
│   ├── frases.json                    # Base de datos de frases
│   └── README.md                      # Explicación del reto
├── reto-2-castigador-typos/
│   ├── sl.py                          # Locomotora ASCII animada
│   ├── trenes.py                      # Arte ASCII de los trenes
│   └── README.md
├── reto-3-dashboard-identidad/
│   ├── neofetch.py                    # Dashboard de sistema
│   ├── ascii_logos.py                 # Logos ASCII de distros
│   └── README.md
└── reto-4-generador-vida/
    ├── bonsai.py                      # Bonsái ASCII animado
    └── README.md
```

---

## 🚀 Cómo Ejecutar

### Reto 1 — El Oráculo y el Mensajero

```bash
# Modo combinado (fortune + cowsay en un solo comando)
python3 reto-1-oraculo-mensajero/fortune_cowsay.py

# Modo pipe — como la filosofía Unix manda
python3 reto-1-oraculo-mensajero/fortune_cowsay.py --fortune-only | python3 reto-1-oraculo-mensajero/fortune_cowsay.py --cowsay-only

# También puedes usarlo con otros programas
echo "Hola desde el pipe" | python3 reto-1-oraculo-mensajero/fortune_cowsay.py --cowsay-only
```

### Reto 2 — El Castigador de Typos

```bash
# Ejecutar la locomotora (intenta Ctrl+C... no funcionará 😈)
python3 reto-2-castigador-typos/sl.py

# Con variaciones
python3 reto-2-castigador-typos/sl.py --speed fast
python3 reto-2-castigador-typos/sl.py --ascii small
```

### Reto 3 — El Dashboard de Identidad

```bash
# Mostrar información del sistema con arte ASCII
python3 reto-3-dashboard-identidad/neofetch.py

# Elegir logo de distro específica
python3 reto-3-dashboard-identidad/neofetch.py --distro arch
```

### Reto 4 — El Generador de Vida

```bash
# Ver crecer un bonsái en tu terminal
python3 reto-4-generador-vida/bonsai.py

# Personalizar el crecimiento
python3 reto-4-generador-vida/bonsai.py --seed 42 --speed slow
```

---

## 🧙 Lore del Módulo

> _Eres un mago de la terminal, un hacker de la vieja escuela que domina el arte arcano de los flujos de datos._
>
> _Tu terminal no es solo una herramienta — es un lienzo, un instrumento musical, un jardín._
>
> _En este módulo, aprenderás las artes oscuras de los CLIs: cómo encadenar programas con tuberías para que los datos fluyan como agua entre ellos, cómo pintar con colores ANSI sobre la oscuridad de tu pantalla, cómo interceptar las señales del sistema operativo para doblar el tiempo a tu voluntad, y cómo dar vida a criaturas ASCII que crecen, se mueven y respiran dentro de tu consola._
>
> _Los GUI son para muggles. La terminal es donde vive la verdadera magia._
>
> _Cada reto de este módulo es un hechizo nuevo en tu grimorio. Al final, tu terminal será irreconocible — y tú serás el tipo de persona que otros miran con una mezcla de admiración y miedo cuando abres una ventana negra y empiezas a teclear._

---

## 📚 Recursos Adicionales

- [The Art of Linux CLIs (YouTube)](https://www.youtube.com/watch?v=KdoaiGTIBY4)
- [Experiencia con Arch Linux (YouTube)](https://www.youtube.com/watch?v=uZDPXFQYz0Q)
- [ANSI Escape Codes — Wikipedia](https://en.wikipedia.org/wiki/ANSI_escape_code)
- [Documentación de `signal` en Python](https://docs.python.org/3/library/signal.html)
- [The Unix Philosophy](https://en.wikipedia.org/wiki/Unix_philosophy)
- [Arch Wiki — General Recommendations](https://wiki.archlinux.org/title/General_recommendations)
