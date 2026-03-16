"""
Suite de pruebas para el Orquestador de Misiones — DAG & Task Manager.

Ejecutar con: pytest test_task_manager.py -v
"""

import pytest
from task_manager import Task, TaskManager, TaskStatus


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def manager():
    """Crea un TaskManager vacío para cada prueba."""
    return TaskManager()


@pytest.fixture
def manager_con_misiones():
    """
    Crea un TaskManager con un escenario de misiones espaciales.

    Grafo de dependencias:
        inspeccionar → repostar → lanzar
        inspeccionar → verificar → lanzar
        cargar_tripulacion → lanzar
        lanzar → orbitar
    """
    m = TaskManager()
    m.add_task("inspeccionar", "Inspeccionar Tanques", priority=1)
    m.add_task("repostar", "Repostar Combustible", priority=2,
               dependencies={"inspeccionar"})
    m.add_task("verificar", "Verificar Sistemas", priority=3,
               dependencies={"inspeccionar"})
    m.add_task("cargar_tripulacion", "Cargar Tripulación", priority=1)
    m.add_task("lanzar", "Lanzar Nave", priority=5,
               dependencies={"repostar", "verificar", "cargar_tripulacion"})
    m.add_task("orbitar", "Entrar en Órbita", priority=4,
               dependencies={"lanzar"})
    return m


# =============================================================================
# PRUEBAS
# =============================================================================

class TestAddTask:
    """Pruebas para la adición de tareas."""

    def test_add_task(self, manager):
        """Verifica que se puede agregar una tarea básica al sistema."""
        task = manager.add_task("t1", "Misión Alpha", priority=1)

        assert task.id == "t1"
        assert task.name == "Misión Alpha"
        assert task.priority == 1
        assert task.status == TaskStatus.READY  # Sin deps → lista
        assert "t1" in manager.tasks

    def test_add_task_con_dependencias(self, manager):
        """Verifica que una tarea con dependencias pendientes queda en estado PENDING."""
        manager.add_task("t1", "Prerequisito", priority=1)
        task = manager.add_task("t2", "Dependiente", priority=2,
                                dependencies={"t1"})

        assert task.status == TaskStatus.PENDING
        assert "t1" in task.dependencies

    def test_add_task_duplicada(self, manager):
        """Verifica que no se puede agregar una tarea con ID duplicado."""
        manager.add_task("t1", "Misión Alpha")

        with pytest.raises(ValueError, match="ya existe"):
            manager.add_task("t1", "Misión Duplicada")

    def test_add_task_sin_dependencias_es_ready(self, manager):
        """Verifica que una tarea sin dependencias inicia en estado READY."""
        task = manager.add_task("t1", "Tarea Independiente")
        assert task.status == TaskStatus.READY


class TestTopologicalSort:
    """Pruebas para el ordenamiento topológico."""

    def test_topological_sort(self, manager_con_misiones):
        """Verifica que el orden topológico respeta todas las dependencias."""
        orden = manager_con_misiones.get_execution_order()
        posiciones = {task_id: i for i, task_id in enumerate(orden)}

        # inspeccionar debe ir antes que repostar y verificar
        assert posiciones["inspeccionar"] < posiciones["repostar"]
        assert posiciones["inspeccionar"] < posiciones["verificar"]

        # repostar, verificar y cargar_tripulacion deben ir antes que lanzar
        assert posiciones["repostar"] < posiciones["lanzar"]
        assert posiciones["verificar"] < posiciones["lanzar"]
        assert posiciones["cargar_tripulacion"] < posiciones["lanzar"]

        # lanzar debe ir antes que orbitar
        assert posiciones["lanzar"] < posiciones["orbitar"]

    def test_topological_sort_incluye_todas_las_tareas(self, manager_con_misiones):
        """Verifica que el orden topológico incluye todas las tareas del sistema."""
        orden = manager_con_misiones.get_execution_order()
        assert len(orden) == len(manager_con_misiones.tasks)
        assert set(orden) == set(manager_con_misiones.tasks.keys())

    def test_topological_sort_vacio(self, manager):
        """Verifica que un manager vacío retorna una lista vacía."""
        assert manager.get_execution_order() == []


class TestCycleDetection:
    """Pruebas para la detección de ciclos."""

    def test_cycle_detection_sin_ciclo(self, manager_con_misiones):
        """Verifica que un DAG válido no reporta ciclos."""
        assert manager_con_misiones.detect_cycle() is False

    def test_cycle_detection_con_ciclo(self, manager):
        """Verifica que se detecta un ciclo directo entre dos tareas."""
        manager.add_task("a", "Tarea A")
        manager.add_task("b", "Tarea B", dependencies={"a"})
        # Forzamos un ciclo añadiendo manualmente la dependencia inversa
        manager.tasks["a"].dependencies.add("b")

        assert manager.detect_cycle() is True

    def test_cycle_detection_ciclo_largo(self, manager):
        """Verifica que se detecta un ciclo que involucra múltiples nodos (A→B→C→A)."""
        manager.add_task("a", "Tarea A")
        manager.add_task("b", "Tarea B", dependencies={"a"})
        manager.add_task("c", "Tarea C", dependencies={"b"})
        # Cerramos el ciclo: A depende de C
        manager.tasks["a"].dependencies.add("c")

        assert manager.detect_cycle() is True

    def test_topological_sort_con_ciclo_lanza_error(self, manager):
        """Verifica que get_execution_order lanza error si hay un ciclo."""
        manager.add_task("a", "Tarea A")
        manager.add_task("b", "Tarea B", dependencies={"a"})
        manager.tasks["a"].dependencies.add("b")

        with pytest.raises(ValueError, match="[Cc]iclo"):
            manager.get_execution_order()


class TestPriorityQueue:
    """Pruebas para la cola de prioridad."""

    def test_priority_queue(self, manager):
        """Verifica que las tareas se ordenan por prioridad (menor valor = más urgente)."""
        manager.add_task("baja", "Prioridad Baja", priority=10)
        manager.add_task("alta", "Prioridad Alta", priority=1)
        manager.add_task("media", "Prioridad Media", priority=5)

        siguientes = manager.get_next_tasks()

        assert len(siguientes) == 3
        assert siguientes[0].id == "alta"
        assert siguientes[1].id == "media"
        assert siguientes[2].id == "baja"

    def test_priority_queue_misma_prioridad(self, manager):
        """Verifica el desempate por ID cuando las prioridades son iguales."""
        manager.add_task("z_tarea", "Tarea Z", priority=1)
        manager.add_task("a_tarea", "Tarea A", priority=1)

        siguientes = manager.get_next_tasks()

        assert len(siguientes) == 2
        # Desempate alfabético por ID
        assert siguientes[0].id == "a_tarea"
        assert siguientes[1].id == "z_tarea"

    def test_priority_queue_no_incluye_pendientes(self, manager):
        """Verifica que las tareas PENDING no aparecen en la cola de prioridad."""
        manager.add_task("base", "Base", priority=1)
        manager.add_task("dep", "Dependiente", priority=1,
                         dependencies={"base"})

        siguientes = manager.get_next_tasks()

        # Solo 'base' está READY; 'dep' está PENDING
        assert len(siguientes) == 1
        assert siguientes[0].id == "base"


class TestCascadeCancellation:
    """Pruebas para la cancelación en cascada."""

    def test_cascade_cancellation(self, manager):
        """Verifica que cancelar una tarea cancela también todas las dependientes downstream."""
        manager.add_task("a", "Tarea A", priority=1)
        manager.add_task("b", "Tarea B", priority=2, dependencies={"a"})
        manager.add_task("c", "Tarea C", priority=3, dependencies={"b"})
        manager.add_task("d", "Tarea D", priority=4, dependencies={"c"})

        canceladas = manager.cancel_task("a")

        # Toda la cadena debe cancelarse: a → b → c → d
        assert set(canceladas) == {"a", "b", "c", "d"}
        for task_id in ["a", "b", "c", "d"]:
            assert manager.tasks[task_id].status == TaskStatus.CANCELLED

    def test_cascade_no_afecta_completadas(self, manager):
        """Verifica que la cancelación en cascada no afecta a tareas ya completadas."""
        manager.add_task("a", "Tarea A", priority=1)
        manager.add_task("b", "Tarea B", priority=2, dependencies={"a"})
        manager.add_task("c", "Tarea C", priority=3, dependencies={"a"})

        # Completamos la tarea 'a' y luego 'b' depende de algo más que cancelamos
        manager.complete_task("a")
        manager.complete_task("b")

        # Intentamos cancelar 'a' — ya completada, no se cancela
        canceladas = manager.cancel_task("a")

        assert canceladas == []  # 'a' ya está completada
        assert manager.tasks["a"].status == TaskStatus.COMPLETED
        assert manager.tasks["b"].status == TaskStatus.COMPLETED

    def test_cascade_cancellation_ramificada(self, manager):
        """
        Verifica la cancelación en cascada con un DAG ramificado.

        Grafo:  a → b → d
                a → c → d
                      → e
        Cancelar 'a' debe cancelar b, c, d, e.
        """
        manager.add_task("a", "Tarea A", priority=1)
        manager.add_task("b", "Tarea B", priority=2, dependencies={"a"})
        manager.add_task("c", "Tarea C", priority=2, dependencies={"a"})
        manager.add_task("d", "Tarea D", priority=3, dependencies={"b", "c"})
        manager.add_task("e", "Tarea E", priority=3, dependencies={"c"})

        canceladas = manager.cancel_task("a")

        assert set(canceladas) == {"a", "b", "c", "d", "e"}

    def test_cancel_tarea_inexistente(self, manager):
        """Verifica que cancelar una tarea que no existe lanza un KeyError."""
        with pytest.raises(KeyError, match="no existe"):
            manager.cancel_task("fantasma")


class TestCompleteTaskFlow:
    """Pruebas para el flujo completo de completar tareas."""

    def test_complete_task_flow(self, manager):
        """Verifica el ciclo de vida completo: PENDING → READY → COMPLETED."""
        manager.add_task("a", "Tarea A", priority=1)
        manager.add_task("b", "Tarea B", priority=2, dependencies={"a"})

        # 'a' está lista, 'b' está pendiente
        assert manager.tasks["a"].status == TaskStatus.READY
        assert manager.tasks["b"].status == TaskStatus.PENDING

        # Completamos 'a'
        manager.complete_task("a")
        assert manager.tasks["a"].status == TaskStatus.COMPLETED

        # Ahora 'b' debe estar lista
        assert manager.tasks["b"].status == TaskStatus.READY

        # Completamos 'b'
        manager.complete_task("b")
        assert manager.tasks["b"].status == TaskStatus.COMPLETED

    def test_complete_task_inexistente(self, manager):
        """Verifica que completar una tarea inexistente lanza un KeyError."""
        with pytest.raises(KeyError, match="no existe"):
            manager.complete_task("fantasma")

    def test_complete_task_ya_completada(self, manager):
        """Verifica que completar una tarea ya completada lanza un ValueError."""
        manager.add_task("a", "Tarea A")
        manager.complete_task("a")

        with pytest.raises(ValueError, match="ya está completada"):
            manager.complete_task("a")

    def test_complete_task_cancelada(self, manager):
        """Verifica que no se puede completar una tarea cancelada."""
        manager.add_task("a", "Tarea A")
        manager.cancel_task("a")

        with pytest.raises(ValueError, match="cancelada"):
            manager.complete_task("a")


class TestGetNextTasks:
    """Pruebas para obtener las siguientes tareas listas."""

    def test_get_next_tasks(self, manager_con_misiones):
        """Verifica que solo se retornan las tareas con estado READY."""
        siguientes = manager_con_misiones.get_next_tasks()
        ids_siguientes = [t.id for t in siguientes]

        # Solo las tareas sin dependencias o con todas completadas
        assert "inspeccionar" in ids_siguientes
        assert "cargar_tripulacion" in ids_siguientes

        # Las que tienen dependencias pendientes NO deben aparecer
        assert "repostar" not in ids_siguientes
        assert "lanzar" not in ids_siguientes
        assert "orbitar" not in ids_siguientes

    def test_get_next_tasks_despues_de_completar(self, manager_con_misiones):
        """Verifica que al completar tareas, las dependientes se vuelven disponibles."""
        # Completamos las tareas iniciales
        manager_con_misiones.complete_task("inspeccionar")
        manager_con_misiones.complete_task("cargar_tripulacion")

        siguientes = manager_con_misiones.get_next_tasks()
        ids_siguientes = [t.id for t in siguientes]

        # Ahora repostar y verificar deberían estar listas
        assert "repostar" in ids_siguientes
        assert "verificar" in ids_siguientes

        # Lanzar aún no (falta repostar y verificar)
        assert "lanzar" not in ids_siguientes

    def test_get_next_tasks_vacio(self, manager):
        """Verifica que un manager vacío retorna lista vacía."""
        assert manager.get_next_tasks() == []

    def test_get_next_tasks_todas_completadas(self, manager):
        """Verifica que no hay tareas listas cuando todas están completadas."""
        manager.add_task("a", "Tarea A")
        manager.complete_task("a")

        assert manager.get_next_tasks() == []


class TestComplexDAG:
    """Pruebas con grafos DAG complejos."""

    def test_complex_dag(self, manager):
        """
        Verifica el funcionamiento con un DAG complejo de múltiples caminos.

        Grafo:
            a ──→ c ──→ e ──→ f
            b ──→ c
            b ──→ d ──→ f
        """
        manager.add_task("a", "Alpha", priority=1)
        manager.add_task("b", "Bravo", priority=2)
        manager.add_task("c", "Charlie", priority=3, dependencies={"a", "b"})
        manager.add_task("d", "Delta", priority=2, dependencies={"b"})
        manager.add_task("e", "Echo", priority=4, dependencies={"c"})
        manager.add_task("f", "Foxtrot", priority=5, dependencies={"e", "d"})

        # Verificar orden topológico
        orden = manager.get_execution_order()
        pos = {tid: i for i, tid in enumerate(orden)}

        assert pos["a"] < pos["c"]
        assert pos["b"] < pos["c"]
        assert pos["b"] < pos["d"]
        assert pos["c"] < pos["e"]
        assert pos["e"] < pos["f"]
        assert pos["d"] < pos["f"]

        # Verificar tareas listas inicialmente (sin dependencias)
        siguientes = manager.get_next_tasks()
        ids_sig = [t.id for t in siguientes]
        assert set(ids_sig) == {"a", "b"}

        # Completar 'a' y 'b' → 'c' y 'd' listas
        manager.complete_task("a")
        manager.complete_task("b")
        siguientes = manager.get_next_tasks()
        ids_sig = [t.id for t in siguientes]
        assert "c" in ids_sig
        assert "d" in ids_sig

    def test_complex_dag_cancelacion_parcial(self, manager):
        """
        Verifica que la cancelación solo afecta las ramas dependientes.

        Grafo:  a → c → e
                b → d → e

        Cancelar 'a' cancela 'c'. 'e' también se cancela porque depende de 'c'.
        Pero 'b' y 'd' no se afectan.
        """
        manager.add_task("a", "Alpha", priority=1)
        manager.add_task("b", "Bravo", priority=1)
        manager.add_task("c", "Charlie", priority=2, dependencies={"a"})
        manager.add_task("d", "Delta", priority=2, dependencies={"b"})
        manager.add_task("e", "Echo", priority=3, dependencies={"c", "d"})

        canceladas = manager.cancel_task("a")

        assert "a" in canceladas
        assert "c" in canceladas
        assert "e" in canceladas
        # 'b' y 'd' no deben estar canceladas
        assert "b" not in canceladas
        assert "d" not in canceladas
        assert manager.tasks["b"].status == TaskStatus.READY
        assert manager.tasks["d"].status == TaskStatus.PENDING  # dep 'b' no completada


class TestIndependentTasks:
    """Pruebas con tareas independientes (sin dependencias entre sí)."""

    def test_independent_tasks(self, manager):
        """Verifica que tareas sin dependencias están todas listas inmediatamente."""
        manager.add_task("t1", "Misión Alfa", priority=3)
        manager.add_task("t2", "Misión Beta", priority=1)
        manager.add_task("t3", "Misión Gamma", priority=2)

        # Todas deben estar READY
        for task in manager.tasks.values():
            assert task.status == TaskStatus.READY

        # get_next_tasks retorna todas, ordenadas por prioridad
        siguientes = manager.get_next_tasks()
        assert len(siguientes) == 3
        assert siguientes[0].id == "t2"   # prioridad 1
        assert siguientes[1].id == "t3"   # prioridad 2
        assert siguientes[2].id == "t1"   # prioridad 3

    def test_independent_tasks_completar_cualquiera(self, manager):
        """Verifica que las tareas independientes se pueden completar en cualquier orden."""
        manager.add_task("t1", "Misión Alfa", priority=3)
        manager.add_task("t2", "Misión Beta", priority=1)
        manager.add_task("t3", "Misión Gamma", priority=2)

        # Completar en orden inverso de prioridad
        manager.complete_task("t1")
        manager.complete_task("t3")
        manager.complete_task("t2")

        for task in manager.tasks.values():
            assert task.status == TaskStatus.COMPLETED

    def test_independent_tasks_topological_sort(self, manager):
        """Verifica que el orden topológico de tareas independientes incluye todas."""
        manager.add_task("t1", "Misión Alfa")
        manager.add_task("t2", "Misión Beta")
        manager.add_task("t3", "Misión Gamma")

        orden = manager.get_execution_order()
        assert set(orden) == {"t1", "t2", "t3"}


class TestAddDependency:
    """Pruebas para agregar dependencias entre tareas existentes."""

    def test_add_dependency(self, manager):
        """Verifica que se puede agregar una dependencia entre tareas existentes."""
        manager.add_task("a", "Tarea A")
        manager.add_task("b", "Tarea B")

        # Ambas deberían estar READY
        assert manager.tasks["b"].status == TaskStatus.READY

        manager.add_dependency("b", "a")

        # Ahora 'b' depende de 'a', y como 'a' no está completada, 'b' → PENDING
        assert "a" in manager.tasks["b"].dependencies
        assert "b" in manager.dependents["a"]

    def test_add_dependency_tarea_inexistente(self, manager):
        """Verifica que agregar dependencia con tarea inexistente lanza KeyError."""
        manager.add_task("a", "Tarea A")

        with pytest.raises(KeyError):
            manager.add_dependency("a", "fantasma")

        with pytest.raises(KeyError):
            manager.add_dependency("fantasma", "a")
