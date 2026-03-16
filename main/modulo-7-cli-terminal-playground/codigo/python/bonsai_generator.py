#!/usr/bin/env python3
"""
Reto 4 — El Generador de Vida (generador de bonsái ASCII)
==========================================================

Este programa genera un bonsái procedural usando recursión y lo anima
en el terminal. Cada ejecución produce un árbol único gracias a la
aleatoriedad controlada.

Conceptos clave:
- Recursión: la función grow() se llama a sí misma para crear ramas.
  Cada llamada reduce la longitud, creando un patrón fractal natural.
  La base de la recursión es cuando la longitud llega a 0 o nos salimos
  de los límites de la cuadrícula.
- Cuadrícula 2D: representamos el terminal como una matriz de caracteres.
  Esto nos permite "dibujar" en cualquier posición sin preocuparnos del
  orden de impresión — al final recorremos la cuadrícula fila por fila.
- Animación en terminal: redibujar la pantalla rápidamente crea la
  ilusión de movimiento. Borramos con \033[2J\033[H y redibujamos.
"""

import os
import random
import sys
import time

# ──────────────────────────────────────────────
# Colores ANSI para las partes del árbol
# ──────────────────────────────────────────────
RESET = "\033[0m"
COLOR_TRONCO = "\033[33m"      # Marrón/amarillo oscuro
COLOR_RAMA = "\033[33m"        # Marrón
COLOR_HOJA = "\033[92m"        # Verde brillante
COLOR_HOJA_ALT = "\033[32m"    # Verde oscuro
COLOR_FLOR = "\033[95m"        # Magenta (flores)
COLOR_MACETA = "\033[91m"      # Terracota/rojo
COLOR_TIERRA = "\033[33m"      # Marrón
BOLD = "\033[1m"

# Caracteres para cada parte del árbol
CHAR_TRONCO = "|"
CHAR_RAMA_IZQ = "/"
CHAR_RAMA_DER = "\\"
CHAR_HOJA = "&"
CHAR_HOJA_ALT = "*"
CHAR_FLOR = "@"


class BonsaiTree:
    """
    Representa un bonsái que crece en una cuadrícula 2D de caracteres.

    La cuadrícula es una lista de listas donde cada celda puede contener
    un carácter y su tipo (para colorear después). Coordenadas:
    - x: columna (0 = izquierda)
    - y: fila (0 = arriba, height-1 = abajo)
    """

    def __init__(self, width: int = 80, height: int = 24):
        """
        Inicializa la cuadrícula vacía.

        Args:
            width:  Ancho en columnas del área de dibujo.
            height: Alto en filas del área de dibujo.
        """
        self.width = width
        self.height = height
        # Cada celda almacena (carácter, tipo) donde tipo determina el color
        self.grid = [[(" ", "vacio") for _ in range(width)] for _ in range(height)]
        # Registro de puntas de ramas para colocar hojas después
        self.puntas_ramas = []
        # Lista de pasos para animación
        self.pasos_animacion = []

    def _en_limites(self, x: int, y: int) -> bool:
        """Verifica si una coordenada está dentro de la cuadrícula."""
        return 0 <= x < self.width and 0 <= y < self.height

    def _colocar(self, x: int, y: int, char: str, tipo: str):
        """
        Coloca un carácter en la cuadrícula si está dentro de los límites.

        También registra el paso para la animación incremental.
        """
        if self._en_limites(x, y):
            self.grid[y][x] = (char, tipo)
            self.pasos_animacion.append((x, y, char, tipo))

    def grow(self, x: int, y: int, direction: str, length: int,
             branch_char: str = CHAR_TRONCO):
        """
        Hace crecer una rama recursivamente.

        Esta es la función central del algoritmo. Cada llamada:
        1. Verifica la base de la recursión (length <= 0 o fuera de límites).
        2. Coloca un carácter en la posición actual.
        3. Avanza en la dirección indicada.
        4. Con cierta probabilidad, crea ramificaciones laterales.

        La recursión crea un patrón fractal similar a un árbol real:
        las ramas se hacen más cortas y finas conforme nos alejamos del tronco.

        Args:
            x:           Columna actual.
            y:           Fila actual.
            direction:   "up", "left", "right" — hacia dónde crece.
            length:      Longitud restante de esta rama.
            branch_char: Carácter a usar para dibujar.
        """
        # Base de la recursión: no más crecimiento
        if length <= 0:
            self.puntas_ramas.append((x, y))
            return

        if not self._en_limites(x, y):
            return

        # Determinar el carácter y tipo según la dirección
        if direction == "up":
            char = branch_char
            tipo = "tronco" if length > 3 else "rama"
        elif direction == "left":
            char = CHAR_RAMA_IZQ
            tipo = "rama"
        elif direction == "right":
            char = CHAR_RAMA_DER
            tipo = "rama"
        else:
            char = branch_char
            tipo = "rama"

        self._colocar(x, y, char, tipo)

        # Calcular siguiente posición según la dirección
        if direction == "up":
            ny = y - 1
            nx = x
        elif direction == "left":
            ny = y - 1
            nx = x - 1
        elif direction == "right":
            ny = y - 1
            nx = x + 1
        else:
            ny = y - 1
            nx = x

        # Continuar creciendo en la misma dirección (llamada recursiva)
        self.grow(nx, ny, direction, length - 1, branch_char)

        # Probabilidad de ramificación — decrece con la longitud restante.
        # Esto crea ramas más densas cerca del tronco y más escasas arriba.
        prob_ramificar = min(0.5, length * 0.06)

        if direction == "up" and length > 2:
            # El tronco puede ramificarse a izquierda y/o derecha
            if random.random() < prob_ramificar:
                largo_rama = max(1, length // 2 + random.randint(-1, 1))
                self.grow(x - 1, y - 1, "left", largo_rama)

            if random.random() < prob_ramificar:
                largo_rama = max(1, length // 2 + random.randint(-1, 1))
                self.grow(x + 1, y - 1, "right", largo_rama)

        elif direction == "left" and length > 1:
            # Las ramas izquierdas pueden sub-ramificarse
            if random.random() < prob_ramificar * 0.7:
                self.grow(nx, ny, "up", max(1, length - 2))

        elif direction == "right" and length > 1:
            if random.random() < prob_ramificar * 0.7:
                self.grow(nx, ny, "up", max(1, length - 2))

    def add_leaves(self):
        """
        Añade hojas coloreadas cerca de las puntas de las ramas.

        Recorre las puntas registradas durante grow() y coloca caracteres
        de hoja en posiciones adyacentes aleatorias. Usa diferentes
        caracteres y colores para dar variedad visual.
        """
        for px, py in self.puntas_ramas:
            # Colocar hojas en un radio de 1-2 celdas alrededor de la punta
            for _ in range(random.randint(2, 5)):
                dx = random.randint(-2, 2)
                dy = random.randint(-2, 1)
                lx, ly = px + dx, py + dy

                if self._en_limites(lx, ly) and self.grid[ly][lx][1] == "vacio":
                    if random.random() < 0.1:
                        self._colocar(lx, ly, CHAR_FLOR, "flor")
                    elif random.random() < 0.5:
                        self._colocar(lx, ly, CHAR_HOJA, "hoja")
                    else:
                        self._colocar(lx, ly, CHAR_HOJA_ALT, "hoja_alt")

    def add_pot(self):
        """
        Dibuja un macetero en la parte inferior central de la cuadrícula.

        El macetero se dibuja con caracteres de borde y se rellena,
        creando una forma trapezoidal típica de una maceta de bonsái.
        """
        centro = self.width // 2
        fila_base = self.height - 1
        fila_borde_sup = self.height - 3
        fila_medio = self.height - 2

        # Borde superior del macetero (más ancho)
        ancho_sup = 10
        for i in range(-ancho_sup // 2, ancho_sup // 2 + 1):
            x = centro + i
            if self._en_limites(x, fila_borde_sup):
                if i == -ancho_sup // 2 or i == ancho_sup // 2:
                    self._colocar(x, fila_borde_sup, "|", "maceta")
                else:
                    self._colocar(x, fila_borde_sup, "=", "maceta")

        # Cuerpo del macetero
        ancho_medio = 8
        for i in range(-ancho_medio // 2, ancho_medio // 2 + 1):
            x = centro + i
            if self._en_limites(x, fila_medio):
                if i == -ancho_medio // 2 or i == ancho_medio // 2:
                    self._colocar(x, fila_medio, "|", "maceta")
                else:
                    self._colocar(x, fila_medio, "~", "tierra")

        # Base del macetero (más estrecho — forma trapezoidal)
        ancho_base = 6
        for i in range(-ancho_base // 2, ancho_base // 2 + 1):
            x = centro + i
            if self._en_limites(x, fila_base):
                if i == -ancho_base // 2 or i == ancho_base // 2:
                    self._colocar(x, fila_base, "|", "maceta")
                else:
                    self._colocar(x, fila_base, "_", "maceta")

    def render(self) -> str:
        """
        Convierte la cuadrícula 2D en una cadena coloreada para imprimir.

        Recorre la cuadrícula fila por fila, aplicando el color ANSI
        correspondiente según el tipo de cada celda.
        """
        mapa_colores = {
            "vacio":    "",
            "tronco":   BOLD + COLOR_TRONCO,
            "rama":     COLOR_RAMA,
            "hoja":     BOLD + COLOR_HOJA,
            "hoja_alt": COLOR_HOJA_ALT,
            "flor":     BOLD + COLOR_FLOR,
            "maceta":   BOLD + COLOR_MACETA,
            "tierra":   COLOR_TIERRA,
        }

        lineas = []
        for fila in self.grid:
            linea = ""
            for char, tipo in fila:
                color = mapa_colores.get(tipo, "")
                if color:
                    linea += color + char + RESET
                else:
                    linea += char
            lineas.append(linea)

        return "\n".join(lineas)

    def animate(self, delay: float = 0.1):
        """
        Muestra el crecimiento del árbol paso a paso.

        Cada paso de la animación añade unos cuantos caracteres nuevos,
        redibuja la pantalla completa y espera un breve intervalo.
        Esto crea la ilusión de un árbol creciendo orgánicamente.

        La técnica de "borrar y redibujar" es la base de toda animación
        en terminal: no podemos actualizar celdas individuales de forma
        eficiente, así que redibujamos todo el frame cada vez.
        """
        mapa_colores = {
            "vacio":    "",
            "tronco":   BOLD + COLOR_TRONCO,
            "rama":     COLOR_RAMA,
            "hoja":     BOLD + COLOR_HOJA,
            "hoja_alt": COLOR_HOJA_ALT,
            "flor":     BOLD + COLOR_FLOR,
            "maceta":   BOLD + COLOR_MACETA,
            "tierra":   COLOR_TIERRA,
        }

        # Crear cuadrícula vacía para animación progresiva
        grid_animado = [[(" ", "vacio") for _ in range(self.width)]
                        for _ in range(self.height)]

        # Agrupar pasos en bloques para que la animación no sea demasiado lenta
        paso_bloque = max(1, len(self.pasos_animacion) // 40)

        for i, (x, y, char, tipo) in enumerate(self.pasos_animacion):
            grid_animado[y][x] = (char, tipo)

            # Redibujar cada N pasos
            if i % paso_bloque == 0 or i == len(self.pasos_animacion) - 1:
                sys.stdout.write("\033[2J\033[H")
                for fila in grid_animado:
                    linea = ""
                    for c, t in fila:
                        color = mapa_colores.get(t, "")
                        if color:
                            linea += color + c + RESET
                        else:
                            linea += c
                    sys.stdout.write(linea + "\n")
                sys.stdout.flush()
                time.sleep(delay)


def crear_bonsai(width: int = 70, height: int = 22) -> BonsaiTree:
    """
    Crea un bonsái completo con tronco, ramas, hojas y maceta.

    El proceso es:
    1. Crear la cuadrícula vacía.
    2. Añadir el macetero en la base.
    3. Hacer crecer el tronco desde el centro-abajo hacia arriba.
    4. Añadir hojas en las puntas de las ramas.
    """
    arbol = BonsaiTree(width, height)

    # Primero el macetero (para que el tronco crezca "desde" él)
    arbol.add_pot()

    # El tronco empieza justo encima del macetero, en el centro
    centro_x = width // 2
    base_y = height - 4  # Justo encima del macetero

    # Altura del tronco — proporcional a la altura de la cuadrícula
    altura_tronco = height // 2 + random.randint(-2, 2)

    arbol.grow(centro_x, base_y, "up", altura_tronco, CHAR_TRONCO)

    # Añadir follaje
    arbol.add_leaves()

    return arbol


if __name__ == "__main__":
    # Demo: generar y animar un bonsái
    print("\033[?25l", end="")  # Ocultar cursor
    try:
        arbol = crear_bonsai()
        arbol.animate(delay=0.08)

        # Mostrar el resultado final unos segundos
        time.sleep(2)

        # Versión final estática con mensaje
        sys.stdout.write("\033[2J\033[H")
        print(arbol.render())
        print(f"\n{BOLD}{COLOR_HOJA}  🌳 Tu bonsái ha crecido. "
              f"Cada ejecución genera uno único.{RESET}")
    finally:
        print("\033[?25h", end="")  # Restaurar cursor
