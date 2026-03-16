# 🤖 Mapa Mental — LLM Inference & System Design

## ⏱ Tiempo estimado: 15–20 horas

```
                     ╔═══════════════════════════╗
                     ║    LLM  INFERENCE  &      ║
                     ║    SYSTEM  DESIGN         ║
                     ╚════════════╤══════════════╝
                                  │
       ┌──────────────┬───────────┼───────────┬────────────────┐
       ▼              ▼           ▼           ▼                ▼
 ┌───────────┐ ┌────────────┐ ┌────────┐ ┌──────────┐  ┌────────────┐
 │PREREQUISI-│ │ CONCEPTOS  │ │  RUTA  │ │ RECURSOS │  │ SIGUIENTES │
 │   TOS     │ │   CLAVE    │ │  DE    │ │          │  │   PASOS    │
 └─────┬─────┘ └─────┬──────┘ │ESTUDIO │ └────┬─────┘  └─────┬──────┘
       │              │        └───┬────┘      │              │
       ▼              ▼            ▼           ▼              ▼
```

---

## 📋 Prerequisitos

```
  Prerequisitos
  ├── Python intermedio-avanzado
  │   ├── NumPy básico
  │   ├── Generadores y yield
  │   └── Async (asyncio)
  ├── Conceptos básicos de ML
  │   ├── Redes neuronales (capas, pesos)
  │   ├── Forward pass
  │   └── Softmax y distribuciones de probabilidad
  └── Álgebra lineal básica
      ├── Multiplicación de matrices
      └── Vectores y embeddings
```

## 🔑 Conceptos Clave

```
  Conceptos Clave
  ├── Tokens y Tokenización
  │   ├── BPE (Byte Pair Encoding)
  │   ├── Vocabulario → IDs numéricos
  │   └── Tokens especiales: <BOS>, <EOS>, <PAD>
  ├── Mecanismo de Atención (Attention)
  │   ├── Query, Key, Value
  │   ├── Self-attention
  │   ├── Multi-head attention
  │   └── Complejidad O(n²) con longitud de secuencia
  ├── KV Cache
  │   ├── Cachear Keys y Values de tokens previos
  │   ├── Evita recalcular atención completa
  │   └── Trade-off: memoria GPU ↔ velocidad
  ├── Batching
  │   ├── Static batching (lotes fijos)
  │   ├── Dynamic / Continuous batching
  │   └── Maximizar utilización de GPU
  ├── Streaming
  │   ├── Generar token por token
  │   ├── Server-Sent Events (SSE)
  │   └── Reducir latencia percibida (TTFT)
  └── Memoria GPU
      ├── Pesos del modelo (estáticos)
      ├── KV Cache (crece con contexto)
      └── Activaciones (durante forward pass)
```

## 🗺 Ruta de Estudio

```
  ① Tokenización
  │   └── → Entender BPE, usar tiktoken / sentencepiece
  │
  ② Mecanismo de Atención
  │   ├── → Implementar scaled dot-product attention
  │   └── → Visualizar matrices de atención
  │
  ③ KV Cache
  │   ├── → Por qué se cachean K y V, no Q
  │   └── → Implementar cache incremental
  │
  ④ Batching
  │   ├── → Static vs continuous batching
  │   └── → Manejar secuencias de distinta longitud
  │
  ⑤ Streaming
  │   ├── → Generación autoregresiva
  │   └── → Implementar endpoint SSE
  │
  ⑥ Sistema completo
      ├── → Orquestar: recibir prompt → tokenizar → inferir → stream
      ├── → Métricas: TTFT, throughput, latencia p99
      └── → Tests de carga y optimización
```

## 📚 Recursos

```
  Recursos
  ├── "Attention Is All You Need" — paper original
  ├── Jay Alammar — "The Illustrated Transformer"
  ├── Andrej Karpathy — "Let's build GPT from scratch"
  ├── HuggingFace — Transformers docs
  └── vLLM blog — "Efficient Memory Management for LLM Serving"
```

## 🚀 Siguientes Pasos

```
  Después de dominar LLM Inference →
  ├── vLLM (serving optimizado)
  ├── TensorRT-LLM (NVIDIA)
  ├── GGML / llama.cpp
  │   └── → Inferencia en CPU, cuantización
  ├── HuggingFace TGI (Text Generation Inference)
  ├── Técnicas avanzadas
  │   ├── PagedAttention
  │   ├── Speculative Decoding
  │   ├── Flash Attention
  │   └── Cuantización (GPTQ, AWQ, GGUF)
  └── MLOps para LLMs
      ├── Model serving (Triton, BentoML)
      └── Monitoreo y observabilidad
```

---

> **💡 Consejo:** La inferencia LLM es esencialmente un loop: predice el
> siguiente token, lo añade al contexto, y repite. Toda la complejidad del
> sistema (KV cache, batching, streaming) optimiza ese loop fundamental.
