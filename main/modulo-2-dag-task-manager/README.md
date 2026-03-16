# Módulo 2: Orquestador de Misiones — DAG & Task Manager

## 🚀 Lore: Comandante de Misiones Espaciales

Eres el **comandante de misiones** de una flota espacial. Cada misión tiene dependencias
que deben respetarse: no puedes "Lanzar la Nave" sin antes "Repostar Combustible", y no
puedes "Repostar" sin antes "Inspeccionar Tanques". Tu trabajo es orquestar todas las
misiones en el orden correcto, priorizar las más críticas cuando varias están listas
al mismo tiempo, y si una misión se cancela, **todas las misiones que dependían de ella
deben cancelarse en cascada** — no puedes lanzar si nunca repostaste.

---

## 📚 Explicación Técnica

### ¿Qué es un DAG (Directed Acyclic Graph)?

Un **Grafo Dirigido Acíclico** es una estructura de datos donde:
- Los nodos representan **tareas** (misiones).
- Las aristas dirigidas representan **dependencias** (A → B significa "A debe completarse antes de B").
- **No existen ciclos**: no puedes tener A → B → C → A, porque sería una dependencia circular imposible de resolver.

```
[Inspeccionar Tanques] → [Repostar Combustible] → [Lanzar Nave]
                                                  ↗
                       [Cargar Tripulación] ------
```

### Ordenamiento Topológico (Topological Sort) con DFS

El **ordenamiento topológico** produce una secuencia lineal de tareas que respeta todas
las dependencias. Utilizamos **DFS (Depth-First Search)** para implementarlo:

1. Visitamos cada nodo no visitado.
2. Recursivamente visitamos todas sus dependencias primero.
3. Al terminar con un nodo, lo añadimos al resultado.
4. Invertimos el resultado final.

**Detección de ciclos**: Durante el DFS, mantenemos tres estados por nodo:
- `NO_VISITADO`: No hemos empezado a procesar este nodo.
- `EN_PROCESO`: Estamos procesando este nodo (está en la pila de recursión).
- `VISITADO`: Ya terminamos de procesar este nodo.

Si durante el DFS encontramos un nodo `EN_PROCESO`, hemos detectado un **ciclo**.

### Cola de Prioridad (Priority Queue) con `heapq`

Cuando múltiples misiones están listas (todas sus dependencias completadas), usamos una
**cola de prioridad** (min-heap) para ejecutar primero la de mayor prioridad (menor valor numérico).

`heapq` en Python implementa un **min-heap binario**:
- `heappush(heap, item)` — Inserta en O(log n).
- `heappop(heap)` — Extrae el mínimo en O(log n).

### Cancelación en Cascada (Cascade Cancellation)

Si una misión se cancela, todas las misiones **downstream** (que dependen de ella directa
o indirectamente) también deben cancelarse. Implementamos esto con un recorrido **BFS**:

1. Partimos de la tarea cancelada.
2. Buscamos todas las tareas que la tienen como dependencia.
3. Las cancelamos y repetimos el proceso para cada una.

---

## 📊 Análisis de Complejidad

| Operación               | Complejidad Temporal | Complejidad Espacial |
|--------------------------|---------------------|----------------------|
| Agregar tarea            | O(1)                | O(1)                 |
| Agregar dependencia      | O(1)                | O(1)                 |
| Ordenamiento topológico  | O(V + E)            | O(V)                 |
| Detección de ciclos      | O(V + E)            | O(V)                 |
| Obtener siguiente tarea  | O(V log V)          | O(V)                 |
| Completar tarea          | O(1)                | O(1)                 |
| Cancelación en cascada   | O(V + E)            | O(V)                 |

Donde **V** = número de tareas (vértices) y **E** = número de dependencias (aristas).

---

## 🛠️ Cómo Ejecutar

### Requisitos
- Python 3.8+
- pytest (para pruebas)

### Ejecutar el demo

```bash
cd main/modulo-2-dag-task-manager/codigo/python
python task_manager.py
```

### Ejecutar las pruebas

```bash
cd main/modulo-2-dag-task-manager/codigo/python
pytest test_task_manager.py -v
```

---

## 🗂️ Estructura del Módulo

```
modulo-2-dag-task-manager/
├── README.md
└── codigo/
    └── python/
        ├── task_manager.py        # Implementación principal
        └── test_task_manager.py   # Suite de pruebas con pytest
```

---

## 🔑 Conceptos Clave para Entrevistas

1. **DAG y Topological Sort**: Pregunta clásica — ordenar tareas con dependencias.
2. **Detección de ciclos en grafos dirigidos**: Uso de estados (blanco/gris/negro) en DFS.
3. **Priority Queue / Heap**: Cuándo usar heap vs sort, complejidad de operaciones.
4. **BFS para propagación**: Cancelación en cascada, propagación de efectos en grafos.
5. **Diseño de sistemas**: Cómo modelar un sistema de tareas con estados y transiciones.
