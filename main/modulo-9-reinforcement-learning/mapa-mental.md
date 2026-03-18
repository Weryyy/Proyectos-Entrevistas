# 🧠 Mapa Mental — Reinforcement Learning

## ⏱ Tiempo estimado: 12–20 horas

```
                    ╔════════════════════════════╗
                    ║   REINFORCEMENT LEARNING   ║
                    ║  (Aprendizaje por Refuerzo)║
                    ╚═════════════╤══════════════╝
                                  │
        ┌──────────┬──────────────┼──────────────┬──────────────┐
        ▼          ▼              ▼              ▼              ▼
  ┌──────────┐ ┌────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
  │PREREQUISI│ │CONCEPT.│  │ALGORITMO │  │RECURSOS  │  │SIGUIENTES│
  │   TOS    │ │ CLAVE  │  │          │  │          │  │  PASOS   │
  └────┬─────┘ └───┬────┘  └─────┬────┘  └────┬─────┘  └────┬─────┘
       │            │             │             │             │
       ▼            ▼             ▼             ▼             ▼
```

---

## 📋 Prerequisitos

```
  Prerequisitos
  ├── Python intermedio
  │   ├── Diccionarios anidados / defaultdict
  │   ├── Listas y arrays (q-table como dict o lista 2D)
  │   └── random.random(), random.choice()
  ├── Matemáticas básicas
  │   ├── Probabilidad (distribuciones, esperanza)
  │   └── Álgebra lineal básica (vectores de valores)
  └── Conceptos de programación dinámica
      ├── Bellman equation (intuitivo)
      └── Optimal substructure
```

## 🔑 Conceptos Clave

```
  Reinforcement Learning
  ├── MDP (Markov Decision Process)
  │   ├── Estado (State): representación del mundo
  │   ├── Acción (Action): qué puede hacer el agente
  │   ├── Recompensa (Reward): señal de feedback
  │   ├── Transición: P(s'|s,a)
  │   └── Propiedad de Markov: el futuro solo depende del presente
  │
  ├── Q-Learning
  │   ├── Q-Table: Q[estado][accion] = valor esperado
  │   ├── Ecuación de Bellman
  │   │   └── Q(s,a) ← Q(s,a) + α[r + γ·max Q(s',·) - Q(s,a)]
  │   ├── Learning rate α: cuánto actualizar (0 < α ≤ 1)
  │   └── Discount factor γ: valor del futuro (0 < γ < 1)
  │
  ├── Exploración vs Explotación
  │   ├── Epsilon-greedy: ε prob. de explorar, 1-ε de explotar
  │   ├── Epsilon decay: reducir ε con el tiempo
  │   └── Dilema fundamental del RL
  │
  └── Gymnasium API (estándar industrial)
      ├── env.reset() → (state, info)
      ├── env.step(action) → (next_state, reward, terminated, truncated, info)
      └── env.render() → visualización
```

## 🗺 Ruta de Estudio

```
  ① Entender el problema de control secuencial
  │   └── → ¿Por qué supervised learning no alcanza?
  │
  ② MDP: formalizar el entorno
  │   ├── → Definir estados, acciones, recompensas
  │   └── → Implementar GridWorld desde cero
  │
  ③ Política aleatoria (baseline)
  │   └── → Agente que elige acciones al azar (¿qué recompensa obtiene?)
  │
  ④ Q-Learning: la Q-Table
  │   ├── → Inicializar Q(s,a) = 0 para todo s, a
  │   ├── → Entender la ecuación de Bellman
  │   └── → Implementar update() con la fórmula TD
  │
  ⑤ Epsilon-Greedy + Decay
  │   ├── → ε alto al inicio → muchas exploraciones
  │   └── → ε decae → el agente explota su conocimiento
  │
  ⑥ Entrenamiento y evaluación
  │   ├── → Curva de recompensa por episodio
  │   └── → Verificar que el agente mejora con el tiempo
  │
  ⑦ Extensiones
      ├── → Deep Q-Network (DQN): Q-Table → red neuronal
      ├── → Policy Gradient (REINFORCE)
      └── → Actor-Critic (A2C, PPO)
```

## 📚 Recursos

```
  Recursos
  ├── "Reinforcement Learning: An Introduction" — Sutton & Barto (gratuito online)
  ├── Gymnasium (formerly OpenAI Gym) — gymnasium.farama.org
  ├── Spinning Up in Deep RL — OpenAI
  ├── David Silver's RL Course — YouTube (UCL/DeepMind)
  └── CS234 Stanford — Reinforcement Learning (YouTube)
```

## 🚀 Siguientes Pasos

```
  Después de dominar Q-Learning →
  ├── Deep Q-Networks (DQN)
  │   ├── Experience replay buffer
  │   ├── Target network
  │   └── Atari games con PyTorch/JAX
  ├── Policy Gradient Methods
  │   ├── REINFORCE
  │   └── Proximal Policy Optimization (PPO)
  ├── Entornos más complejos
  │   ├── CartPole, LunarLander (Gymnasium)
  │   └── MuJoCo (robótica)
  └── RL en producción
      ├── Sistemas de recomendación (Netflix, YouTube)
      ├── Trading algorítmico
      └── RLHF (RL from Human Feedback) — como en ChatGPT
```

---

> **💡 Consejo:** Antes de implementar Q-Learning, corre un agente aleatorio durante
> 100 episodios y observa la recompensa media. Ese es tu baseline. Cuando tu agente
> Q-Learning supere ese baseline consistentemente, ¡estás aprendiendo!
