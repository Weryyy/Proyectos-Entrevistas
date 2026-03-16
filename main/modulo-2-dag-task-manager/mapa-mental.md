# 📊 Mapa Mental — DAG & Task Management

## ⏱ Tiempo estimado: 10–15 horas

```
                     ╔═══════════════════════════╗
                     ║   DAG & TASK MANAGEMENT   ║
                     ║  (Grafos Acíclicos Dirigidos) ║
                     ╚════════════╤══════════════╝
                                  │
       ┌──────────────┬───────────┼───────────┬────────────────┐
       ▼              ▼           ▼           ▼                ▼
 ┌───────────┐ ┌────────────┐ ┌────────┐ ┌──────────┐  ┌────────────┐
 │PREREQUISI-│ │ CONCEPTOS  │ │  RUTA  │ │ RECURSOS │  │ SIGUIENTES │
 │   TOS     │ │   CLAVE    │ │  DE    │ │          │  │   PASOS    │
 └─────┬─────┘ └─────┬──────┘ │ESTUDIO │ └────┬─────┘  └─────┬──────┘
       │              │        └───┬────┘      │              │
       ▼              ▼            ▼           ▼              ▼
```

---

## 📋 Prerequisitos

```
  Prerequisitos
  ├── Python intermedio
  │   ├── Clases y herencia
  │   ├── Estructuras de datos nativas
  │   └── Manejo de excepciones
  ├── Grafos básicos
  │   ├── Nodos y aristas
  │   ├── Dirigidos vs no dirigidos
  │   └── Representación: lista de adyacencia
  └── Recursión y DFS básico
```

## 🔑 Conceptos Clave

```
  Conceptos Clave
  ├── Grafos Dirigidos
  │   ├── Vértices (tareas)
  │   └── Aristas (dependencias)
  ├── DAG (Directed Acyclic Graph)
  │   ├── No tiene ciclos
  │   └── Modela dependencias sin conflictos
  ├── DFS (Depth-First Search)
  │   ├── Recorrido en profundidad
  │   └── Detección de ciclos con colores
  │       ├── BLANCO → no visitado
  │       ├── GRIS  → en proceso
  │       └── NEGRO → completado
  ├── Ordenamiento Topológico
  │   ├── Orden lineal respetando dependencias
  │   └── Algoritmo de Kahn (BFS) o DFS
  ├── Cola de Prioridad (heapq)
  │   ├── Extraer tarea de mayor prioridad
  │   └── O(log n) insert / extract-min
  └── Cancelación en Cascada
      ├── Si una tarea falla → cancelar dependientes
      └── Propagación recursiva por el grafo
```

## 🗺 Ruta de Estudio

```
  ① Grafos: representación y recorrido
  │   └── → Lista de adyacencia, BFS, DFS
  │
  ② Detección de ciclos
  │   └── → Algoritmo de 3 colores con DFS
  │
  ③ Ordenamiento topológico
  │   ├── → Algoritmo de Kahn (grados de entrada)
  │   └── → Variante con DFS + pila
  │
  ④ Colas de prioridad
  │   ├── → Módulo heapq de Python
  │   └── → Ejecutar tareas según prioridad
  │
  ⑤ Cancelación en cascada
      ├── → Propagar fallo a tareas dependientes
      ├── → Manejar estados: PENDING, RUNNING, DONE, CANCELLED
      └── → Tests de integración
```

## 📚 Recursos

```
  Recursos
  ├── CLRS — Cap. 22: Grafos (BFS, DFS, Topological Sort)
  ├── LeetCode #207 — Course Schedule (detección de ciclos)
  ├── LeetCode #210 — Course Schedule II (topological sort)
  ├── Documentación Python: heapq, collections.deque
  └── Wikipedia — Directed Acyclic Graph
```

## 🚀 Siguientes Pasos

```
  Después de dominar DAG Task Manager →
  ├── Apache Airflow (orquestación de workflows)
  ├── Makefiles (dependencias de compilación)
  ├── CI/CD Pipelines
  │   ├── GitHub Actions
  │   └── Jenkins
  ├── Kubernetes Job Scheduling
  └── Luigi / Prefect (orquestadores Python)
```

---

> **💡 Consejo:** Piensa en las tareas como nodos de un grafo. Si la tarea B
> depende de A, hay una arista A → B. Toda la lógica del módulo se construye
> sobre esa idea fundamental.
