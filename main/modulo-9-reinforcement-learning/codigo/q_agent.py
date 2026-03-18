"""
Módulo 9: Reinforcement Learning — Agente Q-Learning.

Implementa un agente que aprende a navegar GridWorldEnv usando el algoritmo
Q-Learning con la estrategia de exploración epsilon-greedy.

Solo usa la biblioteca estándar de Python (sin numpy, sin PyTorch).

Lore: Este es el cerebro del Explorador de Mundos. Con cada episodio aprende
más sobre el peligroso planeta alienígena, hasta dominar la ruta hacia la extracción.
"""

import random
from collections import defaultdict

from rl_environment import GridWorldEnv, _ACTION_SYMBOLS


class QLearningAgent:
    """
    Agente Q-Learning con estrategia epsilon-greedy.

    La Q-Table se almacena como un diccionario anidado:
      Q[estado][accion] = valor_float

    Se usa defaultdict para que los estados no visitados tengan valor 0
    sin necesidad de inicialización explícita.

    Ecuación de actualización (Bellman):
      Q(s,a) ← Q(s,a) + α · [r + γ · max_a' Q(s',a') - Q(s,a)]

    Estrategia epsilon-greedy:
      Con probabilidad ε  → acción aleatoria (exploración)
      Con probabilidad 1-ε → acción con mayor Q(s, ·) (explotación)
    """

    def __init__(
        self,
        n_actions: int = 4,
        learning_rate: float = 0.1,
        gamma: float = 0.99,
        epsilon: float = 1.0,
        epsilon_decay: float = 0.995,
        epsilon_min: float = 0.01,
        seed: int = 42,
    ) -> None:
        """
        Args:
            n_actions:     Número de acciones posibles.
            learning_rate: α — cuánto actualizar la Q-table en cada paso.
            gamma:         γ — factor de descuento para recompensas futuras.
            epsilon:       Probabilidad inicial de exploración.
            epsilon_decay: Factor multiplicativo para reducir ε tras cada episodio.
            epsilon_min:   Valor mínimo al que puede llegar ε.
            seed:          Semilla para reproducibilidad.
        """
        self.n_actions = n_actions
        self.lr = learning_rate
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        self._rng = random.Random(seed)

        # Q-Table: { estado → [Q(s,0), Q(s,1), Q(s,2), Q(s,3)] }
        # Inicializada a 0 para todos los estados no visitados.
        self.q_table: dict = defaultdict(lambda: [0.0] * n_actions)

    # ─── Política ─────────────────────────────────────────────────────────────

    def choose_action(self, state: tuple[int, int]) -> int:
        """
        Selecciona una acción usando la estrategia epsilon-greedy.

        Args:
            state: Estado actual del agente.

        Returns:
            Índice de la acción elegida (0=UP, 1=RIGHT, 2=DOWN, 3=LEFT).
        """
        if self._rng.random() < self.epsilon:
            return self._rng.randint(0, self.n_actions - 1)
        return self._best_action(state)

    def _best_action(self, state: tuple[int, int]) -> int:
        """Retorna la acción con mayor valor Q para el estado dado."""
        q_values = self.q_table[state]
        max_q = max(q_values)
        # Si hay empate, elegir entre las acciones igualmente buenas al azar
        best_actions = [a for a, q in enumerate(q_values) if q == max_q]
        return self._rng.choice(best_actions)

    # ─── Actualización Q ──────────────────────────────────────────────────────

    def update(
        self,
        state: tuple[int, int],
        action: int,
        reward: float,
        next_state: tuple[int, int],
        done: bool,
    ) -> None:
        """
        Actualiza la Q-table usando la ecuación de Bellman.

        Args:
            state:      Estado en el que se tomó la acción.
            action:     Acción tomada.
            reward:     Recompensa recibida.
            next_state: Estado resultante.
            done:       True si el episodio terminó.
        """
        current_q = self.q_table[state][action]

        if done:
            # No hay estado siguiente → el valor futuro es 0
            target = reward
        else:
            target = reward + self.gamma * max(self.q_table[next_state])

        # Actualización con tasa de aprendizaje
        self.q_table[state][action] = current_q + self.lr * (target - current_q)

    # ─── Entrenamiento ────────────────────────────────────────────────────────

    def train(
        self,
        env: GridWorldEnv,
        n_episodes: int = 1000,
        max_steps: int = 200,
    ) -> list[float]:
        """
        Entrena el agente en el entorno durante n_episodes episodios.

        Args:
            env:        Entorno GridWorld.
            n_episodes: Número de episodios de entrenamiento.
            max_steps:  Pasos máximos por episodio (evita bucles infinitos).

        Returns:
            Lista con la recompensa total de cada episodio.
        """
        episode_rewards: list[float] = []

        for _ in range(n_episodes):
            state, _ = env.reset()
            total_reward = 0.0

            for _ in range(max_steps):
                action = self.choose_action(state)
                next_state, reward, terminated, truncated, _ = env.step(action)
                done = terminated or truncated

                self.update(state, action, reward, next_state, done)

                total_reward += reward
                state = next_state

                if done:
                    break

            episode_rewards.append(total_reward)
            # Decaimiento de epsilon al final de cada episodio
            self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

        return episode_rewards

    # ─── Política aprendida ───────────────────────────────────────────────────

    def get_policy(self, env: GridWorldEnv) -> dict[tuple[int, int], int]:
        """
        Extrae la política greedy actual (la mejor acción para cada estado).

        Args:
            env: Entorno del que obtener todos los estados válidos.

        Returns:
            Diccionario { estado → mejor_acción }.
        """
        policy = {}
        for state in env.get_all_states():
            policy[state] = self._best_action(state)
        return policy

    def print_policy(self, env: GridWorldEnv) -> None:
        """Imprime la política aprendida sobre la cuadrícula."""
        from rl_environment import _WALL, _GOAL, _HAZARD

        policy = self.get_policy(env)
        _CELL_CHARS = {_WALL: "#", _GOAL: "G", _HAZARD: "X"}

        header = "  " + " ".join(str(c) for c in range(env.size))
        print(header)
        for r in range(env.size):
            row = []
            for c in range(env.size):
                cell = env._grid[r][c]
                if cell in _CELL_CHARS:
                    row.append(_CELL_CHARS[cell])
                else:
                    action = policy.get((r, c), 0)
                    row.append(_ACTION_SYMBOLS[action])
            print(f"{r}│" + " ".join(row))


# ─────────────────────────────────────────────────────────────────────────────
# DEMO
# ─────────────────────────────────────────────────────────────────────────────


def _moving_average(data: list[float], window: int = 50) -> list[float]:
    result = []
    for i in range(len(data)):
        start = max(0, i - window + 1)
        result.append(sum(data[start : i + 1]) / (i - start + 1))
    return result


if __name__ == "__main__":
    print("=" * 55)
    print("  MÓDULO 9 — El Explorador de Mundos: Q-Learning  ")
    print("=" * 55)

    env = GridWorldEnv(size=5, seed=42)
    agent = QLearningAgent(
        n_actions=4,
        learning_rate=0.1,
        gamma=0.99,
        epsilon=1.0,
        epsilon_decay=0.995,
        epsilon_min=0.01,
        seed=42,
    )

    print("\n🌍 Planeta alienígena (estado inicial):")
    env.reset()
    print(env.render())

    print("\n🤖 Entrenando el agente por 1000 episodios...")
    rewards = agent.train(env, n_episodes=1000, max_steps=200)

    first_100 = sum(rewards[:100]) / 100
    last_100 = sum(rewards[-100:]) / 100
    print(f"\n📊 Recompensa media — primeros 100 episodios: {first_100:.1f}")
    print(f"📊 Recompensa media — últimos 100 episodios:  {last_100:.1f}")
    print(f"📈 Mejora: {last_100 - first_100:+.1f} puntos")

    print("\n🗺  Política aprendida (mejor acción para cada celda):")
    agent.print_policy(env)

    print("\n🚀 Ejecutando un episodio con la política aprendida...")
    agent.epsilon = 0.0  # Modo explotación pura
    state, _ = env.reset()
    total = 0.0
    steps = 0
    for step in range(50):
        action = agent.choose_action(state)
        next_state, reward, terminated, truncated, _ = env.step(action)
        total += reward
        steps += 1
        print(f"  Paso {step + 1}: {state} → {_ACTION_SYMBOLS[action]} → {next_state} (r={reward:+.0f})")
        state = next_state
        if terminated or truncated:
            break

    print(f"\n✅ Recompensa total del episodio: {total:.0f} en {steps} pasos")
    print("\n¡Misión completa, Explorador! El planeta ha sido cartografiado. 🌌")
