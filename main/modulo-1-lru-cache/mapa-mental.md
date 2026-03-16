# 🧠 Mapa Mental — LRU Cache

## ⏱ Tiempo estimado: 8–12 horas

```
                        ╔══════════════════════╗
                        ║     LRU  CACHE       ║
                        ║  (Least Recently Used)║
                        ╚═══════════╤══════════╝
                                    │
        ┌───────────────┬───────────┼───────────┬────────────────┐
        ▼               ▼           ▼           ▼                ▼
  ┌───────────┐  ┌────────────┐ ┌────────┐ ┌──────────┐  ┌────────────┐
  │PREREQUISI-│  │ CONCEPTOS  │ │  RUTA  │ │ RECURSOS │  │ SIGUIENTES │
  │   TOS     │  │   CLAVE    │ │  DE    │ │          │  │   PASOS    │
  └─────┬─────┘  └─────┬──────┘ │ESTUDIO │ └────┬─────┘  └─────┬──────┘
        │               │        └───┬────┘      │              │
        ▼               ▼            ▼           ▼              ▼
```

---

## 📋 Prerequisitos

```
  Prerequisitos
  ├── Python básico
  │   ├── Diccionarios (dict)
  │   ├── Clases y objetos
  │   └── Decoradores (opcional)
  ├── Complejidad algorítmica (Big-O)
  │   ├── O(1), O(n), O(log n)
  │   └── Análisis amortizado
  └── Estructuras de datos fundamentales
      ├── Arrays / Listas
      └── Tablas hash
```

## 🔑 Conceptos Clave

```
  Conceptos Clave
  ├── HashMap (diccionario)
  │   ├── Acceso O(1) por clave
  │   └── Almacena referencia al nodo
  ├── Lista Doblemente Enlazada
  │   ├── Inserción O(1) en cabeza/cola
  │   ├── Eliminación O(1) dado el nodo
  │   └── Mantiene el orden de uso
  ├── Nodos Centinela (Sentinel Nodes)
  │   ├── head → nodo ficticio al inicio
  │   ├── tail → nodo ficticio al final
  │   └── Simplifican casos borde
  └── Complejidad O(1) amortizada
      ├── get(key)  → O(1)
      └── put(key, value) → O(1)
```

## 🗺 Ruta de Estudio

```
  ① Entender arrays y hash tables
  │   └── → Cómo funcionan internamente los diccionarios
  │
  ② Linked Lists (listas enlazadas)
  │   └── → Simple → Doble → Operaciones insert/delete
  │
  ③ Combinar ambas estructuras
  │   └── → HashMap apunta a nodos de la lista
  │
  ④ Implementar LRU Cache
  │   ├── → get(key): mover nodo al frente
  │   ├── → put(key, val): insertar/actualizar + evicción
  │   └── → Manejar capacidad máxima
  │
  ⑤ Optimizar y probar
      ├── → Tests unitarios
      ├── → Edge cases (capacidad 0, claves repetidas)
      └── → Comparar con OrderedDict de Python
```

## 📚 Recursos

```
  Recursos
  ├── LeetCode #146 — LRU Cache
  ├── Neetcode — explicación visual
  ├── Documentación Python: collections.OrderedDict
  └── "Designing Data-Intensive Applications" — Cap. 5
```

## 🚀 Siguientes Pasos

```
  Después de dominar LRU Cache →
  ├── Redis caching (caché distribuido)
  ├── Memcached (caché en memoria)
  ├── Estrategias de caché
  │   ├── LFU (Least Frequently Used)
  │   ├── FIFO (First In, First Out)
  │   └── TTL (Time To Live)
  └── System Design: diseñar un sistema de caché a escala
```

---

> **💡 Consejo:** Dibuja en papel la lista doblemente enlazada y el hashmap
> antes de escribir código. Visualizar las conexiones es la clave para
> entender esta estructura.
