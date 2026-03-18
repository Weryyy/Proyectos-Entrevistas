"""
Módulo 11: Motor de Búsqueda Semántica — Vector Store.

Implementaciones de búsqueda de vecinos más cercanos:
  1. VectorStore      — Búsqueda exacta por fuerza bruta O(n·d)
  2. KDTreeVectorStore — KD-Tree para O(d·log n) promedio
  3. LSHVectorStore   — Locality Sensitive Hashing O(1) aproximado

Solo usa la biblioteca estándar de Python (sin numpy, sin scipy).

Lore: Eres el arquitecto del motor de búsqueda de la Biblioteca Alienígena.
Los sabios del universo depositan aquí su conocimiento en forma de vectores
de alta dimensión. Tu misión: encontrar el conocimiento más relevante en
microsegundos, aunque la biblioteca crezca hasta contener billones de documentos.
"""

import heapq
import math
import random
from typing import Any, Dict, List, Optional, Tuple


# ─────────────────────────────────────────────────────────────────────────────
# Funciones de distancia y similitud
# ─────────────────────────────────────────────────────────────────────────────

def dot_product(a: List[float], b: List[float]) -> float:
    """Producto punto entre dos vectores."""
    return sum(x * y for x, y in zip(a, b))


def cosine_similarity(a: List[float], b: List[float]) -> float:
    """
    Similitud coseno entre dos vectores: cos(θ) = (a·b) / (‖a‖·‖b‖).
    Rango: [-1, 1]. 1 = idénticos, 0 = ortogonales, -1 = opuestos.
    Devuelve 0.0 si alguno de los vectores es el vector cero.
    """
    dot = dot_product(a, b)
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)


def euclidean_distance(a: List[float], b: List[float]) -> float:
    """Distancia euclidiana: √Σ(aᵢ - bᵢ)²"""
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def normalize(v: List[float]) -> List[float]:
    """Devuelve el vector unitario (norma = 1). Si ‖v‖=0, devuelve v."""
    norm = math.sqrt(sum(x * x for x in v))
    if norm == 0.0:
        return list(v)
    return [x / norm for x in v]


# ─────────────────────────────────────────────────────────────────────────────
# 1. VectorStore — Fuerza bruta exacta
# ─────────────────────────────────────────────────────────────────────────────

class VectorStore:
    """
    Motor de búsqueda exacto por fuerza bruta.

    Complejidad:
      add()    → O(1)
      search() → O(n·d)  donde n = nº vectores, d = dimensión
      delete() → O(1)

    Métricas soportadas: 'cosine' (similitud, mayor=mejor),
                         'euclidean' (distancia, menor=mejor).
    """

    def __init__(self, dim: int) -> None:
        self.dim = dim
        self._vectors: Dict[str, Tuple[List[float], Dict[str, Any]]] = {}

    def add(
        self,
        id: str,
        vector: List[float],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Añade o actualiza un vector."""
        if len(vector) != self.dim:
            raise ValueError(
                f"Vector de dimensión {len(vector)}, se esperaba {self.dim}"
            )
        self._vectors[id] = (list(vector), metadata or {})

    def delete(self, id: str) -> bool:
        """Elimina un vector. Devuelve True si existía."""
        if id in self._vectors:
            del self._vectors[id]
            return True
        return False

    def search(
        self,
        query: List[float],
        k: int = 5,
        metric: str = "cosine",
    ) -> List[Tuple[str, float, Dict[str, Any]]]:
        """
        Devuelve los k vecinos más cercanos.
        Retorna lista de (id, score, metadata) ordenada de mejor a peor.
        Para 'cosine': mayor score = más similar.
        Para 'euclidean': menor score = más cercano.
        """
        if not self._vectors:
            return []

        scored: List[Tuple[str, float, Dict[str, Any]]] = []
        for id_, (vec, meta) in self._vectors.items():
            if metric == "cosine":
                score = cosine_similarity(query, vec)
                scored.append((id_, score, meta))
            elif metric == "euclidean":
                score = euclidean_distance(query, vec)
                scored.append((id_, score, meta))
            else:
                raise ValueError(f"Métrica desconocida: '{metric}'")

        if metric == "cosine":
            scored.sort(key=lambda x: x[1], reverse=True)
        else:
            scored.sort(key=lambda x: x[1])

        return scored[:k]

    def __len__(self) -> int:
        return len(self._vectors)


# ─────────────────────────────────────────────────────────────────────────────
# 2. KDTreeVectorStore — KD-Tree para búsqueda eficiente
# ─────────────────────────────────────────────────────────────────────────────

class KDTreeNode:
    """Nodo de un KD-Tree."""

    __slots__ = ('point', 'id', 'metadata', 'left', 'right')

    def __init__(
        self,
        point: List[float],
        id: str,
        metadata: Dict[str, Any],
        left: Optional['KDTreeNode'] = None,
        right: Optional['KDTreeNode'] = None,
    ) -> None:
        self.point = point
        self.id = id
        self.metadata = metadata
        self.left = left
        self.right = right


class KDTreeVectorStore:
    """
    Motor de búsqueda basado en KD-Tree (distancia euclidiana).

    El índice debe construirse explícitamente con build_index()
    tras añadir todos los vectores (o tras actualizaciones por lote).

    Complejidad:
      add()         → O(1)  (acumula puntos)
      build_index() → O(n·d·log n)
      search()      → O(d·log n) promedio, O(n·d) peor caso
    """

    def __init__(self, dim: int) -> None:
        self.dim = dim
        self._points: List[Tuple[str, List[float], Dict[str, Any]]] = []
        self._root: Optional[KDTreeNode] = None

    def add(
        self,
        id: str,
        vector: List[float],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Acumula un punto. Llama a build_index() para actualizar el árbol."""
        self._points.append((id, list(vector), metadata or {}))

    def build_index(self) -> None:
        """Construye (o reconstruye) el KD-Tree desde los puntos acumulados."""
        self._root = self._build(list(self._points), depth=0)

    def _build(
        self,
        points: List[Tuple[str, List[float], Dict[str, Any]]],
        depth: int,
    ) -> Optional[KDTreeNode]:
        if not points:
            return None
        axis = depth % self.dim
        points.sort(key=lambda p: p[1][axis])
        mid = len(points) // 2
        return KDTreeNode(
            point=points[mid][1],
            id=points[mid][0],
            metadata=points[mid][2],
            left=self._build(points[:mid], depth + 1),
            right=self._build(points[mid + 1:], depth + 1),
        )

    def search(
        self,
        query: List[float],
        k: int = 5,
    ) -> List[Tuple[str, float, Dict[str, Any]]]:
        """
        Devuelve los k vecinos más cercanos (distancia euclidiana).
        Retorna lista de (id, distancia, metadata) ordenada de menor a mayor.
        Requiere haber llamado build_index() antes.
        """
        if self._root is None:
            return []
        # max-heap de (-dist, id, meta) para mantener los k mejores
        heap: List[Tuple[float, str, Dict[str, Any]]] = []
        self._search_knn(self._root, query, k, 0, heap)
        # Convertir y ordenar por distancia ascendente
        result = [
            (id_, -neg_dist, meta)
            for neg_dist, id_, meta in heap
        ]
        result.sort(key=lambda x: x[1])
        return result

    def _search_knn(
        self,
        node: Optional[KDTreeNode],
        query: List[float],
        k: int,
        depth: int,
        heap: List,
    ) -> None:
        if node is None:
            return

        dist = euclidean_distance(query, node.point)

        if len(heap) < k:
            heapq.heappush(heap, (-dist, node.id, node.metadata))
        elif dist < -heap[0][0]:
            heapq.heapreplace(heap, (-dist, node.id, node.metadata))

        axis = depth % self.dim
        diff = query[axis] - node.point[axis]
        near = node.left if diff <= 0 else node.right
        far = node.right if diff <= 0 else node.left

        self._search_knn(near, query, k, depth + 1, heap)

        # Explorar lado lejano sólo si puede contener un vecino más cercano
        worst_dist = -heap[0][0] if heap else float('inf')
        if len(heap) < k or abs(diff) < worst_dist:
            self._search_knn(far, query, k, depth + 1, heap)

    def __len__(self) -> int:
        return len(self._points)


# ─────────────────────────────────────────────────────────────────────────────
# 3. LSHVectorStore — Locality Sensitive Hashing (aproximado)
# ─────────────────────────────────────────────────────────────────────────────

class LSHVectorStore:
    """
    Motor de búsqueda aproximada usando Locality Sensitive Hashing (LSH)
    con hiperplanos aleatorios (Random Projection LSH para similitud coseno).

    Idea: dos vectores similares (ángulo pequeño) tienen alta probabilidad de
    caer en el mismo lado de un hiperplano aleatorio → mismo hash bucket.

    Con múltiples tablas de hash se aumenta el recall.

    Complejidad:
      add()    → O(n_tables · n_planes · d)
      search() → O(candidatos · d)  donde candidatos << n en el caso feliz
    """

    def __init__(
        self,
        dim: int,
        n_planes: int = 10,
        n_tables: int = 5,
        seed: int = 42,
    ) -> None:
        self.dim = dim
        self.n_planes = n_planes
        self.n_tables = n_tables

        rng = random.Random(seed)

        # Hiperplanos aleatorios: n_tables × n_planes × dim
        self._hyperplanes: List[List[List[float]]] = [
            [
                [rng.gauss(0, 1) for _ in range(dim)]
                for _ in range(n_planes)
            ]
            for _ in range(n_tables)
        ]

        # Tablas de hash: lista de dicts {bits_tuple → [ids]}
        self._tables: List[Dict[tuple, List[str]]] = [
            {} for _ in range(n_tables)
        ]

        # Almacén de vectores: id → (vector, metadata)
        self._store: Dict[str, Tuple[List[float], Dict[str, Any]]] = {}

    def _hash(self, vector: List[float], table_idx: int) -> tuple:
        """Proyecta el vector en el espacio de bits usando hiperplanos."""
        planes = self._hyperplanes[table_idx]
        return tuple(
            1 if dot_product(vector, plane) >= 0 else 0
            for plane in planes
        )

    def add(
        self,
        id: str,
        vector: List[float],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Indexa un vector en todas las tablas LSH."""
        self._store[id] = (list(vector), metadata or {})
        for i in range(self.n_tables):
            bucket = self._hash(vector, i)
            if bucket not in self._tables[i]:
                self._tables[i][bucket] = []
            if id not in self._tables[i][bucket]:
                self._tables[i][bucket].append(id)

    def search(
        self,
        query: List[float],
        k: int = 5,
    ) -> List[Tuple[str, float, Dict[str, Any]]]:
        """
        Búsqueda aproximada de vecinos más cercanos (similitud coseno).
        Retorna lista de (id, similitud, metadata) ordenada de mayor a menor.
        Si no encuentra candidatos por LSH, usa fuerza bruta como fallback.
        """
        candidates: set = set()
        for i in range(self.n_tables):
            bucket = self._hash(query, i)
            for id_ in self._tables[i].get(bucket, []):
                candidates.add(id_)

        # Fallback: si no hay candidatos, explorar todo
        if not candidates:
            candidates = set(self._store.keys())

        scored = []
        for id_ in candidates:
            vec, meta = self._store[id_]
            sim = cosine_similarity(query, vec)
            scored.append((id_, sim, meta))

        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:k]

    def __len__(self) -> int:
        return len(self._store)
