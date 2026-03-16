#!/usr/bin/env python3
"""
Reto 1 — El Oráculo y el Mensajero (fortune | cowsay)
======================================================

Este script replica el famoso pipeline de Unix `fortune | cowsay`.
En sistemas Unix, el operador `|` (pipe) conecta la salida estándar (stdout)
de un programa con la entrada estándar (stdin) del siguiente. Así:

    $ ./fortune_cowsay.py --fortune-only | ./fortune_cowsay.py --cowsay-only

Esto demuestra cómo los programas pequeños de Unix se componen entre sí,
siguiendo la filosofía de "haz una cosa y hazla bien".

Conceptos clave:
- stdout (sys.stdout): flujo de salida estándar, donde print() escribe.
- stdin  (sys.stdin):  flujo de entrada estándar, de donde se lee al recibir pipes.
- pipe   (|):          conecta stdout de un proceso con stdin del siguiente.
"""

import json
import os
import random
import sys
import textwrap

# ──────────────────────────────────────────────
# Constantes: colores ANSI para dar vida al terminal
# Los códigos ANSI siguen el formato \033[<código>m
# ──────────────────────────────────────────────
COLORES = {
    "rojo":     "\033[91m",
    "verde":    "\033[92m",
    "amarillo": "\033[93m",
    "azul":     "\033[94m",
    "magenta":  "\033[95m",
    "cyan":     "\033[96m",
    "blanco":   "\033[97m",
}
RESET = "\033[0m"

# ──────────────────────────────────────────────
# Arte ASCII para cada personaje
# ──────────────────────────────────────────────
PERSONAJES = {
    "cow": (
        "        \\   ^__^\n"
        "         \\  (oo)\\_______\n"
        "            (__)\\       )\\/\\\n"
        "                ||----w |\n"
        "                ||     ||\n"
    ),
    "dragon": (
        "        \\          ____ /\n"
        '         \\   /\\  .-    "-.\n'
        "          \\ /--\\/ .     . \\\n"
        "            |   /   )     )\n"
        "            \\  |  _/    /|\n"
        "             \\ \\ (  __ / /\n"
        "              \\_/`-----' /\n"
        "                |  o  o  |\n"
        "                \\   __   /\n"
        "                 `------'\n"
    ),
    "wizard": (
        "        \\\n"
        "         \\     /\\\n"
        "          \\   /  \\\n"
        "              |  |\n"
        "             /|\\/|\\\n"
        "            /_||||_\\\n"
        "              |  |\n"
        "             /    \\\n"
        "            / ^  ^ \\\n"
        "           |  (__)  |\n"
        "            \\  --  /\n"
        "             '----'\n"
    ),
}

# Ancho máximo de la burbuja de texto
ANCHO_BURBUJA = 40


def _ruta_frases() -> str:
    """Calcula la ruta absoluta al archivo frases.json relativa al script."""
    directorio_script = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(directorio_script, "..", "..", "datos", "frases.json")


def fortune() -> str:
    """
    Lee frases.json y devuelve una frase aleatoria formateada.

    Retorna:
        Cadena con formato «"texto" — autor»
    """
    ruta = _ruta_frases()
    with open(ruta, "r", encoding="utf-8") as f:
        datos = json.load(f)

    frase = random.choice(datos["frases"])
    return f'"{frase["texto"]}"\n  — {frase["autor"]}'


def _construir_burbuja(mensaje: str) -> str:
    """
    Envuelve un mensaje en una burbuja de texto estilo cowsay.

    La burbuja tiene bordes superior e inferior y el texto se ajusta
    automáticamente al ancho máximo definido por ANCHO_BURBUJA usando
    textwrap, que es el módulo estándar de Python para formateo de texto.
    """
    lineas = []
    for parrafo in mensaje.split("\n"):
        lineas.extend(textwrap.wrap(parrafo, width=ANCHO_BURBUJA) or [""])

    ancho = max(len(linea) for linea in lineas) if lineas else ANCHO_BURBUJA

    burbuja = []
    burbuja.append(" " + "_" * (ancho + 2))

    if len(lineas) == 1:
        burbuja.append(f"< {lineas[0].ljust(ancho)} >")
    else:
        burbuja.append(f"/ {lineas[0].ljust(ancho)} \\")
        for linea in lineas[1:-1]:
            burbuja.append(f"| {linea.ljust(ancho)} |")
        burbuja.append(f"\\ {lineas[-1].ljust(ancho)} /")

    burbuja.append(" " + "-" * (ancho + 2))
    return "\n".join(burbuja)


def cowsay(message: str, character: str = "cow") -> str:
    """
    Genera el arte ASCII completo: burbuja de texto + personaje.

    Args:
        message:   Texto a mostrar en la burbuja.
        character: Nombre del personaje ("cow", "dragon", "wizard").

    Retorna:
        Cadena con la burbuja y el personaje coloreado.
    """
    if character not in PERSONAJES:
        character = "cow"

    burbuja = _construir_burbuja(message)

    # Elegir un color aleatorio para el personaje
    color = random.choice(list(COLORES.values()))
    arte = PERSONAJES[character]
    arte_coloreado = color + arte + RESET

    return burbuja + "\n" + arte_coloreado


def _mostrar_ayuda():
    """Muestra la ayuda del programa."""
    print(
        "Uso: fortune_cowsay.py [opciones]\n"
        "\n"
        "Opciones:\n"
        "  (sin argumentos)        fortune | cowsay combinados\n"
        "  --fortune-only          Solo imprime la frase (para usar con pipe)\n"
        "  --cowsay-only           Lee de stdin y muestra con personaje\n"
        "  --character <nombre>    Personaje: cow, dragon, wizard\n"
        "  --help                  Muestra esta ayuda\n"
        "\n"
        "Ejemplo de pipeline:\n"
        "  python fortune_cowsay.py --fortune-only | python fortune_cowsay.py --cowsay-only"
    )


def main():
    """
    Punto de entrada principal — gestiona los modos del CLI.

    Modos:
    1. Sin argumentos → fortune + cowsay juntos (modo por defecto).
    2. --fortune-only  → solo imprime la frase por stdout.
       Útil para: python fortune_cowsay.py --fortune-only | otro_programa
    3. --cowsay-only   → lee de stdin y muestra con personaje.
       Útil para: echo "Hola" | python fortune_cowsay.py --cowsay-only
    """
    args = sys.argv[1:]

    if "--help" in args:
        _mostrar_ayuda()
        return

    # Determinar el personaje elegido
    personaje = "cow"
    if "--character" in args:
        idx = args.index("--character")
        if idx + 1 < len(args):
            personaje = args[idx + 1]

    if "--fortune-only" in args:
        # Modo pipeline: solo imprimir la frase por stdout para que otro
        # programa la pueda leer desde su stdin.
        print(fortune())

    elif "--cowsay-only" in args:
        # Modo pipeline: leer desde stdin (lo que llega por el pipe)
        # sys.stdin.read() lee TODO lo que viene por el pipe hasta EOF.
        mensaje = sys.stdin.read().strip()
        if not mensaje:
            mensaje = "¡Moo! No me diste nada que decir."
        print(cowsay(mensaje, personaje))

    else:
        # Modo combinado: fortune | cowsay en un solo paso
        frase = fortune()
        print(cowsay(frase, personaje))


if __name__ == "__main__":
    main()
