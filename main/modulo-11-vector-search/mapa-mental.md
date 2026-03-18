# 🧠 Mapa Mental — Vector Search Engine

## ⏱ Tiempo estimado: 10–15 horas

```
                    ╔══════════════════════════════╗
                    ║   MOTOR DE BÚSQUEDA          ║
                    ║   SEMÁNTICA (VECTOR SEARCH)  ║
                    ╚══════════════╤═══════════════╝
                                   │
        ┌───────────┬──────────────┼──────────────┬──────────────┐
        ▼           ▼              ▼              ▼              ▼
  ┌──────────┐ ┌─────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
  │PREREQUISI│ │CONCEPT. │  │ALGORITMO │  │RECURSOS  │  │SIGUIENTES│
  │   TOS    │ │  CLAVE  │  │          │  │          │  │  PASOS   │
  └────┬─────┘ └────┬────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘
       │             │            │             │              │
       ▼             ▼            ▼             ▼              ▼
```

---

## 📋 Prerequisitos

```
  Prerequisitos
  ├── Álgebra lineal básica
  │   ├── Vectores y operaciones (suma, producto escalar)
  │   ├── Norma (‖v‖) y normalización
  │   ├── Producto punto y su interpretación geométrica
  │   └── Ángulo entre vectores (similitud coseno)
  ├── Python intermedio
  │   ├── Diccionarios, listas, sets
  │   ├── Comprensiones de listas
  │   ├── heapq (colas de prioridad)
  │   └── random.gauss() para distribución normal
  └── Notación Big-O
      ├── O(n·d): qué significa para n=10M, d=1536
      ├── Complejidad de espacio
      └── Tradeoffs exactitud vs velocidad
```

## 🔑 Conceptos Clave

```
  Vector Search
  ├── Embeddings
  │   ├── Representación densa de alta dimensión
  │   ├── Propiedades semánticas preservadas
  │   └── Modelos: BERT, OpenAI, Sentence-Transformers
  │
  ├── Métricas de similitud
  │   ├── Similitud Coseno: cos(θ) = (a·b)/(‖a‖·‖b‖)
  │   │   └── Invariante a escala, mide orientación
  │   ├── Distancia Euclidiana: √Σ(aᵢ-bᵢ)²
  │   │   └── Sensible a magnitud, intuitiva geométricamente
  │   └── Producto Punto: Σaᵢbᵢ
  │       └── Para vectores normalizados ≡ similitud coseno
  │
  ├── Exact Nearest Neighbor (ENN)
  │   ├── Fuerza Bruta: O(n·d) — siempre correcto
  │   └── KD-Tree: O(d·log n) avg — falla en alta dimensión
  │
  ├── Approximate Nearest Neighbor (ANN)
  │   ├── LSH (Locality Sensitive Hashing)
  │   │   ├── Random Projection: hiperplanos aleatorios
  │   │   ├── Múltiples tablas aumentan recall
  │   │   └── Tradeoff: más planos → mejor precision, más lento
  │   └── HNSW (Hierarchical Navigable Small World)
  │       ├── Grafo jerárquico de vecinos
  │       ├── O(log n) búsqueda, recall >99%
  │       └── Estándar en producción (Pinecone, pgvector)
  │
  └── Maldición de la Dimensionalidad
      ├── En alta dimensión todos los puntos están "lejos"
      ├── KD-Tree pierde eficiencia: explora casi todo el árbol
      └── Solución: ANN con estructuras de datos especializadas
```

## 🗺 Ruta de Estudio

```
  ① Entender embeddings y similitud coseno
  │   ├── → Visualizar en 2D: ¿qué significa el ángulo?
  │   └── → Implementar cosine_similarity() desde cero
  │
  ② Fuerza bruta (VectorStore)
  │   ├── → Implementar add() / search() / delete()
  │   ├── → Medir tiempo con 1K, 10K, 100K vectores
  │   └── → Ver cómo el tiempo crece linealmente con n
  │
  ③ KD-Tree (KDTreeVectorStore)
  │   ├── → Entender cómo el árbol divide el espacio
  │   ├── → Implementar _build() recursivo con mediana
  │   ├── → Implementar _search_knn() con poda inteligente
  │   └── → Comparar con fuerza bruta: ¿cuándo gana? ¿cuándo pierde?
  │
  ④ LSH (LSHVectorStore)
  │   ├── → Entender la idea: hiperplanos = bits de hash
  │   ├── → ¿Por qué vectores similares caen en el mismo bucket?
  │   ├── → Implementar con múltiples tablas
  │   └── → Medir recall vs fuerza bruta con distintas configuraciones
  │
  ⑤ Benchmarking comparativo
  │   ├── → n=10K vectores de 128d
  │   ├── → Medir latencia de búsqueda para cada algoritmo
  │   └── → Tabular: latencia vs recall vs uso de memoria
  │
  ⑥ Comprender HNSW (conceptual, sin implementar)
      ├── → Leer el paper original (Malkov & Yashunin, 2016)
      └── → Explorar hnswlib o pgvector en modo "caja negra"
```

## 📚 Recursos

```
  Recursos
  ├── Papers
  │   ├── "Efficient and Robust ANN Search" — Malkov & Yashunin (HNSW)
  │   ├── "Locality-Sensitive Hashing Scheme" — Indyk & Motwani (1998)
  │   └── "Billion-scale similarity search with GPUs" — Johnson et al. (FAISS)
  │
  ├── Documentación oficial
  │   ├── Pinecone — pinecone.io/learn/vector-database
  │   ├── Weaviate — weaviate.io/developers/weaviate
  │   └── FAISS — github.com/facebookresearch/faiss/wiki
  │
  ├── Artículos / tutoriales
  │   ├── "Vector Databases Explained" — Pinecone Blog
  │   ├── "Understanding HNSW" — Weaviate Blog
  │   └── "ANN Benchmarks" — ann-benchmarks.com
  │
  └── Cursos
      ├── CS324 Stanford (LLMs) — lectura sobre retrieval
      └── "Building RAG from Scratch" — LlamaIndex Docs
```

## 🚀 Siguientes Pasos

```
  Después de dominar este módulo →
  ├── HNSW desde cero
  │   ├── Grafo de proximidad en múltiples capas
  │   ├── Inserción con selección greedy de vecinos
  │   └── Búsqueda: de capa superior a inferior
  │
  ├── FAISS (Facebook AI Similarity Search)
  │   ├── IndexFlatL2 — fuerza bruta en GPU
  │   ├── IndexIVFFlat — clustering + búsqueda por cluster
  │   └── IndexPQ — compresión con Product Quantization
  │
  ├── Bases de datos vectoriales en producción
  │   ├── Pinecone (SaaS managed)
  │   ├── Weaviate (open source, self-hosted o cloud)
  │   ├── Qdrant (Rust, alto rendimiento)
  │   └── pgvector (extensión de PostgreSQL)
  │
  └── Sistemas RAG completos
      ├── LangChain / LlamaIndex
      ├── Chunking strategies (fixed, semantic, hierarchical)
      └── Re-ranking con cross-encoders
```

---

> **💡 Consejo:** Antes de usar FAISS o Pinecone, implementa la fuerza bruta y mide
> en cuántos vectores tu aplicación realmente necesita ANN. Para < 100K vectores,
> la fuerza bruta con numpy puede ser más rápida y simple que montar un vector DB.
> La optimización prematura es la raíz de todos los males — Knuth.
