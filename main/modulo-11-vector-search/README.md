# Módulo 11: El Motor de Búsqueda Semántica — Vector Search Engine

## 🧠 Concepto Técnico

La **búsqueda vectorial** (Vector Search) es la tecnología central detrás de los sistemas
de IA modernos: motores de búsqueda semántica, sistemas RAG, motores de recomendación
y bases de conocimiento para LLMs. En lugar de buscar por palabras clave exactas, convierte
datos (texto, imágenes, audio) en **vectores de alta dimensión** (embeddings) y busca por
*similitud geométrica* en ese espacio.

Empresas como **Pinecone, Weaviate, Chroma, Qdrant, Milvus, Google, Anthropic y OpenAI**
buscan ingenieros que entiendan cómo funciona esta tecnología por dentro, desde las
matemáticas hasta los compromisos de diseño en producción.

### ¿Qué es un embedding?

Un **embedding** es una función que mapea objetos complejos (palabras, oraciones,
imágenes) a vectores de números reales que preservan relaciones semánticas:

```
"gato"   → [0.82, -0.31,  0.54, ..., 0.12]  ← vector 768-dimensional
"felino" → [0.79, -0.28,  0.51, ..., 0.14]  ← muy cercano al anterior
"avión"  → [-0.12, 0.73, -0.41, ..., 0.88]  ← muy lejano
```

La similitud semántica entre conceptos se convierte en **proximidad geométrica** en
el espacio vectorial.

---

## 🚀 Lore: La Biblioteca Alienígena

> *Existe una biblioteca en el centro de la galaxia que contiene el conocimiento
> de todas las civilizaciones que han existido. Cada libro, cada fórmula, cada
> recuerdo está codificado como un vector de alta dimensión en cristales de datos.*
>
> *La biblioteca tiene billones de entradas y crece cada segundo. Los sabios
> del universo necesitan encontrar el conocimiento más relevante para su pregunta
> en microsegundos, no en años.*
>
> *Eres el arquitecto del motor de búsqueda. Tu diseño determinará si la
> civilización puede acceder a la sabiduría cósmica en tiempo real, o si
> quedará sepultada bajo una avalancha de datos irrelevantes.*
>
> *Implementa el motor. El universo espera.*

---

## 📐 Matemáticas Fundamentales

### Similitud Coseno

Mide el ángulo entre dos vectores, independientemente de su magnitud:

```
           a · b           Σ(aᵢ · bᵢ)
cos(θ) = ————————— = ————————————————————————
          ‖a‖ · ‖b‖   √Σaᵢ² · √Σbᵢ²

Rango: [-1, 1]
  cos(θ) =  1  → vectores idénticos (θ = 0°)
  cos(θ) =  0  → vectores ortogonales (θ = 90°)
  cos(θ) = -1  → vectores opuestos (θ = 180°)
```

### Producto Punto (Dot Product)

```
a · b = Σ(aᵢ · bᵢ) = a₁b₁ + a₂b₂ + ... + aₙbₙ
```

### Distancia Euclidiana

```
d(a, b) = √Σ(aᵢ - bᵢ)²
```

> **Nota**: Para vectores normalizados (‖v‖ = 1), maximizar el producto punto
> es equivalente a maximizar la similitud coseno. Esta propiedad se explota en
> FAISS y otros motores de producción.

---

## 🌌 Diagrama: Cómo Funciona la Búsqueda Vectorial

```
  CONSULTA DEL USUARIO
  "¿Cómo funciona la fotosíntesis?"
         │
         ▼
  ┌──────────────┐
  │   Modelo de  │
  │  Embeddings  │   (BERT, OpenAI text-embedding-3, etc.)
  └──────┬───────┘
         │  Genera vector de 1536 dimensiones
         ▼
  query = [0.12, -0.45, 0.83, ..., 0.31]
         │
         ▼
  ┌──────────────────────────────────────────────────────┐
  │              MOTOR DE BÚSQUEDA VECTORIAL             │
  │                                                      │
  │  ┌────────────┐  ┌─────────────┐  ┌──────────────┐  │
  │  │  Fuerza    │  │   KD-Tree   │  │     LSH      │  │
  │  │  Bruta     │  │  (exacto,   │  │ (aproximado, │  │
  │  │ O(n·d)     │  │  bajo dim.) │  │  alta dim.)  │  │
  │  └────────────┘  └─────────────┘  └──────────────┘  │
  │                                                      │
  │  BASE DE DATOS VECTORIAL (millones de documentos)    │
  │  ┌─────┬───────────────────────────────────────────┐ │
  │  │ id  │ vector (1536d)              │ metadata    │ │
  │  ├─────┼───────────────────────────────────────────┤ │
  │  │ d1  │ [0.11, -0.44, 0.82, ...]   │ {src: wiki} │ │
  │  │ d2  │ [-0.3,  0.71, 0.12, ...]   │ {src: pdf}  │ │
  │  │ d3  │ [0.13, -0.43, 0.85, ...]   │ {src: web}  │ │
  │  │ ... │ ...                         │ ...         │ │
  │  └─────┴───────────────────────────────────────────┘ │
  └──────────────────────────────────────────────────────┘
         │
         ▼  Top-K resultados por similitud coseno
  ┌─────────────────────────────────┐
  │  RESULTADOS (ordenados)         │
  │  1. d3 — sim=0.98 — {src: web} │
  │  2. d1 — sim=0.97 — {src: wiki}│
  │  3. ...                         │
  └─────────────────────────────────┘
         │
         ▼
  SISTEMA RAG / APLICACIÓN
  "La fotosíntesis es el proceso por el cual..."
```

---

## ⚡ ¿Por Qué la Búsqueda Exacta No Escala?

Con **n** vectores de dimensión **d**:

```
  n = 1,000,000 documentos
  d = 1,536 dimensiones (OpenAI text-embedding-3-small)

  Operaciones por búsqueda exacta:
  n × d = 1,000,000 × 1,536 = 1,536,000,000 multiplicaciones

  A 10⁹ FLOPS (CPU moderna):
  ~1.5 segundos por consulta ← inaceptable para producción
```

Por eso se necesita **Approximate Nearest Neighbor (ANN)**: sacrificamos exactitud
por velocidad, aceptando que encontremos el 95–99% de los vecinos reales.

---

## 📊 Comparativa de Algoritmos

| Algoritmo        | Tipo        | Complejidad búsqueda | Complejidad índice | Dim. óptima | Recall   |
|------------------|-------------|---------------------|--------------------|-------------|----------|
| **Fuerza Bruta** | Exacto      | O(n·d)              | O(n·d)             | Cualquiera  | 100%     |
| **KD-Tree**      | Exacto      | O(d·log n) avg      | O(n·d·log n)       | d ≤ 20      | 100%     |
| **Ball-Tree**    | Exacto      | O(d·log n) avg      | O(n·d·log n)       | d ≤ 40      | 100%     |
| **LSH**          | Aproximado  | O(candidatos · d)   | O(n·t·p·d)         | Cualquiera  | ~80–95%  |
| **HNSW**         | Aproximado  | O(log n)            | O(n·log n)         | Cualquiera  | ~95–99%  |
| **FAISS IVF**    | Aproximado  | O(n/c · d)          | O(n·d)             | Cualquiera  | ~90–99%  |

> **t** = número de tablas LSH, **p** = número de planos por tabla, **c** = número de celdas IVF

---

## 🔬 Análisis de Complejidad Detallado

### VectorStore (Fuerza Bruta)

| Operación  | Tiempo  | Espacio |
|------------|---------|---------|
| `add()`    | O(1)    | O(n·d)  |
| `search()` | O(n·d)  | O(n)    |
| `delete()` | O(1)    | —       |

### KDTreeVectorStore

| Operación       | Tiempo promedio | Tiempo peor caso | Espacio |
|-----------------|-----------------|------------------|---------|
| `add()`         | O(1)            | O(1)             | O(n·d)  |
| `build_index()` | O(n·d·log n)    | O(n·d·log n)     | O(n)    |
| `search()`      | O(d·log n)      | O(n·d)           | O(log n)|

> El peor caso ocurre en dimensiones altas (la "maldición de la dimensionalidad"):
> cuando d es grande, casi todos los puntos están a distancia similar y el árbol
> no puede podar ramas eficientemente.

### LSHVectorStore

| Operación  | Tiempo                  | Espacio       |
|------------|-------------------------|---------------|
| `add()`    | O(t·p·d)                | O(n·t)        |
| `search()` | O(t·p·d + candidatos·d) | O(t·p·d)      |

> **t** = tablas, **p** = planos/tabla. El espacio de los hiperplanos es O(t·p·d),
> que puede ser grande para alta dimensión. HNSW es preferido en producción.

---

## 🛠 Aplicaciones Reales

```
  Búsqueda Semántica
  ├── Google Search (neural matching)
  ├── Búsqueda en código (GitHub Copilot)
  └── Recuperación de documentos legales/médicos

  Sistemas RAG (Retrieval-Augmented Generation)
  ├── ChatGPT con búsqueda web
  ├── Asistentes con base de conocimiento corporativa
  └── Chatbots con memoria a largo plazo

  Recomendación
  ├── Spotify (canciones similares)
  ├── Netflix (películas parecidas)
  └── Amazon (productos relacionados)

  Visión por Computador
  ├── Búsqueda de imágenes similares
  ├── Reconocimiento facial
  └── Detección de contenido duplicado
```

---

## 🗂 Estructura de Archivos

```
modulo-11-vector-search/
├── README.md                  ← Este archivo
├── mapa-mental.md             ← Guía de estudio
└── codigo/
    ├── vector_store.py        ← Implementaciones (VectorStore, KDTree, LSH)
    └── test_vector_store.py   ← Suite de tests con pytest
```

---

## ▶ Cómo Ejecutar

```bash
# Desde la raíz del repositorio:
cd main/modulo-11-vector-search/codigo

# Ejecutar todos los tests con detalle:
pytest test_vector_store.py -v

# Ejecutar solo una clase de tests:
pytest test_vector_store.py::TestVectorStore -v
pytest test_vector_store.py::TestKDTreeVectorStore -v
pytest test_vector_store.py::TestLSHVectorStore -v

# Con reporte de cobertura (si tienes pytest-cov):
pytest test_vector_store.py -v --tb=short
```

**Requisitos**: solo Python 3.8+ y pytest. Sin dependencias externas.

```bash
pip install pytest
```

---

## 🎯 Preguntas Frecuentes en Entrevistas

1. **¿Por qué la similitud coseno en lugar de la distancia euclidiana para embeddings?**
   — Coseno es invariante a la magnitud del vector, solo mide el ángulo. Útil cuando
   los embeddings pueden tener magnitudes variables.

2. **¿Cuándo falla el KD-Tree?**
   — Con dimensiones > 20-30 (maldición de la dimensionalidad). El árbol tiene que
   explorar casi todos los nodos porque el hiperplano de corte ya no elimina puntos.

3. **¿Qué es HNSW y por qué es el estándar de facto?**
   — Hierarchical Navigable Small World. Construye un grafo jerárquico donde cada
   nodo tiene conexiones con sus vecinos más cercanos. Búsqueda en O(log n) con
   recall >99%. Usado por Pinecone, Weaviate, pgvector.

4. **¿Cómo escalar a billones de vectores?**
   — Sharding + índices ANN distribuidos. FAISS con IVF (inverted file index) divide
   el espacio en clusters y busca solo en los más prometedores.
