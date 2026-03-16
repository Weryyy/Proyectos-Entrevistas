"""
Módulo 2: Orquestador de Misiones — DAG & Task Manager
=======================================================

Este módulo implementa un sistema de gestión de tareas basado en un
Grafo Dirigido Acíclico (DAG). Permite:

- Definir tareas con prioridades y dependencias.
- Obtener el orden de ejecución mediante ordenamiento topológico (DFS).
- Seleccionar la siguiente tarea a ejecutar usando una cola de prioridad (heapq).
- Cancelar tareas en cascada cuando una dependencia falla.

Lore: Eres el comandante de una flota espacial. Cada misión (tarea) tiene
dependencias que deben completarse antes de poder ejecutarla. ¡Ordena tus
misiones sabiamente o la flota quedará varada en el espacio!
"""

from enum import Enum
from collections import deque
from dataclasses import dataclass, field
import heapq


# =============================================================================
# ENUMERACIÓN DE ESTADOS
# =============================================================================
# Cada tarea pasa por un ciclo de vida definido por estos estados.
# Las transiciones válidas son:
#   PENDING → READY → RUNNING → COMPLETED
#   Cualquier estado (excepto COMPLETED) → CANCELLED

class TaskStatus(Enum):
    """Estados posibles de una tarea/misión."""
    PENDING = "pending"       # Esperando a que se cumplan dependencias
    READY = "ready"           # Todas las dependencias cumplidas, lista para ejecutar
    RUNNING = "running"       # En ejecución actualmente
    COMPLETED = "completed"   # Completada exitosamente
    CANCELLED = "cancelled"   # Cancelada (manual o por cascada)


# =============================================================================
# CLASE TASK (TAREA / MISIÓN)
# =============================================================================

@dataclass
class Task:
    """
    Representa una tarea (misión) en el sistema.

    Atributos:
        id: Identificador único de la tarea.
        name: Nombre descriptivo de la tarea/misión.
        priority: Prioridad numérica (menor valor = mayor prioridad).
                  Ejemplo: priority=1 se ejecuta antes que priority=5.
        status: Estado actual de la tarea (ver TaskStatus).
        dependencies: Conjunto de IDs de tareas que deben completarse antes.
    """
    id: str
    name: str
    priority: int = 0
    status: TaskStatus = TaskStatus.PENDING
    dependencies: set = field(default_factory=set)

    def __lt__(self, other):
        """
        Comparación para la cola de prioridad (heapq).
        heapq es un min-heap, así que menor valor = mayor prioridad.
        En caso de empate en prioridad, ordenamos por id para determinismo.
        """
        if self.priority == other.priority:
            return self.id < other.id
        return self.priority < other.priority


# =============================================================================
# CLASE TASKMANAGER (ORQUESTADOR DE MISIONES)
# =============================================================================

class TaskManager:
    """
    Orquestador de misiones espaciales basado en DAG.

    Gestiona un grafo dirigido acíclico de tareas donde las aristas
    representan dependencias. Proporciona:
    - Ordenamiento topológico para determinar el orden de ejecución.
    - Cola de prioridad para seleccionar la siguiente tarea.
    - Cancelación en cascada para propagar fallos.

    Estructura interna:
        tasks: dict[str, Task] — Mapa de id → tarea.
        dependents: dict[str, set] — Mapa de id → conjunto de tareas que dependen de ella.
                    Si A está en dependencies de B, entonces B está en dependents[A].
                    Esto nos permite propagar cancelaciones eficientemente.
    """

    def __init__(self):
        # Diccionario principal: task_id → objeto Task
        self.tasks: dict[str, Task] = {}

        # Grafo inverso: task_id → {tareas que dependen de esta tarea}
        # Necesario para la cancelación en cascada (propagación hacia adelante)
        self.dependents: dict[str, set] = {}

    # -------------------------------------------------------------------------
    # AGREGAR TAREA
    # -------------------------------------------------------------------------

    def add_task(self, task_id: str, name: str, priority: int = 0,
                 dependencies: set = None) -> Task:
        """
        Agrega una nueva misión al sistema.

        Args:
            task_id: Identificador único de la misión.
            name: Nombre de la misión (ej: "Repostar Combustible").
            priority: Prioridad (menor = más urgente). Por defecto 0.
            dependencies: Conjunto de IDs de misiones prerequisito.

        Returns:
            La tarea creada.

        Raises:
            ValueError: Si ya existe una tarea con ese ID.
        """
        if task_id in self.tasks:
            raise ValueError(f"La tarea '{task_id}' ya existe en el sistema.")

        deps = set(dependencies) if dependencies else set()
        task = Task(id=task_id, name=name, priority=priority, dependencies=deps)

        self.tasks[task_id] = task

        # Inicializamos la entrada en el grafo inverso
        if task_id not in self.dependents:
            self.dependents[task_id] = set()

        # Registramos esta tarea como dependiente de cada una de sus dependencias
        # Si la tarea B depende de A, entonces A.dependents incluye B
        for dep_id in deps:
            if dep_id not in self.dependents:
                self.dependents[dep_id] = set()
            self.dependents[dep_id].add(task_id)

        # Actualizamos el estado: si no tiene dependencias, está lista
        self._update_task_status(task_id)

        return task

    # -------------------------------------------------------------------------
    # AGREGAR DEPENDENCIA
    # -------------------------------------------------------------------------

    def add_dependency(self, task_id: str, depends_on: str) -> None:
        """
        Agrega una dependencia entre dos tareas existentes.

        Esto significa que 'task_id' no puede ejecutarse hasta que
        'depends_on' esté completada.

        Args:
            task_id: La tarea que necesita la dependencia.
            depends_on: La tarea que debe completarse primero.

        Raises:
            KeyError: Si alguna de las tareas no existe.
        """
        if task_id not in self.tasks:
            raise KeyError(f"La tarea '{task_id}' no existe.")
        if depends_on not in self.tasks:
            raise KeyError(f"La tarea '{depends_on}' no existe.")

        # Agregamos la dependencia en ambas direcciones del grafo
        self.tasks[task_id].dependencies.add(depends_on)

        if depends_on not in self.dependents:
            self.dependents[depends_on] = set()
        self.dependents[depends_on].add(task_id)

        # Recalculamos el estado de la tarea
        self._update_task_status(task_id)

    # -------------------------------------------------------------------------
    # ORDENAMIENTO TOPOLÓGICO CON DFS
    # -------------------------------------------------------------------------

    def get_execution_order(self) -> list[str]:
        """
        Retorna el orden de ejecución de todas las tareas usando
        ordenamiento topológico basado en DFS.

        El algoritmo funciona así:
        1. Mantenemos tres estados por nodo: NO_VISITADO, EN_PROCESO, VISITADO.
        2. Para cada nodo no visitado, iniciamos un DFS.
        3. Al entrar a un nodo, lo marcamos EN_PROCESO.
        4. Visitamos recursivamente todas sus dependencias.
        5. Si encontramos un nodo EN_PROCESO, hay un ciclo → error.
        6. Al terminar con un nodo, lo marcamos VISITADO y lo agregamos al resultado.
        7. Al final, invertimos el resultado.

        Returns:
            Lista de task_ids en orden de ejecución válido.

        Raises:
            ValueError: Si se detecta un ciclo en las dependencias.
        """
        # Estados del DFS: 0 = no visitado, 1 = en proceso, 2 = visitado
        NO_VISITADO, EN_PROCESO, VISITADO = 0, 1, 2
        estado = {task_id: NO_VISITADO for task_id in self.tasks}
        resultado = []

        def dfs(nodo: str):
            """
            DFS recursivo para ordenamiento topológico.
            Visitamos las dependencias primero (los prerequisitos),
            luego agregamos el nodo actual al resultado.
            """
            if estado[nodo] == EN_PROCESO:
                # ¡Ciclo detectado! Estamos visitando un nodo que ya está
                # en nuestra pila de recursión actual.
                raise ValueError(
                    f"¡Ciclo detectado! La tarea '{nodo}' forma parte de "
                    f"una dependencia circular. Misión imposible. 🔄"
                )

            if estado[nodo] == VISITADO:
                # Ya procesamos este nodo completamente, no hay nada que hacer.
                return

            # Marcamos el nodo como EN_PROCESO (está en la pila de recursión)
            estado[nodo] = EN_PROCESO

            # Visitamos recursivamente todas las dependencias (prerequisitos)
            for dep_id in self.tasks[nodo].dependencies:
                if dep_id in self.tasks:
                    dfs(dep_id)

            # Todas las dependencias procesadas → marcamos como VISITADO
            estado[nodo] = VISITADO
            resultado.append(nodo)

        # Iniciamos DFS desde cada nodo no visitado
        for task_id in self.tasks:
            if estado[task_id] == NO_VISITADO:
                dfs(task_id)

        # El resultado ya está en orden topológico correcto
        # (las dependencias se agregan antes que los que dependen de ellas)
        return resultado

    # -------------------------------------------------------------------------
    # OBTENER SIGUIENTES TAREAS (COLA DE PRIORIDAD)
    # -------------------------------------------------------------------------

    def get_next_tasks(self) -> list[Task]:
        """
        Retorna las tareas listas para ejecutar, ordenadas por prioridad.

        Una tarea está "lista" si:
        - Su estado es READY (todas sus dependencias están completadas).
        - No está cancelada, completada ni en ejecución.

        Usamos heapq (min-heap) para ordenar por prioridad.
        En un min-heap, el elemento con menor valor está en la raíz,
        lo cual coincide con nuestra convención de que menor número = mayor prioridad.

        Returns:
            Lista de tareas listas, ordenadas de mayor a menor prioridad.
        """
        # Construimos un heap con las tareas listas
        # heapq usa el operador __lt__ de Task para comparar
        heap = []
        for task in self.tasks.values():
            if task.status == TaskStatus.READY:
                # heappush mantiene la propiedad del min-heap
                heapq.heappush(heap, task)

        # Extraemos todas las tareas del heap en orden de prioridad
        tareas_ordenadas = []
        while heap:
            # heappop extrae el elemento con menor prioridad (más urgente)
            tareas_ordenadas.append(heapq.heappop(heap))

        return tareas_ordenadas

    # -------------------------------------------------------------------------
    # COMPLETAR TAREA
    # -------------------------------------------------------------------------

    def complete_task(self, task_id: str) -> None:
        """
        Marca una misión como completada y actualiza las dependientes.

        Al completar una tarea, verificamos si alguna de las tareas que
        dependían de ella ahora tiene todas sus dependencias satisfechas.
        Si es así, su estado cambia a READY.

        Args:
            task_id: ID de la tarea a completar.

        Raises:
            KeyError: Si la tarea no existe.
            ValueError: Si la tarea no está en un estado válido para completar.
        """
        if task_id not in self.tasks:
            raise KeyError(f"La tarea '{task_id}' no existe.")

        task = self.tasks[task_id]

        if task.status == TaskStatus.CANCELLED:
            raise ValueError(
                f"No se puede completar '{task_id}': está cancelada."
            )
        if task.status == TaskStatus.COMPLETED:
            raise ValueError(
                f"La tarea '{task_id}' ya está completada."
            )

        # Marcamos como completada
        task.status = TaskStatus.COMPLETED

        # Actualizamos el estado de todas las tareas que dependían de esta
        # Ahora que esta tarea está completa, quizá otras están listas
        for dependent_id in self.dependents.get(task_id, set()):
            self._update_task_status(dependent_id)

    # -------------------------------------------------------------------------
    # CANCELAR TAREA (CON CASCADA)
    # -------------------------------------------------------------------------

    def cancel_task(self, task_id: str) -> list[str]:
        """
        Cancela una misión y propaga la cancelación en cascada.

        Usa BFS (Breadth-First Search) para encontrar todas las tareas
        downstream que dependen directa o indirectamente de la tarea
        cancelada, y las cancela también.

        Analogía: Si cancelas "Repostar Combustible", automáticamente
        se cancela "Lanzar Nave" y "Viaje Interestelar" porque no
        pueden ejecutarse sin combustible.

        Args:
            task_id: ID de la tarea a cancelar.

        Returns:
            Lista de todos los IDs de tareas canceladas (incluyendo la original).

        Raises:
            KeyError: Si la tarea no existe.
        """
        if task_id not in self.tasks:
            raise KeyError(f"La tarea '{task_id}' no existe.")

        # Lista de todas las tareas canceladas en esta operación
        canceladas = []

        # BFS para propagación en cascada
        # Usamos una cola (deque) para procesar nivel por nivel
        cola = deque([task_id])

        while cola:
            current_id = cola.popleft()

            if current_id not in self.tasks:
                continue

            current_task = self.tasks[current_id]

            # Solo cancelamos si no está ya completada o cancelada
            if current_task.status in (TaskStatus.COMPLETED, TaskStatus.CANCELLED):
                continue

            # Cancelamos la tarea actual
            current_task.status = TaskStatus.CANCELLED
            canceladas.append(current_id)

            # Agregamos todas las tareas dependientes a la cola
            # Estas son las tareas que necesitaban que la actual se completara
            for dependent_id in self.dependents.get(current_id, set()):
                dependent_task = self.tasks.get(dependent_id)
                if dependent_task and dependent_task.status not in (
                    TaskStatus.COMPLETED, TaskStatus.CANCELLED
                ):
                    cola.append(dependent_id)

        return canceladas

    # -------------------------------------------------------------------------
    # DETECCIÓN DE CICLOS
    # -------------------------------------------------------------------------

    def detect_cycle(self) -> bool:
        """
        Detecta si existe algún ciclo en el grafo de dependencias.

        Utiliza DFS con coloreo de nodos (tres estados):
        - BLANCO (0): No visitado.
        - GRIS (1): En proceso (en la pila de recursión actual).
        - NEGRO (2): Completamente procesado.

        Si durante el DFS encontramos un nodo GRIS, significa que
        hemos encontrado un ciclo (estamos volviendo a un nodo que
        aún está siendo procesado).

        Returns:
            True si hay un ciclo, False si el grafo es un DAG válido.
        """
        BLANCO, GRIS, NEGRO = 0, 1, 2
        color = {task_id: BLANCO for task_id in self.tasks}

        def tiene_ciclo(nodo: str) -> bool:
            """Retorna True si se detecta un ciclo a partir de este nodo."""
            color[nodo] = GRIS  # Marcamos como "en proceso"

            # Exploramos las dependencias (aristas salientes)
            for dep_id in self.tasks[nodo].dependencies:
                if dep_id not in self.tasks:
                    continue

                if color[dep_id] == GRIS:
                    # ¡Encontramos un nodo que ya está en proceso!
                    # Esto significa que hay un ciclo.
                    return True

                if color[dep_id] == BLANCO:
                    # Nodo no visitado, continuamos el DFS
                    if tiene_ciclo(dep_id):
                        return True

            color[nodo] = NEGRO  # Completamente procesado
            return False

        # Verificamos cada nodo no visitado
        for task_id in self.tasks:
            if color[task_id] == BLANCO:
                if tiene_ciclo(task_id):
                    return True

        return False

    # -------------------------------------------------------------------------
    # MÉTODOS AUXILIARES PRIVADOS
    # -------------------------------------------------------------------------

    def _update_task_status(self, task_id: str) -> None:
        """
        Actualiza el estado de una tarea basándose en sus dependencias.

        Si todas las dependencias de una tarea están COMPLETED y la tarea
        está en estado PENDING, la movemos a READY.

        Este método se llama automáticamente cuando:
        - Se agrega una nueva tarea.
        - Se completa una tarea (para actualizar sus dependientes).
        """
        if task_id not in self.tasks:
            return

        task = self.tasks[task_id]

        # Solo actualizamos tareas en estado PENDING
        if task.status != TaskStatus.PENDING:
            return

        # Verificamos si todas las dependencias están completadas
        todas_completadas = all(
            self.tasks[dep_id].status == TaskStatus.COMPLETED
            for dep_id in task.dependencies
            if dep_id in self.tasks
        )

        # Si no tiene dependencias o todas están completadas → READY
        if todas_completadas:
            task.status = TaskStatus.READY

    def __repr__(self) -> str:
        """Representación del estado actual del orquestador."""
        lineas = ["=== Estado del Orquestador de Misiones ==="]
        for task in self.tasks.values():
            deps = ", ".join(task.dependencies) if task.dependencies else "ninguna"
            lineas.append(
                f"  [{task.status.value:>10}] {task.name} "
                f"(id={task.id}, prioridad={task.priority}, deps=[{deps}])"
            )
        return "\n".join(lineas)


# =============================================================================
# DEMO: ESCENARIO DE MISIONES ESPACIALES
# =============================================================================

if __name__ == "__main__":
    print("=" * 65)
    print("🚀 ORQUESTADOR DE MISIONES ESPACIALES — DEMO")
    print("=" * 65)

    # Creamos el orquestador
    manager = TaskManager()

    # --- Fase 1: Definir las misiones ---
    print("\n📋 Fase 1: Definiendo misiones de la flota...")

    manager.add_task("inspeccionar", "Inspeccionar Tanques", priority=1)
    manager.add_task("repostar", "Repostar Combustible", priority=2,
                     dependencies={"inspeccionar"})
    manager.add_task("cargar_tripulacion", "Cargar Tripulación", priority=1)
    manager.add_task("verificar_sistemas", "Verificar Sistemas de Navegación",
                     priority=3, dependencies={"inspeccionar"})
    manager.add_task("lanzar", "Lanzar Nave", priority=5,
                     dependencies={"repostar", "cargar_tripulacion",
                                   "verificar_sistemas"})
    manager.add_task("orbitar", "Entrar en Órbita", priority=4,
                     dependencies={"lanzar"})
    manager.add_task("mision_exploracion", "Misión de Exploración", priority=6,
                     dependencies={"orbitar"})

    print(manager)

    # --- Fase 2: Obtener orden de ejecución ---
    print("\n\n📊 Fase 2: Calculando orden de ejecución (topological sort)...")
    orden = manager.get_execution_order()
    print("Orden de ejecución:")
    for i, task_id in enumerate(orden, 1):
        task = manager.tasks[task_id]
        print(f"  {i}. {task.name} (prioridad={task.priority})")

    # --- Fase 3: Verificar que no hay ciclos ---
    print("\n🔍 Fase 3: Verificando integridad del DAG...")
    if manager.detect_cycle():
        print("  ⚠️  ¡ALERTA! Se detectó un ciclo en las dependencias.")
    else:
        print("  ✅ DAG válido — No se detectaron ciclos.")

    # --- Fase 4: Ejecutar misiones por prioridad ---
    print("\n⚡ Fase 4: Ejecutando misiones por prioridad...")
    ronda = 1
    while True:
        siguientes = manager.get_next_tasks()
        if not siguientes:
            # Verificamos si quedaron tareas pendientes (posible bloqueo)
            pendientes = [t for t in manager.tasks.values()
                          if t.status in (TaskStatus.PENDING, TaskStatus.READY)]
            if not pendientes:
                break
            else:
                print(f"  ⚠️  Tareas bloqueadas detectadas. Abortando.")
                break

        print(f"\n  --- Ronda {ronda} ---")
        for task in siguientes:
            print(f"  🟢 Ejecutando: {task.name} (prioridad={task.priority})")
            task.status = TaskStatus.RUNNING
            manager.complete_task(task.id)
            print(f"  ✅ Completada: {task.name}")
        ronda += 1

    # --- Fase 5: Demo de cancelación en cascada ---
    print("\n\n" + "=" * 65)
    print("💥 DEMO DE CANCELACIÓN EN CASCADA")
    print("=" * 65)

    manager2 = TaskManager()
    manager2.add_task("base", "Construir Base Lunar", priority=1)
    manager2.add_task("energia", "Instalar Paneles Solares", priority=2,
                      dependencies={"base"})
    manager2.add_task("comunicaciones", "Establecer Comunicaciones", priority=2,
                      dependencies={"base"})
    manager2.add_task("laboratorio", "Montar Laboratorio", priority=3,
                      dependencies={"energia", "comunicaciones"})
    manager2.add_task("experimentos", "Iniciar Experimentos", priority=4,
                      dependencies={"laboratorio"})

    print("\nEstado inicial:")
    print(manager2)

    print("\n💥 Cancelando 'Instalar Paneles Solares'...")
    canceladas = manager2.cancel_task("energia")
    print(f"Misiones canceladas en cascada: {canceladas}")

    print("\nEstado después de la cancelación:")
    print(manager2)

    print("\n" + "=" * 65)
    print("🏁 Demo completado. ¡Que la fuerza del DAG te acompañe!")
    print("=" * 65)
