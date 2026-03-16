# 🧠 Módulo 4: Simulador de Inferencia de LLM — System Design

> **Tema:** Batching, KV Cache y Streaming en servidores de inferencia de modelos de lenguaje grandes.

---

## 🌌 La Historia: El Oráculo Galáctico

Eres el **arquitecto principal** del Oráculo de IA Galáctico. Miles de millones de seres
de todos los rincones del cosmos envían preguntas simultáneamente. Tu misión:

- **Agrupar sus consultas sabiamente** (batching) para que la GPU del oráculo no desperdicie ciclos.
- **Gestionar la memoria cristalina del oráculo** (KV Cache) donde se almacenan los estados
  intermedios de atención — sin ella, cada nuevo token requeriría recalcular toda la secuencia.
- **Transmitir las respuestas token por token** (streaming) a través del cosmos, para que
  los seres no esperen a que la respuesta completa se materialice.

```
    🌍 🌏 🌎          ┌──────────────────────────┐
   Peticiones          │   🔮 ORÁCULO GALÁCTICO   │
   simultáneas ──────► │                          │
   de billones         │  ┌────────┐  ┌────────┐  │
   de seres            │  │ Batch  │  │  KV    │  │      Token a token
                       │  │Scheduler│  │ Cache  │  │ ────► 🌟 Streaming
                       │  └────────┘  └────────┘  │      hacia el cosmos
                       │                          │
                       │  ┌────────────────────┐  │
                       │  │  Token Generator   │  │
                       │  └────────────────────┘  │
                       └──────────────────────────┘
```

---

## 📚 Conceptos Técnicos Clave

### 1. Batching (Agrupación de Peticiones)

En la inferencia de LLMs, la GPU es el recurso más costoso. Si procesamos una petición
a la vez, la GPU queda infrautilizada — es como enviar un autobús con un solo pasajero.

```
  ❌ Sin batching (ineficiente):
  ┌─────┐     ┌─────┐     ┌─────┐
  │ R1  │ ──► │ GPU │ ──► │ T1  │   (GPU al 10% de uso)
  └─────┘     └─────┘     └─────┘

  ✅ Con batching (eficiente):
  ┌─────┐
  │ R1  │──┐  ┌─────┐     ┌─────┐
  ├─────┤  ├─►│ GPU │ ──► │T1-T8│   (GPU al 80% de uso)
  │ R2  │──┤  └─────┘     └─────┘
  ├─────┤  │
  │ ... │──┘
  └─────┘
```

**Batching estático vs. continuo:**

| Aspecto              | Estático                          | Continuo                                |
|----------------------|-----------------------------------|-----------------------------------------|
| Cuando se forma      | Se espera a llenar el batch       | Se forma en cada paso de inferencia     |
| Peticiones cortas    | Esperan a que acaben las largas   | Se reemplazan inmediatamente al acabar  |
| Throughput           | Menor                             | Mayor                                   |
| Complejidad          | Simple                            | Más complejo de implementar             |

### 2. KV Cache (Caché de Clave-Valor de Atención)

Durante la generación autoregresiva, el transformer calcula estados de **Key** y **Value**
para cada capa de atención. Sin caché, generar el token N requeriría recalcular los N-1
tokens anteriores — complejidad O(n²) por token.

```
  Sin KV Cache:                    Con KV Cache:
  Token 1: calcular K,V            Token 1: calcular K,V → guardar
  Token 2: recalcular K,V 1-2      Token 2: leer caché + calcular nuevo → guardar
  Token 3: recalcular K,V 1-3      Token 3: leer caché + calcular nuevo → guardar
  ...                               ...
  Token N: recalcular K,V 1-N      Token N: leer caché + calcular nuevo → guardar
  ──────────────────────────        ──────────────────────────
  Coste: O(n²) por secuencia       Coste: O(n) por secuencia
```

La memoria del KV Cache crece con: `batch_size × num_capas × longitud_secuencia × dim_modelo × 2`

### 3. Streaming de Respuestas

En vez de esperar a que se generen todos los tokens, el servidor envía cada token
al cliente conforme se produce. Esto reduce la **latencia percibida** dramáticamente.

```
  Sin streaming:
  Usuario ──► [espera 5 segundos] ──► "La respuesta completa aparece de golpe"

  Con streaming:
  Usuario ──► "La" ──► "respuesta" ──► "aparece" ──► "token" ──► "a" ──► "token"
              10ms      20ms           30ms           40ms        50ms     60ms
```

---

## 🏗️ Consideraciones de Diseño del Sistema

### Escalabilidad
- **Horizontal:** Múltiples instancias del servidor detrás de un balanceador de carga.
- **Vertical:** Más memoria GPU → mayor KV Cache → más peticiones concurrentes.

### Gestión de Memoria
- El KV Cache es el mayor consumidor de memoria GPU.
- Se necesitan políticas de evicción cuando la memoria se agota.
- Trade-off: más memoria para KV Cache = menos para el batch size.

### Latencia vs. Throughput
- Batches más grandes → mayor throughput pero mayor latencia por petición individual.
- Batches más pequeños → menor latencia pero menor throughput total.
- El scheduler debe balancear estos dos objetivos.

### Tolerancia a Fallos
- ¿Qué pasa si una petición en el batch falla?
- Las demás peticiones del batch no deben verse afectadas.
- El KV Cache de la petición fallida debe liberarse inmediatamente.

---

## 📁 Estructura del Módulo

```
modulo-4-llm-inference/
├── README.md                                  ← Este archivo
└── codigo/
    └── python/
        ├── inference_server.py                ← Servidor de inferencia simulado
        └── test_inference_server.py           ← Suite de pruebas con pytest
```

---

## ▶️ Cómo Ejecutar

### Demostración interactiva

```bash
cd main/modulo-4-llm-inference/codigo/python
python inference_server.py
```

### Ejecutar pruebas

```bash
cd main/modulo-4-llm-inference/codigo/python
pytest test_inference_server.py -v
```

---

## 📊 Complejidades

| Operación               | Complejidad Temporal | Complejidad Espacial          |
|--------------------------|----------------------|-------------------------------|
| Almacenar en KV Cache    | O(1)                 | O(capas × dim)                |
| Consultar KV Cache       | O(1)                 | O(1)                          |
| Evicción de KV Cache     | O(capas)             | O(1)                          |
| Formación de batch       | O(n log n)           | O(batch_size)                 |
| Paso de inferencia       | O(batch_size)        | O(batch_size × seq_len × dim) |
| Streaming de respuesta   | O(1) por token       | O(1)                          |

Donde `n` es el número de peticiones en cola y `dim` es la dimensión del modelo.
