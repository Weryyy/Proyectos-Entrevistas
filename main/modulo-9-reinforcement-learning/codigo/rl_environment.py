"""
Módulo 9: Reinforcement Learning — Entorno GridWorld.

Implementa un entorno de cuadrícula NxN siguiendo el patrón de la API de Gymnasium
(reset, step, render). Es completamente determinista y solo usa la biblioteca estándar.

Lore: Eres un explorador IA enviado a un planeta alienígena. La cuadrícula representa
el terreno. Aprende a llegar al punto de extracción evitando las trampas de energía.
"""

import random
from typing import Optional


# Tipos de celda
_EMPTY = 0
_WALL = 1
_HAZARD = 2
_GOAL = 3
_START = 4

# Acciones
UP = 0
RIGHT = 1
DOWN = 2
LEFT = 3

_ACTION_DELTAS = {
    UP:    (-1,  0),
    RIGHT: ( 0,  1),
    DOWN:  ( 1,  0),
    LEFT:  ( 0, -1),
}

_ACTION_SYMBOLS = {UP: "↑", RIGHT: "→", DOWN: "↓", LEFT: "←"}

# Recompensas
_REWARD_GOAL = 100.0
_REWARD_HAZARD = -100.0
_REWARD_STEP = -1.0
_REWARD_WALL = -5.0


class GridWorldEnv:
    """
    Entorno de cuadrícula NxN con API estilo Gymnasium.

    El tablero tiene:
      - Una posición de inicio (S)
      - Una posición meta (G) → recompensa +100, episodio termina
      - Paredes (#) → el agente rebota, recompensa -5
      - Peligros (X) → recompensa -100, episodio termina
      - Celdas vacías → recompensa -1 por paso

    Estado: tupla (fila, columna)
    Acciones: 0=UP, 1=RIGHT, 2=DOWN, 3=LEFT

    Uso:
        env = GridWorldEnv(size=5, seed=42)
        state, info = env.reset()
        next_state, reward, terminated, truncated, info = env.step(action)
        print(env.render())
    """

    def __init__(self, size: int = 5, seed: int = 42) -> None:
        """
        Args:
            size: Dimensión de la cuadrícula (size × size).
            seed: Semilla para reproducibilidad del layout generado.
        """
        self.size = size
        self.seed = seed
        self._rng = random.Random(seed)

        # Generar el mapa
        self._grid = self._build_grid()
        self._start = self._find_cell(_START)
        self._goal = self._find_cell(_GOAL)

        # Estado actual del agente
        self._agent_pos: tuple[int, int] = self._start

        # Número de estados (para uso externo)
        self.n_states = size * size
        self.n_actions = 4

    # ─── Construcción del mapa ────────────────────────────────────────────────

    def _build_grid(self) -> list[list[int]]:
        """Construye una cuadrícula fija basada en el tamaño y la semilla."""
        n = self.size
        grid = [[_EMPTY] * n for _ in range(n)]

        # Inicio en la esquina superior izquierda
        grid[0][0] = _START
        # Meta en la esquina inferior derecha
        grid[n - 1][n - 1] = _GOAL

        if n >= 4:
            # Paredes fijas (diseño predeterminado para size≥4)
            walls = [
                (0, n - 2),
                (1, 1),
                (2, n - 2),
            ]
            for r, c in walls:
                if 0 <= r < n and 0 <= c < n and grid[r][c] == _EMPTY:
                    grid[r][c] = _WALL

            # Peligros fijos
            hazards = [
                (n - 2, 1),
                (n - 1, n - 2),
            ]
            for r, c in hazards:
                if 0 <= r < n and 0 <= c < n and grid[r][c] == _EMPTY:
                    grid[r][c] = _HAZARD
        elif n >= 3:
            grid[1][1] = _WALL
            grid[n - 1][1] = _HAZARD

        return grid

    def _find_cell(self, cell_type: int) -> tuple[int, int]:
        for r in range(self.size):
            for c in range(self.size):
                if self._grid[r][c] == cell_type:
                    return (r, c)
        raise ValueError(f"Celda de tipo {cell_type} no encontrada en el mapa.")

    # ─── API Gymnasium ────────────────────────────────────────────────────────

    def reset(self, seed: Optional[int] = None) -> tuple[tuple[int, int], dict]:
        """
        Reinicia el entorno al inicio de un episodio.

        Returns:
            state: Posición inicial del agente.
            info:  Diccionario con información adicional (vacío).
        """
        if seed is not None:
            self._rng = random.Random(seed)
        self._agent_pos = self._start
        return self._agent_pos, {}

    def step(
        self, action: int
    ) -> tuple[tuple[int, int], float, bool, bool, dict]:
        """
        Ejecuta una acción en el entorno.

        Args:
            action: Una de las constantes UP=0, RIGHT=1, DOWN=2, LEFT=3.

        Returns:
            next_state:  Nueva posición del agente.
            reward:      Recompensa recibida.
            terminated:  True si el episodio terminó (meta o peligro).
            truncated:   Siempre False (sin límite de pasos en la implementación base).
            info:        Diccionario con la acción ejecutada.
        """
        dr, dc = _ACTION_DELTAS[action]
        r, c = self._agent_pos
        nr, nc = r + dr, c + dc

        # ¿El movimiento choca con una pared o sale del mapa?
        if not (0 <= nr < self.size and 0 <= nc < self.size) or self._grid[nr][nc] == _WALL:
            return self._agent_pos, _REWARD_WALL, False, False, {"action": action}

        # Mover al agente
        self._agent_pos = (nr, nc)
        cell = self._grid[nr][nc]

        if cell == _GOAL:
            return self._agent_pos, _REWARD_GOAL, True, False, {"action": action}

        if cell == _HAZARD:
            return self._agent_pos, _REWARD_HAZARD, True, False, {"action": action}

        return self._agent_pos, _REWARD_STEP, False, False, {"action": action}

    def render(self) -> str:
        """
        Devuelve una representación ASCII del estado actual del entorno.

        Símbolos:
          S = inicio, G = meta, X = peligro, # = pared
          E = agente (explorador), · = celda vacía
        """
        _CELL_CHARS = {
            _EMPTY:  "·",
            _WALL:   "#",
            _HAZARD: "X",
            _GOAL:   "G",
            _START:  "S",
        }

        lines = []
        header = "  " + " ".join(str(c) for c in range(self.size))
        lines.append(header)
        lines.append("  " + "─" * (self.size * 2 - 1))

        for r in range(self.size):
            row_chars = []
            for c in range(self.size):
                if (r, c) == self._agent_pos and self._grid[r][c] not in (_GOAL, _HAZARD):
                    row_chars.append("E")
                else:
                    row_chars.append(_CELL_CHARS[self._grid[r][c]])
            lines.append(f"{r}│" + " ".join(row_chars))

        return "\n".join(lines)

    # ─── Utilidades ──────────────────────────────────────────────────────────

    def state_to_index(self, state: tuple[int, int]) -> int:
        """Convierte un estado (fila, col) a un índice entero para la Q-table."""
        return state[0] * self.size + state[1]

    def get_all_states(self) -> list[tuple[int, int]]:
        """Retorna todos los estados posibles (excluye paredes)."""
        return [
            (r, c)
            for r in range(self.size)
            for c in range(self.size)
            if self._grid[r][c] != _WALL
        ]


if __name__ == "__main__":
    env = GridWorldEnv(size=5, seed=42)
    state, _ = env.reset()
    print("Estado inicial del planeta alienígena:")
    print(env.render())
    print(f"\nAgente en: {state}")

    print("\nEjecutando acciones de ejemplo: →, ↓, →, ↓")
    for action in [RIGHT, DOWN, RIGHT, DOWN]:
        state, reward, terminated, truncated, _ = env.step(action)
        print(f"  Acción: {_ACTION_SYMBOLS[action]} → Estado: {state}, Recompensa: {reward}")
        if terminated:
            print("  ¡Episodio terminado!")
            break

    print("\nEstado final:")
    print(env.render())
