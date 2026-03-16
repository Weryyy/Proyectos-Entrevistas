# Módulo 1: El Corazón del Rendimiento — LRU Cache

## 🧠 Concepto Técnico

Una **LRU Cache** (Least Recently Used Cache) es una estructura de datos que almacena
un número limitado de elementos y, cuando se alcanza la capacidad máxima, **descarta
el elemento que no se ha usado durante más tiempo**.

### ¿Por qué es importante?

En sistemas reales — bases de datos, navegadores, sistemas operativos — la memoria es
finita. Una LRU Cache permite mantener los datos más relevantes (los usados recientemente)
en memoria rápida, sacrificando los que llevan más tiempo sin accederse.

### Estructura Interna: HashMap + Lista Doblemente Enlazada

Para lograr **O(1)** en todas las operaciones necesitamos combinar dos estructuras:

```
┌─────────────────────────────────────────────────────────────┐
│                        HashMap (dict)                       │
│  key → Node    Acceso directo al nodo en O(1)               │
├─────────────────────────────────────────────────────────────┤
│                Lista Doblemente Enlazada                    │
│                                                             │
│  HEAD ⟷ [MRU] ⟷ [···] ⟷ [LRU] ⟷ TAIL                     │
│  (sentinel)                         (sentinel)              │
│                                                             │
│  • Insertar/eliminar nodos en O(1)                          │
│  • El frente = más recientemente usado (MRU)                │
│  • El final  = menos recientemente usado (LRU)              │
└─────────────────────────────────────────────────────────────┘
```

- **HashMap (diccionario):** Nos da acceso instantáneo a cualquier nodo por su clave.
- **Lista doblemente enlazada:** Nos permite reordenar elementos en O(1) sin recorrer
  toda la estructura. Los nodos centinela (HEAD y TAIL) simplifican los casos borde.

### ¿Por qué no basta con solo un diccionario?

Un diccionario no mantiene orden de acceso. Necesitaríamos recorrer todos los elementos
para encontrar el menos usado → O(n). La lista enlazada resuelve esto.

### ¿Por qué no basta con solo una lista?

Buscar un elemento en una lista es O(n). El diccionario nos da acceso directo al nodo.

**La combinación de ambos nos da lo mejor de los dos mundos: O(1) para todo.**

---

## 🚀 Lore: La Nave Espacial de Navegación IA

> *Imagina que eres el ingeniero principal de una nave espacial controlada por una IA.
> La nave viaja por el cosmos y debe recordar las coordenadas de navegación recientes
> para poder hacer correcciones de rumbo instantáneas.*
>
> *Sin embargo, la memoria de navegación de la nave tiene un límite: solo puede almacenar
> **N** coordenadas. Cada vez que la IA consulta una coordenada, esa coordenada se marca
> como "recientemente usada" y se mueve al frente de la memoria.*
>
> *Cuando la nave descubre una nueva coordenada y la memoria está llena, debe olvidar
> la coordenada que lleva más tiempo sin ser consultada — la menos recientemente usada.*
>
> *Tu misión: implementar el sistema de memoria de la nave para que todas las operaciones
> de consulta y almacenamiento sean instantáneas — O(1). La supervivencia de la tripulación
> depende de ello.*

---

## 📊 Tabla de Complejidad

| Operación         | Tiempo | Espacio | Descripción                                        |
|-------------------|--------|---------|----------------------------------------------------|
| `get(key)`        | O(1)   | O(1)    | Busca en hashmap + mueve nodo al frente de la lista |
| `put(key, value)` | O(1)   | O(1)    | Inserta/actualiza + posible evicción del LRU        |
| `_remove(node)`   | O(1)   | O(1)    | Desenlaza un nodo de la lista doblemente enlazada    |
| `_add_to_front(node)` | O(1) | O(1)  | Enlaza un nodo justo después del centinela HEAD     |
| **Espacio total** | —      | O(n)    | Donde n = capacidad máxima de la cache              |

---

## ▶️ Cómo Ejecutar

### Ejecución directa (ejemplo interactivo)

```bash
cd main/modulo-1-lru-cache/codigo/python
python lru_cache.py
```

### Ejecutar las pruebas

```bash
cd main/modulo-1-lru-cache/codigo/python
pytest test_lru_cache.py -v
```

### Requisitos

- Python 3.8+
- pytest (`pip install pytest`)

---

## 📁 Estructura del Módulo

```
modulo-1-lru-cache/
├── README.md                          # Este archivo
└── codigo/
    └── python/
        ├── lru_cache.py               # Implementación de la LRU Cache
        └── test_lru_cache.py          # Suite de pruebas con pytest
```
