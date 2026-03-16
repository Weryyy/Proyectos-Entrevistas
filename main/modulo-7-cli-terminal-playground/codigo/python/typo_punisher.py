#!/usr/bin/env python3
"""
Reto 2 — El Castigador de Typos (clon de sl)
=============================================

El comando `sl` es una broma clásica de Unix: cuando escribes `sl` en vez de
`ls` (un typo muy común), aparece una locomotora de vapor cruzando tu terminal.
No puedes detenerla con Ctrl+C — ¡es tu castigo por el error tipográfico!

Conceptos clave:
- Secuencias de escape ANSI: códigos especiales que el terminal interpreta
  como instrucciones (mover cursor, borrar pantalla, cambiar color).
  • \033[2J   → borra toda la pantalla
  • \033[H    → mueve el cursor a la esquina superior izquierda
  • \033[nC   → mueve el cursor n columnas a la derecha
- Señales (signals): mecanismo del SO para comunicar eventos a un proceso.
  • SIGINT (señal 2) se envía al presionar Ctrl+C.
  • signal.signal(SIGINT, handler) nos permite interceptar la señal.
- shutil.get_terminal_size(): obtiene las dimensiones actuales del terminal.
"""

import os
import random
import signal
import shutil
import sys
import time

# ──────────────────────────────────────────────
# Colores ANSI para la locomotora y el humo
# ──────────────────────────────────────────────
COLOR_LOCOMOTORA = "\033[91m"  # Rojo
COLOR_HUMO = "\033[90m"        # Gris
COLOR_RUEDAS = "\033[93m"      # Amarillo
RESET = "\033[0m"

# ──────────────────────────────────────────────
# Frames de la locomotora — mínimo 4 frames para animación fluida.
# Cada frame es una lista de cadenas (líneas) que representan un estado
# de las ruedas en movimiento.
# ──────────────────────────────────────────────
FRAMES_LOCOMOTORA = [
    # Frame 0 — ruedas en posición base
    [
        "      ====        ________                 ",
        "  _D _|  |_______/        \\__I_I_____===__|",
        "   |(_)---  |   H\\________/ |   |        =|",
        "   /     |  |   H  |  |     |   |         |",
        "  |      |  |   H  |__----__|   |         |",
        "  | ________|___H__/__|_____/[][]~\\_____A  |",
        "  |/ |   |-----------I_____I [][] []  D   |]",
        "  __/ =| o |=-~~\\  /~~\\  /~~\\  /~~\\ ____Y_|",
        " |/-=|___|=    ||    ||    ||    |_____/~\\|",
        "  \\_/      \\O=====O=====O=====O_/      \\_/ ",
    ],
    # Frame 1 — ruedas rotando (posición 1)
    [
        "      ====        ________                 ",
        "  _D _|  |_______/        \\__I_I_____===__|",
        "   |(_)---  |   H\\________/ |   |        =|",
        "   /     |  |   H  |  |     |   |         |",
        "  |      |  |   H  |__----__|   |         |",
        "  | ________|___H__/__|_____/[][]~\\_____A  |",
        "  |/ |   |-----------I_____I [][] []  D   |]",
        "  __/ =| o |=-~~\\  /~~\\  /~~\\  /~~\\ ____Y_|",
        " |/-=|___|=   O=====O=====O=====O  |_/~\\| ",
        "  \\_/      \\_/      \\_/     \\_/     \\_/    ",
    ],
    # Frame 2 — ruedas rotando (posición 2)
    [
        "      ====        ________                 ",
        "  _D _|  |_______/        \\__I_I_____===__|",
        "   |(_)---  |   H\\________/ |   |        =|",
        "   /     |  |   H  |  |     |   |         |",
        "  |      |  |   H  |__----__|   |         |",
        "  | ________|___H__/__|_____/[][]~\\_____A  |",
        "  |/ |   |-----------I_____I [][] []  D   |]",
        "  __/ =| o |=-~~\\  /~~\\  /~~\\  /~~\\ ____Y_|",
        " |/-=|___|= O=====O=====O=====O=   |_/~\\| ",
        "  \\_/      \\_/     \\_/     \\_/    \\_/     \\",
    ],
    # Frame 3 — ruedas rotando (posición 3)
    [
        "      ====        ________                 ",
        "  _D _|  |_______/        \\__I_I_____===__|",
        "   |(_)---  |   H\\________/ |   |        =|",
        "   /     |  |   H  |  |     |   |         |",
        "  |      |  |   H  |__----__|   |         |",
        "  | ________|___H__/__|_____/[][]~\\_____A  |",
        "  |/ |   |-----------I_____I [][] []  D   |]",
        "  __/ =| o |=-~~\\  /~~\\  /~~\\  /~~\\ ____Y_|",
        " |/-=|___|=  O=====O=====O=====O   |_/~\\| ",
        "  \\_/      \\_/    \\_/     \\_/    \\_/      \\",
    ],
]

# Altura uniforme de todos los frames
FRAME_HEIGHT = len(FRAMES_LOCOMOTORA[0])
FRAME_WIDTH = max(len(linea) for frame in FRAMES_LOCOMOTORA for linea in frame)

# ──────────────────────────────────────────────
# Contador de Ctrl+C para la válvula de escape de seguridad.
# Permitimos salir después de 3 pulsaciones rápidas.
# ──────────────────────────────────────────────
_ctrl_c_count = 0
_ultimo_ctrl_c = 0.0


def _handler_sigint(signum, frame):
    """
    Manejador de la señal SIGINT (Ctrl+C).

    En Unix, cuando presionas Ctrl+C, el kernel envía la señal SIGINT
    al proceso en primer plano. Normalmente esto termina el programa,
    pero podemos interceptarla con signal.signal().

    Por seguridad, permitimos salir tras 3 Ctrl+C rápidos (en < 2 seg).
    """
    global _ctrl_c_count, _ultimo_ctrl_c

    ahora = time.time()
    if ahora - _ultimo_ctrl_c < 2.0:
        _ctrl_c_count += 1
    else:
        _ctrl_c_count = 1

    _ultimo_ctrl_c = ahora

    if _ctrl_c_count >= 3:
        # Restaurar terminal y salir limpiamente
        print(f"\033[{FRAME_HEIGHT + 5};1H{RESET}")
        print("¡Escapaste! Pero recuerda: ¡ls, no sl! 🚂")
        sys.exit(0)


def generar_humo(ancho_humo: int = 20) -> list:
    """
    Genera líneas de humo aleatorio encima de la locomotora.

    Usa caracteres ASCII que simulan partículas de vapor dispersándose.
    El humo se desplaza y difumina hacia arriba.
    """
    caracteres_humo = ["~", "*", "o", "O", ".", "'", "°", "·"]
    lineas = []
    for i in range(3):
        densidad = max(1, ancho_humo - i * 5)
        linea = ""
        for _ in range(densidad):
            if random.random() < 0.4:
                linea += random.choice(caracteres_humo)
            else:
                linea += " "
        lineas.append(linea)
    return lineas


def get_terminal_size():
    """
    Obtiene el tamaño del terminal.

    shutil.get_terminal_size() consulta el descriptor de archivo del terminal
    (usando ioctl TIOCGWINSZ en Linux) para obtener columnas y filas.
    Retorna un valor por defecto de (80, 24) si no puede determinarlo.
    """
    return shutil.get_terminal_size(fallback=(80, 24))


def animate(speed: float = 0.05):
    """
    Bucle principal de animación: la locomotora cruza de derecha a izquierda.

    Cada iteración:
    1. Se borra la pantalla con \033[2J\033[H
    2. Se calcula la posición horizontal de la locomotora
    3. Se genera humo aleatorio sobre la chimenea
    4. Se dibuja el frame actual con colores

    El frame de la locomotora alterna entre los 4 definidos para simular
    el movimiento de las ruedas (como un GIF).
    """
    columnas, filas = get_terminal_size()
    num_frames = len(FRAMES_LOCOMOTORA)

    # La locomotora empieza fuera de la pantalla (derecha) y sale por la izquierda
    posicion_inicio = columnas + 5
    posicion_fin = -(FRAME_WIDTH + 10)

    for pos in range(posicion_inicio, posicion_fin, -2):
        # Seleccionar frame actual (rotación cíclica para animar ruedas)
        frame_idx = ((posicion_inicio - pos) // 2) % num_frames
        frame = FRAMES_LOCOMOTORA[frame_idx]

        # Borrar pantalla: \033[2J borra todo, \033[H mueve cursor a (1,1)
        sys.stdout.write("\033[2J\033[H")

        # Generar y dibujar humo
        humo = generar_humo()
        for linea_humo in humo:
            desplazamiento = max(0, pos + 5)
            if desplazamiento < columnas:
                sys.stdout.write(
                    f"\033[{desplazamiento}C{COLOR_HUMO}{linea_humo}{RESET}\n"
                )
            else:
                sys.stdout.write("\n")

        # Dibujar la locomotora
        for i, linea in enumerate(frame):
            if pos >= 0:
                # La locomotora está parcial o totalmente en pantalla
                visible = linea[:columnas - pos] if pos < columnas else ""
                if visible:
                    color = COLOR_RUEDAS if i >= len(frame) - 2 else COLOR_LOCOMOTORA
                    sys.stdout.write(f"\033[{pos}C{color}{visible}{RESET}\n")
                else:
                    sys.stdout.write("\n")
            else:
                # La locomotora está saliendo por la izquierda
                recorte = abs(pos)
                if recorte < len(linea):
                    visible = linea[recorte:]
                    color = COLOR_RUEDAS if i >= len(frame) - 2 else COLOR_LOCOMOTORA
                    sys.stdout.write(f"{color}{visible}{RESET}\n")
                else:
                    sys.stdout.write("\n")

        sys.stdout.flush()
        time.sleep(speed)


if __name__ == "__main__":
    # Interceptar SIGINT (Ctrl+C) — el castigo no se detiene fácilmente.
    # signal.signal() registra una función que se ejecutará cuando llegue
    # la señal especificada, en lugar del comportamiento por defecto.
    signal.signal(signal.SIGINT, _handler_sigint)

    print("\033[?25l", end="")  # Ocultar cursor para animación limpia
    try:
        animate()
    finally:
        print("\033[?25h", end="")  # Restaurar cursor al terminar
        print(RESET)
