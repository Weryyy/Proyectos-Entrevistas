#!/usr/bin/env python3
"""
Reto 3 — El Dashboard de Identidad (clon de neofetch)
======================================================

Neofetch es una herramienta de línea de comandos que muestra información
del sistema junto a un logo ASCII del sistema operativo. Este clon
demuestra cómo obtener información del sistema usando solo la biblioteca
estándar de Python y el sistema de archivos virtual /proc de Linux.

En Linux, /proc es un sistema de archivos virtual que expone información
del kernel en forma de archivos de texto:
  - /proc/cpuinfo  → información del procesador
  - /proc/meminfo  → uso de memoria
  - /proc/uptime   → tiempo encendido en segundos

Conceptos clave:
- platform: módulo estándar para info del sistema portátil entre SOs.
- os.environ: diccionario con las variables de entorno del proceso.
- ANSI escape codes: para colores y posicionamiento en terminal.
"""

import getpass
import os
import platform
import sys

# ──────────────────────────────────────────────
# Colores ANSI
# ──────────────────────────────────────────────
RESET = "\033[0m"
BOLD = "\033[1m"

# Colores para etiquetas y valores
COLOR_LABEL = "\033[96m"   # Cyan brillante
COLOR_VALOR = "\033[97m"   # Blanco brillante
COLOR_TITULO = "\033[93m"  # Amarillo brillante
COLOR_LINEA = "\033[90m"   # Gris

# Colores para logos
COLOR_ARCH = "\033[96m"     # Cyan
COLOR_PYTHON = "\033[93m"   # Amarillo
COLOR_DEFAULT = "\033[97m"  # Blanco


# ──────────────────────────────────────────────
# Logos ASCII — cada uno tiene un color asociado
# ──────────────────────────────────────────────
ASCII_LOGOS = {
    "arch": (COLOR_ARCH, [
        "        /\\         ",
        "       /  \\        ",
        "      /\\   \\       ",
        "     /  .. \\\\      ",
        "    /  .    \\\\     ",
        "   / :.      \\\\   ",
        "  /..          \\\\ ",
        " /              \\\\",
        "/.........    ...\\",
        "               \\/ ",
    ]),
    "python": (COLOR_PYTHON, [
        "     ___            ",
        "    / _ \\     |     ",
        "   | |_| |  __|__   ",
        "   |  ___/ |  |  |  ",
        "   | |     |  |  |  ",
        "   |_|     |__|__|  ",
        "    ___    /  /     ",
        "   /   \\  /  /      ",
        "  |     |/  /       ",
        "   \\___/  \\/        ",
    ]),
    "default": (COLOR_DEFAULT, [
        "       _nnnn_       ",
        "      dGGGGMMb      ",
        "     @p~qp~~qMb     ",
        "     M|@||@) M|     ",
        "     @,----.JM|     ",
        "    JS^\\__/  qKL    ",
        "   dZP        qKRb  ",
        "  dZP          qKKb ",
        " fZP            SMMb",
        " HZM            MMMM",
        " FqM            MMMM",
        " __| \".        |\\dS\"",
        " |    `.       | `' ",
        " |      ;.___.'|    ",
        " |_____/        \\__ ",
    ]),
}


def _leer_archivo(ruta: str) -> str:
    """Lee un archivo de texto completo, retorna cadena vacía si falla."""
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            return f.read()
    except (OSError, IOError):
        return ""


def _obtener_os() -> str:
    """
    Obtiene el nombre del sistema operativo.

    En Linux, /etc/os-release contiene información como PRETTY_NAME.
    Si no existe, usamos platform.system() como respaldo.
    """
    try:
        contenido = _leer_archivo("/etc/os-release")
        if contenido:
            for linea in contenido.splitlines():
                if linea.startswith("PRETTY_NAME="):
                    return linea.split("=", 1)[1].strip('"')
    except Exception:
        pass
    return platform.system() + " " + platform.release()


def _obtener_uptime() -> str:
    """
    Obtiene el tiempo de actividad del sistema.

    En Linux, /proc/uptime contiene dos números:
    - Primer valor: segundos desde el arranque del sistema.
    - Segundo valor: tiempo idle acumulado de todos los CPUs.
    """
    try:
        contenido = _leer_archivo("/proc/uptime")
        if contenido:
            segundos = float(contenido.split()[0])
            horas = int(segundos // 3600)
            minutos = int((segundos % 3600) // 60)
            return f"{horas}h {minutos}m"
    except Exception:
        pass
    return "N/A"


def _obtener_cpu() -> str:
    """
    Obtiene el nombre del procesador.

    En Linux, /proc/cpuinfo lista información de cada núcleo.
    Buscamos la línea 'model name' que contiene el nombre comercial.
    """
    try:
        contenido = _leer_archivo("/proc/cpuinfo")
        if contenido:
            for linea in contenido.splitlines():
                if "model name" in linea:
                    return linea.split(":", 1)[1].strip()
    except Exception:
        pass

    proc = platform.processor()
    return proc if proc else "N/A"


def _obtener_memoria() -> str:
    """
    Obtiene información de memoria RAM.

    /proc/meminfo expone MemTotal y MemAvailable (entre otros) en kB.
    Calculamos la memoria usada como Total - Available.
    """
    try:
        contenido = _leer_archivo("/proc/meminfo")
        if contenido:
            mem_total = 0
            mem_disponible = 0
            for linea in contenido.splitlines():
                if linea.startswith("MemTotal:"):
                    mem_total = int(linea.split()[1])
                elif linea.startswith("MemAvailable:"):
                    mem_disponible = int(linea.split()[1])
            if mem_total > 0:
                mem_usada = mem_total - mem_disponible
                total_mb = mem_total // 1024
                usada_mb = mem_usada // 1024
                return f"{usada_mb} MiB / {total_mb} MiB"
    except Exception:
        pass
    return "N/A"


def get_system_info() -> dict:
    """
    Recopila toda la información del sistema en un diccionario.

    Cada campo se obtiene con su propia función que maneja errores
    internamente, retornando "N/A" si algo falla. Esto asegura que
    el dashboard siempre se muestre, aunque falte algún dato.
    """
    return {
        "os": _obtener_os(),
        "kernel": platform.release(),
        "uptime": _obtener_uptime(),
        "shell": os.environ.get("SHELL", "N/A"),
        "cpu": _obtener_cpu(),
        "memory": _obtener_memoria(),
        "hostname": platform.node(),
        "user": os.environ.get("USER", getpass.getuser()),
    }


def color_bar() -> str:
    """
    Genera una barra de colores usando los 8 colores estándar ANSI.

    Los códigos 40-47 son colores de fondo estándar.
    Usamos el carácter de bloque completo (█) para mostrar cada color.
    También incluimos los colores brillantes (100-107).
    """
    barra = ""
    # Colores normales (40-47)
    for code in range(40, 48):
        barra += f"\033[{code}m   "
    barra += RESET + "\n"
    # Colores brillantes (100-107)
    for code in range(100, 108):
        barra += f"\033[{code}m   "
    barra += RESET
    return barra


def render_dashboard(info: dict, logo_name: str = "default") -> str:
    """
    Renderiza el dashboard con el logo a la izquierda y la info a la derecha.

    El diseño imita a neofetch: logo ASCII coloreado en la columna izquierda
    y datos del sistema alineados en la columna derecha.
    """
    if logo_name not in ASCII_LOGOS:
        logo_name = "default"

    color_logo, lineas_logo = ASCII_LOGOS[logo_name]

    # Preparar las líneas de información del sistema
    titulo = f"{BOLD}{COLOR_TITULO}{info['user']}@{info['hostname']}{RESET}"
    separador = f"{COLOR_LINEA}{'-' * (len(info['user']) + len(info['hostname']) + 1)}{RESET}"

    campos = [
        ("OS", info["os"]),
        ("Kernel", info["kernel"]),
        ("Uptime", info["uptime"]),
        ("Shell", info["shell"]),
        ("CPU", info["cpu"]),
        ("Memory", info["memory"]),
    ]

    lineas_info = [titulo, separador]
    for etiqueta, valor in campos:
        lineas_info.append(
            f"{BOLD}{COLOR_LABEL}{etiqueta}: {RESET}{COLOR_VALOR}{valor}{RESET}"
        )
    lineas_info.append("")
    lineas_info.append(color_bar())

    # Calcular el ancho del logo para alineación
    ancho_logo = max(len(linea) for linea in lineas_logo) + 4

    # Combinar logo e info lado a lado
    max_lineas = max(len(lineas_logo), len(lineas_info))
    resultado = []

    for i in range(max_lineas):
        # Columna izquierda: logo
        if i < len(lineas_logo):
            parte_logo = f"{color_logo}{lineas_logo[i]}{RESET}"
            # Calcular padding sin contar códigos ANSI
            padding = ancho_logo - len(lineas_logo[i])
        else:
            parte_logo = ""
            padding = ancho_logo

        # Columna derecha: info del sistema
        parte_info = lineas_info[i] if i < len(lineas_info) else ""

        resultado.append(f"  {parte_logo}{' ' * padding}{parte_info}")

    return "\n".join(resultado)


def main():
    """Punto de entrada: parsea argumentos y muestra el dashboard."""
    args = sys.argv[1:]
    logo = "default"

    if "--logo" in args:
        idx = args.index("--logo")
        if idx + 1 < len(args):
            logo = args[idx + 1]

    if "--help" in args:
        print(
            "Uso: neofetch_clone.py [--logo arch|python|default]\n"
            "\n"
            "Muestra información del sistema con un logo ASCII."
        )
        return

    info = get_system_info()
    print(render_dashboard(info, logo))


if __name__ == "__main__":
    main()
