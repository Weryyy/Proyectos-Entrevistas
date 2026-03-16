"""
Tests para el Módulo 9: Reinforcement Learning.

Cubre el entorno GridWorld y el agente Q-Learning.

Ejecutar con:
    pytest test_rl.py -v
"""

import pytest
import random

from rl_environment import (
    GridWorldEnv,
    UP,
    RIGHT,
    DOWN,
    LEFT,
    _GOAL,
    _HAZARD,
    _WALL,
    _REWARD_GOAL,
    _REWARD_HAZARD,
    _REWARD_STEP,
    _REWARD_WALL,
)
from q_agent import QLearningAgent


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────


@pytest.fixture
def env():
    return GridWorldEnv(size=5, seed=42)


@pytest.fixture
def agent():
    return QLearningAgent(
        n_actions=4,
        learning_rate=0.1,
        gamma=0.99,
        epsilon=0.0,  # Explotación pura para tests deterministas
        seed=0,
    )


# ─────────────────────────────────────────────────────────────────────────────
# TESTS DEL ENTORNO
# ─────────────────────────────────────────────────────────────────────────────


class TestGridWorldEnv:
    def test_reset_retorna_estado_valido(self, env):
        state, info = env.reset()
        assert isinstance(state, tuple)
        assert len(state) == 2
        r, c = state
        assert 0 <= r < env.size
        assert 0 <= c < env.size

    def test_reset_retorna_posicion_inicio(self, env):
        """El agente siempre empieza en (0, 0)."""
        state, _ = env.reset()
        assert state == (0, 0)

    def test_reset_info_es_diccionario(self, env):
        _, info = env.reset()
        assert isinstance(info, dict)

    def test_step_retorna_cinco_valores(self, env):
        env.reset()
        resultado = env.step(RIGHT)
        assert len(resultado) == 5
        next_state, reward, terminated, truncated, info = resultado
        assert isinstance(next_state, tuple)
        assert isinstance(reward, float)
        assert isinstance(terminated, bool)
        assert isinstance(truncated, bool)
        assert isinstance(info, dict)

    def test_accion_up_mueve_arriba(self, env):
        """Desde (1,0) moverse UP debe llevar a (0,0)."""
        env.reset()
        # Moverse DOWN para llegar a (1,0)
        env.step(DOWN)
        next_state, _, _, _, _ = env.step(UP)
        assert next_state == (0, 0)

    def test_accion_right_mueve_a_la_derecha(self, env):
        env.reset()
        next_state, _, _, _, _ = env.step(RIGHT)
        assert next_state == (0, 1)

    def test_accion_down_mueve_abajo(self, env):
        env.reset()
        next_state, _, _, _, _ = env.step(DOWN)
        assert next_state == (1, 0)

    def test_accion_left_mueve_a_la_izquierda(self, env):
        """Desde (0,1) moverse LEFT debe regresar a (0,0)."""
        env.reset()
        env.step(RIGHT)  # Ir a (0,1)
        next_state, _, _, _, _ = env.step(LEFT)
        assert next_state == (0, 0)

    def test_choque_con_borde_no_mueve_agente(self, env):
        """Intentar salir del mapa por el borde no mueve al agente."""
        env.reset()  # Agente en (0,0)
        next_state, reward, _, _, _ = env.step(UP)
        assert next_state == (0, 0)
        assert reward == _REWARD_WALL

    def test_choque_con_borde_da_recompensa_negativa(self, env):
        env.reset()
        _, reward, _, _, _ = env.step(LEFT)
        assert reward == _REWARD_WALL

    def test_choque_con_pared_no_mueve_agente(self, env):
        """Chocar con una pared interior mantiene la posición del agente."""
        env.reset()
        # La pared está en (0, 3) en el mapa de size=5
        # Desde (0,0): →(0,1) →(0,2) →intentar(0,3)=WALL
        env.step(RIGHT)  # (0,1)
        env.step(RIGHT)  # (0,2)
        pos_before_wall = (0, 2)
        next_state, reward, _, _, _ = env.step(RIGHT)  # (0,3) es pared
        assert next_state == pos_before_wall
        assert reward == _REWARD_WALL

    def test_paso_normal_da_recompensa_menos_uno(self, env):
        env.reset()
        _, reward, terminated, _, _ = env.step(DOWN)
        assert reward == _REWARD_STEP
        assert terminated is False

    def test_meta_da_recompensa_cien_y_termina(self, env):
        """Llegar a la meta (4,4) da +100 y termina el episodio."""
        env.reset()
        # Ruta válida evitando paredes (0,3),(1,1),(2,3) y peligros (3,1),(4,3):
        # (0,0)→(0,1)→(0,2)→(1,2)→(2,2)→(3,2)→(3,3)→(3,4)→(4,4)
        moves = [RIGHT, RIGHT, DOWN, DOWN, DOWN, RIGHT, RIGHT, DOWN]
        reward = None
        terminated = False
        for action in moves:
            _, reward, terminated, _, _ = env.step(action)
            if terminated:
                break
        assert reward == _REWARD_GOAL
        assert terminated is True

    def test_peligro_da_recompensa_menos_cien_y_termina(self, env):
        """Caer en un peligro da -100 y termina el episodio."""
        # El peligro en el mapa de 5x5 está en (3,1) y (4,3)
        # Navegar a (3,1): ↓↓↓→
        env.reset()
        env.step(DOWN)   # (1,0)
        env.step(DOWN)   # (2,0)
        env.step(DOWN)   # (3,0)
        _, reward, terminated, _, _ = env.step(RIGHT)  # (3,1) = HAZARD
        assert reward == _REWARD_HAZARD
        assert terminated is True

    def test_render_retorna_string(self, env):
        env.reset()
        output = env.render()
        assert isinstance(output, str)
        assert len(output) > 0

    def test_render_contiene_simbolo_explorador(self, env):
        """El render debe mostrar 'E' en la posición del agente."""
        env.reset()  # Agente en (0,0) = START
        output = env.render()
        assert "E" in output

    def test_get_all_states_excluye_paredes(self, env):
        states = env.get_all_states()
        for state in states:
            r, c = state
            assert env._grid[r][c] != _WALL

    def test_state_to_index_es_biyectivo(self, env):
        """Cada estado debe tener un índice único."""
        indices = set()
        for r in range(env.size):
            for c in range(env.size):
                idx = env.state_to_index((r, c))
                assert idx not in indices
                indices.add(idx)


# ─────────────────────────────────────────────────────────────────────────────
# TESTS DEL AGENTE Q-LEARNING
# ─────────────────────────────────────────────────────────────────────────────


class TestQLearningAgent:
    def test_choose_action_retorna_accion_valida(self, agent):
        action = agent.choose_action((0, 0))
        assert action in (UP, RIGHT, DOWN, LEFT)

    def test_choose_action_epsilon_cero_es_determinista(self, agent):
        """Con ε=0, la misma Q-table siempre elige la misma acción."""
        assert agent.epsilon == 0.0
        a1 = agent.choose_action((2, 2))
        a2 = agent.choose_action((2, 2))
        assert a1 == a2

    def test_choose_action_epsilon_uno_es_aleatorio(self):
        """Con ε=1, el agente elige siempre al azar → debería variar."""
        ag = QLearningAgent(epsilon=1.0, seed=1)
        acciones = {ag.choose_action((0, 0)) for _ in range(50)}
        # Con 50 intentos y 4 posibles acciones, casi seguro hay variedad
        assert len(acciones) > 1

    def test_update_modifica_q_table(self, agent):
        """Tras update(), el valor Q(s, a) debe cambiar."""
        state = (1, 1)
        action = RIGHT
        q_antes = agent.q_table[state][action]
        agent.update(state, action, reward=10.0, next_state=(1, 2), done=False)
        q_despues = agent.q_table[state][action]
        assert q_despues != q_antes

    def test_update_hacia_recompensa_positiva_aumenta_q(self, agent):
        """Una recompensa positiva debe aumentar el Q-valor."""
        state = (0, 0)
        action = DOWN
        agent.q_table[state][action] = 0.0
        agent.update(state, action, reward=100.0, next_state=(1, 0), done=True)
        assert agent.q_table[state][action] > 0.0

    def test_update_hacia_recompensa_negativa_disminuye_q(self, agent):
        """Una recompensa negativa debe disminuir el Q-valor."""
        state = (0, 0)
        action = LEFT
        agent.q_table[state][action] = 0.0
        agent.update(state, action, reward=-100.0, next_state=(0, 0), done=True)
        assert agent.q_table[state][action] < 0.0

    def test_update_done_no_usa_estado_siguiente(self):
        """Cuando done=True, el valor futuro es 0 (sin bootstrap)."""
        ag = QLearningAgent(learning_rate=1.0, gamma=0.99, epsilon=0.0)
        state = (2, 2)
        action = UP
        ag.q_table[state][action] = 0.0
        # Con lr=1.0 y done=True: Q(s,a) = reward exactamente
        ag.update(state, action, reward=50.0, next_state=(1, 2), done=True)
        assert ag.q_table[state][action] == pytest.approx(50.0)

    def test_epsilon_decae_durante_entrenamiento(self, env):
        """Después del entrenamiento, ε debe ser menor que al inicio."""
        ag = QLearningAgent(epsilon=1.0, epsilon_decay=0.9, epsilon_min=0.01)
        epsilon_inicial = ag.epsilon
        ag.train(env, n_episodes=20, max_steps=50)
        assert ag.epsilon < epsilon_inicial

    def test_epsilon_no_baja_de_epsilon_min(self, env):
        """ε nunca debe ser menor que epsilon_min."""
        ag = QLearningAgent(epsilon=1.0, epsilon_decay=0.5, epsilon_min=0.05)
        ag.train(env, n_episodes=100, max_steps=50)
        assert ag.epsilon >= 0.05

    def test_train_retorna_lista_de_recompensas(self, env):
        ag = QLearningAgent()
        rewards = ag.train(env, n_episodes=10, max_steps=50)
        assert isinstance(rewards, list)
        assert len(rewards) == 10

    def test_train_retorna_floats(self, env):
        ag = QLearningAgent()
        rewards = ag.train(env, n_episodes=5, max_steps=50)
        for r in rewards:
            assert isinstance(r, float)

    def test_agente_mejora_con_entrenamiento(self, env):
        """
        Tras 500 episodios, la recompensa media de los últimos 100 episodios
        debe ser mayor que la de los primeros 100.

        Este test valida que el aprendizaje ocurre.
        """
        ag = QLearningAgent(
            learning_rate=0.2,
            gamma=0.99,
            epsilon=1.0,
            epsilon_decay=0.995,
            epsilon_min=0.01,
            seed=42,
        )
        rewards = ag.train(env, n_episodes=500, max_steps=200)

        first_100_avg = sum(rewards[:100]) / 100
        last_100_avg = sum(rewards[-100:]) / 100

        assert last_100_avg > first_100_avg, (
            f"El agente no mejoró: primeros 100 = {first_100_avg:.1f}, "
            f"últimos 100 = {last_100_avg:.1f}"
        )

    def test_get_policy_retorna_acciones_validas(self, env, agent):
        policy = agent.get_policy(env)
        for state, action in policy.items():
            assert action in (UP, RIGHT, DOWN, LEFT)

    def test_get_policy_cubre_todos_los_estados_validos(self, env, agent):
        """La política debe tener una acción para cada estado no-pared."""
        policy = agent.get_policy(env)
        valid_states = set(env.get_all_states())
        policy_states = set(policy.keys())
        assert valid_states == policy_states
