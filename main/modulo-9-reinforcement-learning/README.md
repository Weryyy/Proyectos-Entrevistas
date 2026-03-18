# Módulo 9: El Explorador de Mundos — Reinforcement Learning

## 🧠 Concepto Técnico

El **Aprendizaje por Refuerzo** (Reinforcement Learning, RL) es una rama del machine
learning donde un **agente** aprende a tomar decisiones interactuando con un **entorno**.
No se le dice qué hacer: descubre por sí solo qué acciones maximizan una **recompensa acumulada**.

### Los 6 elementos fundamentales del RL

| Elemento        | Definición                                               | En nuestro problema          |
|-----------------|----------------------------------------------------------|------------------------------|
| **Agente**      | El que toma decisiones                                   | El explorador IA             |
| **Entorno**     | El sistema con el que interactúa el agente               | La cuadrícula planetaria     |
| **Estado (s)**  | La situación actual del agente                           | Posición (fila, columna)     |
| **Acción (a)**  | Lo que puede hacer el agente                             | Moverse: ↑ ↓ ← →             |
| **Recompensa (r)** | Señal de feedback del entorno                         | +100 meta, -100 peligro, -1 paso |
| **Política (π)**| La estrategia del agente: estado → acción               | Q-table aprendida            |

---

## 🚀 Lore: El Explorador de Mundos Alienígenas

> *La Federación Galáctica te ha enviado a explorar un planeta desconocido.
> El terreno está representado como una cuadrícula. Algunos sectores son seguros,
> otros esconden trampas de energía letales, y hay un solo punto de extracción.*
>
> *Tu módulo de IA empieza sin saber nada: no tiene mapa, no conoce los peligros.
> Solo puede aprender a través de la experiencia: explorar, recibir señales de
> retroalimentación del ambiente, y ajustar su estrategia.*
>
> *Con cada episodio de entrenamiento, el explorador aprende qué caminos llevan
> a la extracción y cuáles terminan en desastre. Tu misión: implementar ese cerebro.*

---

## 🌐 Formalización: Proceso de Decisión de Markov (MDP)

El entorno es un **MDP** definido por la tupla **(S, A, P, R, γ)**:

- **S** — Conjunto de estados: todas las celdas (i, j) de la cuadrícula
- **A** — Conjunto de acciones: {↑=0, →=1, ↓=2, ←=3}
- **P** — Probabilidad de transición: determinista (siempre moverse en la dirección elegida)
- **R** — Función de recompensa: +100 meta, -100 peligro, -1 por paso, -5 por chocar con muro
- **γ** — Factor de descuento (gamma): cuánto valora el futuro vs el presente (γ=0.99)

---

## 🌍 El Entorno: GridWorld

```
Cuadrícula 5×5 (por defecto):

  0   1   2   3   4
┌───┬───┬───┬───┬───┐
│ S │   │   │ # │   │  0   S = Inicio (Start)
├───┼───┼───┼───┼───┤
│   │ # │   │   │   │  1   # = Pared (Wall) — impasable
├───┼───┼───┼───┼───┤
│   │   │   │ # │   │  2   X = Peligro (Hazard) — recompensa -100
├───┼───┼───┼───┼───┤
│   │ X │   │   │   │  3   G = Meta (Goal) — recompensa +100
├───┼───┼───┼───┼───┤
│   │   │   │ X │ G │  4
└───┴───┴───┴───┴───┘

Recompensas:
  • Cada paso:          -1   (incentiva rutas cortas)
  • Chocar con muro:    -5   (penaliza intentos inválidos)
  • Caer en peligro: -100   (episodio termina)
  • Llegar a la meta: +100  (episodio termina)
```

---

## 🤖 El Algoritmo: Q-Learning

Q-Learning es un algoritmo de **TD (Temporal Difference)** que aprende una función
de valor-acción **Q(s, a)**: "¿cuánta recompensa acumulada puedo esperar si estoy en
el estado `s` y tomo la acción `a`?"

### La ecuación de Bellman (actualización Q-Learning):

```
Q(s, a) ← Q(s, a) + α · [r + γ · max_a'(Q(s', a')) - Q(s, a)]

Donde:
  α (alpha)     = tasa de aprendizaje (learning rate) — cuánto actualizar
  γ (gamma)     = factor de descuento — cuánto valen las recompensas futuras
  r             = recompensa inmediata recibida
  s'            = estado siguiente
  max_a' Q(s',a') = mejor valor esperado desde el estado siguiente
  [r + γ·max Q(s',a') - Q(s,a)] = Error TD (temporal difference error)
```

### Estrategia de exploración: Epsilon-Greedy

El agente necesita un balance entre **explorar** (probar acciones nuevas) y
**explotar** (usar lo que ya sabe que funciona):

```
Con probabilidad ε:    acción aleatoria  (EXPLORACIÓN)
Con probabilidad 1-ε:  mejor acción Q   (EXPLOTACIÓN)

ε empieza alto (ej. 1.0 = exploración pura) y decae con el tiempo:
  ε = max(ε_min, ε × ε_decay)

Al inicio: el agente explora mucho para aprender el mapa.
Al final:  el agente explota su conocimiento para maximizar la recompensa.
```

---

## 🔌 La API: Patrón Gymnasium

Nuestro entorno sigue el mismo patrón que **Gymnasium** (antes OpenAI Gym),
el estándar de facto para entornos de RL:

```python
env = GridWorldEnv(size=5)

# Reiniciar el entorno al inicio de cada episodio
state, info = env.reset()

# Bucle de interacción agente-entorno
done = False
while not done:
    action = agent.choose_action(state)      # el agente elige
    next_state, reward, terminated, truncated, info = env.step(action)
    agent.update(state, action, reward, next_state, done)
    state = next_state
    done = terminated or truncated

# Visualizar el estado actual
print(env.render())
```

---

## ▶️ Cómo Ejecutar

### Entrenamiento y demo

```bash
cd main/modulo-9-reinforcement-learning/codigo
python q_agent.py
```

### Ejecutar las pruebas

```bash
cd main/modulo-9-reinforcement-learning/codigo
pytest test_rl.py -v
```

### Requisitos

- Python 3.10+
- pytest (`pip install pytest`)

---

## 📁 Estructura del Módulo

```
modulo-9-reinforcement-learning/
├── README.md                    # Este archivo
├── mapa-mental.md               # Mapa mental del módulo
└── codigo/
    ├── rl_environment.py        # Entorno GridWorld (API estilo Gymnasium)
    ├── q_agent.py               # Agente Q-Learning con epsilon-greedy
    └── test_rl.py               # Suite de pruebas con pytest
```
