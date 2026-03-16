"""
Suite de pruebas para la LRU Cache — Módulo 1.

Ejecutar con: pytest test_lru_cache.py -v
"""

import pytest

from lru_cache import LRUCache


class TestLRUCache:
    """Pruebas exhaustivas para la implementación de LRU Cache."""

    def test_basic_get_put(self) -> None:
        """Verifica que las operaciones básicas de inserción y lectura funcionan.

        Se insertan dos pares clave-valor y se comprueba que ambos pueden
        recuperarse correctamente con get().
        """
        cache = LRUCache(2)
        cache.put(1, 10)
        cache.put(2, 20)

        assert cache.get(1) == 10
        assert cache.get(2) == 20

    def test_eviction(self) -> None:
        """Verifica que se desaloja el elemento menos recientemente usado (LRU)
        cuando la cache supera su capacidad.

        Con capacidad 2, al insertar un tercer elemento, el primero (el menos
        recientemente usado) debe ser eliminado y retornar -1.
        """
        cache = LRUCache(2)
        cache.put(1, 10)
        cache.put(2, 20)
        # La cache está llena: [2:20, 1:10]
        # Insertar un tercer elemento debe desalojar key=1 (el LRU)
        cache.put(3, 30)

        assert cache.get(1) == -1, "key=1 debería haber sido desalojada"
        assert cache.get(2) == 20
        assert cache.get(3) == 30

    def test_update_existing_key(self) -> None:
        """Verifica que actualizar una clave existente la mueve al frente (MRU)
        y actualiza su valor sin cambiar el tamaño de la cache.

        Después de actualizar key=1, debería ser la MRU. Al insertar un nuevo
        elemento, key=2 (ahora la LRU) debería ser desalojada, no key=1.
        """
        cache = LRUCache(2)
        cache.put(1, 10)
        cache.put(2, 20)
        # Actualizar key=1: ahora key=1 es MRU, key=2 es LRU
        cache.put(1, 100)

        assert cache.get(1) == 100, "El valor de key=1 debería estar actualizado"

        # Insertar key=3 debe desalojar key=2 (LRU), no key=1
        cache.put(3, 30)
        assert cache.get(2) == -1, "key=2 debería haber sido desalojada"
        assert cache.get(1) == 100
        assert cache.get(3) == 30

    def test_access_order(self) -> None:
        """Verifica que acceder a un elemento con get() cambia el orden de evicción.

        Al consultar key=1 con get(), esta pasa a ser MRU. Luego, al insertar
        un nuevo elemento, key=2 (ahora LRU) es la que se desaloja.
        """
        cache = LRUCache(2)
        cache.put(1, 10)
        cache.put(2, 20)
        # Acceder a key=1 la convierte en MRU → key=2 pasa a ser LRU
        cache.get(1)

        # Insertar key=3 debe desalojar key=2 (LRU)
        cache.put(3, 30)

        assert cache.get(2) == -1, "key=2 debería haber sido desalojada"
        assert cache.get(1) == 10, "key=1 debería seguir en la cache"
        assert cache.get(3) == 30

    def test_capacity_one(self) -> None:
        """Verifica el caso borde de una cache con capacidad 1.

        Con capacidad 1, cada nueva inserción debe desalojar el elemento anterior.
        Solo puede existir un elemento a la vez.
        """
        cache = LRUCache(1)

        cache.put(1, 10)
        assert cache.get(1) == 10

        # Insertar key=2 desaloja key=1
        cache.put(2, 20)
        assert cache.get(1) == -1, "key=1 debería haber sido desalojada"
        assert cache.get(2) == 20

        # Insertar key=3 desaloja key=2
        cache.put(3, 30)
        assert cache.get(2) == -1, "key=2 debería haber sido desalojada"
        assert cache.get(3) == 30

    def test_get_nonexistent(self) -> None:
        """Verifica que buscar una clave inexistente retorna -1.

        Tanto en una cache vacía como en una con elementos, las claves
        no presentes deben retornar -1.
        """
        cache = LRUCache(2)

        # Cache vacía
        assert cache.get(99) == -1

        # Cache con elementos, pero clave no presente
        cache.put(1, 10)
        assert cache.get(99) == -1
        assert cache.get(0) == -1
        assert cache.get(-1) == -1

    def test_large_cache(self) -> None:
        """Prueba de rendimiento con 10,000 operaciones.

        Inserta 10,000 elementos en una cache de capacidad 1,000, luego verifica
        que solo los últimos 1,000 elementos sobreviven. Las operaciones deben
        completarse rápidamente gracias a la complejidad O(1).
        """
        capacity = 1000
        total_ops = 10000
        cache = LRUCache(capacity)

        # Insertar 10,000 elementos
        for i in range(total_ops):
            cache.put(i, i * 10)

        # Solo los últimos 1,000 deben existir (keys 9000-9999)
        for i in range(total_ops - capacity):
            assert cache.get(i) == -1, (
                f"key={i} debería haber sido desalojada"
            )

        for i in range(total_ops - capacity, total_ops):
            assert cache.get(i) == i * 10, (
                f"key={i} debería existir con valor {i * 10}"
            )

    def test_overwrite_value(self) -> None:
        """Verifica que sobrescribir un valor no cambia la capacidad de la cache.

        Al actualizar un elemento existente, el tamaño de la cache no debe
        incrementarse. Todos los elementos originales deben seguir accesibles.
        """
        cache = LRUCache(3)
        cache.put(1, 10)
        cache.put(2, 20)
        cache.put(3, 30)

        # Sobrescribir key=2 (no debe cambiar el tamaño)
        cache.put(2, 200)

        # Todos los elementos deben seguir presentes
        assert cache.get(1) == 10, "key=1 no debería haber sido desalojada"
        assert cache.get(2) == 200, "key=2 debería tener el valor actualizado"
        assert cache.get(3) == 30, "key=3 no debería haber sido desalojada"

        # Verificar que el tamaño interno es correcto
        assert len(cache.cache) == 3

    def test_repr(self) -> None:
        """Verifica que la representación visual de la cache es informativa.

        El método __repr__ debe mostrar la capacidad, el tamaño y los elementos
        en orden de MRU a LRU.
        """
        cache = LRUCache(3)
        representacion = repr(cache)
        assert "capacidad=3" in representacion
        assert "tamaño=0" in representacion

        cache.put(1, 10)
        cache.put(2, 20)
        representacion = repr(cache)
        assert "tamaño=2" in representacion
        assert "2:20" in representacion
        assert "1:10" in representacion

    def test_invalid_capacity(self) -> None:
        """Verifica que se lanza un error al crear una cache con capacidad inválida.

        La capacidad debe ser al menos 1. Valores menores deben lanzar ValueError.
        """
        with pytest.raises(ValueError):
            LRUCache(0)

        with pytest.raises(ValueError):
            LRUCache(-5)

    def test_sequential_evictions(self) -> None:
        """Verifica múltiples evicciones consecutivas en una cache pequeña.

        Con capacidad 2, al insertar 5 elementos secuencialmente, solo los
        dos últimos deben sobrevivir en cada paso.
        """
        cache = LRUCache(2)

        cache.put(1, 10)
        cache.put(2, 20)
        assert cache.get(1) == 10
        assert cache.get(2) == 20

        cache.put(3, 30)  # Desaloja key=1
        assert cache.get(1) == -1
        assert cache.get(2) == 20

        cache.put(4, 40)  # Desaloja key=3 (key=2 fue consultada recientemente)
        assert cache.get(3) == -1
        assert cache.get(2) == 20
        assert cache.get(4) == 40

        cache.put(5, 50)  # Desaloja key=2 (key=4 fue consultada recientemente)
        assert cache.get(2) == -1
        assert cache.get(4) == 40
        assert cache.get(5) == 50
