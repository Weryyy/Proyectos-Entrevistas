"""
Módulo 1: LRU Cache — Implementación desde cero.

Una LRU Cache (Least Recently Used Cache) almacena un número limitado de elementos
y descarta el menos recientemente usado cuando se alcanza la capacidad máxima.

Estructura interna: HashMap (dict) + Lista Doblemente Enlazada.
Todas las operaciones son O(1).

Lore: Este es el sistema de memoria de navegación de una nave espacial IA.
La nave solo puede recordar N coordenadas recientes. Cuando la memoria está llena,
la coordenada menos recientemente consultada se olvida para siempre.
"""


class Node:
    """
    Nodo de la lista doblemente enlazada.

    ¿Por qué una lista DOBLEMENTE enlazada y no simplemente enlazada?
    Porque necesitamos eliminar nodos en O(1). Para eliminar un nodo de una lista
    simplemente enlazada necesitaríamos recorrerla hasta encontrar el nodo anterior → O(n).
    Con enlaces en ambas direcciones (prev y next), podemos desenlazar cualquier nodo
    instantáneamente sin recorrer nada.

    Cada nodo almacena tanto la clave (key) como el valor (value).
    ¿Por qué guardar la clave si ya la tenemos en el hashmap?
    Porque cuando hacemos evicción, necesitamos saber qué clave eliminar del hashmap,
    y solo tenemos acceso al nodo (el último de la lista). Sin la clave almacenada
    en el nodo, tendríamos que recorrer todo el hashmap para encontrarla → O(n).
    """

    __slots__ = ("key", "value", "prev", "next")

    def __init__(self, key: int = 0, value: int = 0) -> None:
        self.key = key
        self.value = value
        self.prev: "Node | None" = None
        self.next: "Node | None" = None

    def __repr__(self) -> str:
        return f"Node(key={self.key}, value={self.value})"


class LRUCache:
    """
    LRU Cache con operaciones O(1) para get y put.

    Arquitectura interna:
    ┌──────────────────────────────────────────────────────┐
    │  HashMap: { key → Node }   → acceso directo O(1)    │
    │                                                      │
    │  Lista doblemente enlazada con centinelas:           │
    │  HEAD ⟷ [MRU] ⟷ [···] ⟷ [LRU] ⟷ TAIL              │
    └──────────────────────────────────────────────────────┘

    Los nodos centinela (HEAD y TAIL) son nodos "fantasma" que simplifican el código:
    nunca contienen datos reales, solo sirven como anclas fijas de la lista.
    Sin ellos, tendríamos que manejar muchos casos borde (lista vacía, un solo
    elemento, etc.) con condicionales adicionales.
    """

    def __init__(self, capacity: int) -> None:
        """
        Inicializa la cache con una capacidad máxima.

        Args:
            capacity: Número máximo de elementos que la cache puede almacenar.
                      Debe ser >= 1.
        """
        if capacity < 1:
            raise ValueError("La capacidad debe ser al menos 1")

        self.capacity = capacity
        # El hashmap: clave → nodo. Nos da acceso O(1) a cualquier nodo.
        self.cache: dict[int, Node] = {}

        # Centinelas de la lista doblemente enlazada.
        # Estos nodos nunca se eliminan ni contienen datos reales.
        # Simplifican enormemente la lógica de inserción/eliminación.
        self.head = Node()  # Centinela izquierdo (antes del MRU)
        self.tail = Node()  # Centinela derecho (después del LRU)

        # Conectar los centinelas entre sí (lista vacía inicial)
        self.head.next = self.tail
        self.tail.prev = self.head

    def get(self, key: int) -> int:
        """
        Obtiene el valor asociado a una clave.

        Si la clave existe:
          1. Mueve el nodo al frente (ahora es el más recientemente usado).
          2. Retorna el valor.
        Si la clave no existe:
          Retorna -1.

        Complejidad: O(1) — búsqueda en hashmap + reubicación en lista.

        Args:
            key: La clave a buscar.

        Returns:
            El valor asociado a la clave, o -1 si no existe.
        """
        if key not in self.cache:
            return -1

        node = self.cache[key]
        # Mover al frente: este nodo acaba de ser "usado"
        self._remove(node)
        self._add_to_front(node)
        return node.value

    def put(self, key: int, value: int) -> None:
        """
        Inserta o actualiza un par clave-valor en la cache.

        Casos:
          1. La clave ya existe → actualizar valor y mover al frente.
          2. La clave no existe y hay espacio → insertar al frente.
          3. La clave no existe y NO hay espacio → eliminar el LRU (último
             antes de TAIL), luego insertar al frente.

        Complejidad: O(1) — todas las sub-operaciones son O(1).

        Args:
            key: La clave del elemento.
            value: El valor del elemento.
        """
        if key in self.cache:
            # Caso 1: La clave ya existe. Actualizar valor y mover al frente.
            node = self.cache[key]
            node.value = value
            self._remove(node)
            self._add_to_front(node)
        else:
            # Caso 2/3: Clave nueva.
            if len(self.cache) >= self.capacity:
                # Caso 3: Cache llena. Eliminar el LRU (el nodo justo antes de TAIL).
                lru_node = self.tail.prev
                assert lru_node is not None and lru_node is not self.head
                self._remove(lru_node)
                del self.cache[lru_node.key]

            # Crear nuevo nodo e insertarlo al frente
            new_node = Node(key, value)
            self.cache[key] = new_node
            self._add_to_front(new_node)

    def _remove(self, node: Node) -> None:
        """
        Elimina (desenlaza) un nodo de la lista doblemente enlazada.

        Esta operación es O(1) porque tenemos acceso directo a los vecinos
        del nodo gracias a los punteros prev y next.

        Antes:  ... ⟷ A ⟷ [node] ⟷ B ⟷ ...
        Después: ... ⟷ A ⟷ B ⟷ ...

        El nodo no se destruye; solo se desenlaza. Esto permite reutilizarlo
        al reinsertarlo en otra posición.

        Args:
            node: El nodo a desenlazar de la lista.
        """
        prev_node = node.prev
        next_node = node.next
        assert prev_node is not None and next_node is not None
        prev_node.next = next_node
        next_node.prev = prev_node

    def _add_to_front(self, node: Node) -> None:
        """
        Inserta un nodo al frente de la lista (justo después de HEAD).

        El frente de la lista representa el elemento más recientemente usado (MRU).

        Antes:  HEAD ⟷ [old_first] ⟷ ...
        Después: HEAD ⟷ [node] ⟷ [old_first] ⟷ ...

        Complejidad: O(1) — solo se modifican 4 punteros.

        Args:
            node: El nodo a insertar al frente.
        """
        # El nodo que actualmente está al frente
        first_node = self.head.next
        assert first_node is not None

        # Insertar el nuevo nodo entre HEAD y el primer nodo actual
        node.prev = self.head
        node.next = first_node
        self.head.next = node
        first_node.prev = node

    def __repr__(self) -> str:
        """
        Representación visual del estado actual de la cache.

        Muestra los elementos en orden de más recientemente usado (izquierda)
        a menos recientemente usado (derecha).
        """
        elements = []
        current = self.head.next
        while current is not None and current != self.tail:
            elements.append(f"{current.key}:{current.value}")
            current = current.next

        items_str = " ⟷ ".join(elements) if elements else "(vacía)"
        return (
            f"LRUCache(capacidad={self.capacity}, "
            f"tamaño={len(self.cache)}, "
            f"elementos=[MRU] {items_str} [LRU])"
        )


# ---------------------------------------------------------------------------
# Ejemplo de uso interactivo
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 65)
    print("  🚀 Sistema de Memoria de Navegación — Nave Espacial IA")
    print("=" * 65)
    print()

    # Crear una cache con capacidad para 3 coordenadas
    memoria = LRUCache(3)
    print(f"Memoria inicializada: {memoria}")
    print()

    # La nave descubre nuevas coordenadas
    print("📍 Registrando coordenada Alpha (key=1, value=100)...")
    memoria.put(1, 100)
    print(f"   Estado: {memoria}")

    print("📍 Registrando coordenada Beta (key=2, value=200)...")
    memoria.put(2, 200)
    print(f"   Estado: {memoria}")

    print("📍 Registrando coordenada Gamma (key=3, value=300)...")
    memoria.put(3, 300)
    print(f"   Estado: {memoria}")
    print()

    # Consultar una coordenada (se mueve al frente)
    print("🔍 Consultando coordenada Alpha (key=1)...")
    valor = memoria.get(1)
    print(f"   Valor obtenido: {valor}")
    print(f"   Estado: {memoria}")
    print("   (Alpha se movió al frente por ser consultada)")
    print()

    # Registrar nueva coordenada — ¡memoria llena! Se elimina la LRU
    print("📍 Registrando coordenada Delta (key=4, value=400)...")
    print("   ⚠️  Memoria llena. Se olvida la coordenada menos usada (Beta).")
    memoria.put(4, 400)
    print(f"   Estado: {memoria}")
    print()

    # Intentar consultar la coordenada eliminada
    print("🔍 Intentando consultar coordenada Beta (key=2)...")
    valor = memoria.get(2)
    print(f"   Valor obtenido: {valor}  (Beta fue olvidada)")
    print()

    print("=" * 65)
    print("  ✅ Sistema de memoria funcionando correctamente.")
    print("=" * 65)
