# 🧠 Mapa Mental — Rate Limiter

## ⏱ Tiempo estimado: 6–10 horas

```
                        ╔══════════════════════╗
                        ║    RATE  LIMITER     ║
                        ║  (Guardián de Tráfico)║
                        ╚═══════════╤══════════╝
                                    │
        ┌───────────────┬───────────┼───────────┬────────────────┐
        ▼               ▼           ▼           ▼                ▼
  ┌───────────┐  ┌────────────┐ ┌────────┐ ┌──────────┐  ┌────────────┐
  │PREREQUISI-│  │ ALGORITMOS │ │  RUTA  │ │ RECURSOS │  │ SIGUIENTES │
  │   TOS     │  │   CLAVE    │ │  DE    │ │          │  │   PASOS    │
  └─────┬─────┘  └─────┬──────┘ │ESTUDIO │ └────┬─────┘  └─────┬──────┘
        │               │        └───┬────┘      │              │
        ▼               ▼            ▼           ▼              ▼
```

---

## 📋 Prerequisitos

```
  Prerequisitos
  ├── Python intermedio
  │   ├── Diccionarios anidados
  │   ├── collections.deque
  │   └── Módulo time (time.time())
  ├── Complejidad algorítmica (Big-O)
  │   ├── O(1) amortizado
  │   └── Trade-offs tiempo/espacio
  └── Conceptos de sistemas distribuidos
      ├── Latencia vs throughput
      ├── Cliente-servidor
      └── APIs REST (qué son los rate limits HTTP 429)
```

## 🔑 Algoritmos Clave

```
  Rate Limiting Algorithms
  ├── Fixed Window Counter
  │   ├── Ventana de tiempo fija
  │   ├── Un contador por ventana
  │   └── ⚠️ Spike en el límite de ventana
  ├── Sliding Window Log
  │   ├── Timestamps exactos en deque
  │   ├── Limpia entradas antiguas en cada request
  │   └── ⚠️ O(n) espacio por cliente activo
  ├── Token Bucket
  │   ├── Capacidad máxima de tokens
  │   ├── Refill a tasa constante (tokens/segundo)
  │   ├── Permite ráfagas controladas
  │   └── Usado por: AWS API Gateway, Stripe
  └── Leaky Bucket
      ├── Cola FIFO de peticiones
      ├── Procesamiento a tasa constante
      ├── Suaviza tráfico irregular
      └── Usado por: routers de red, QoS
```

## 🗺 Ruta de Estudio

```
  ① Entender el problema
  │   ├── → ¿Por qué es necesario el rate limiting?
  │   └── → Ejemplos reales: APIs, DDoS, monetización
  │
  ② Fixed Window Counter
  │   ├── → Implementación más simple
  │   └── → Identificar el bug del límite de ventana
  │
  ③ Sliding Window Log
  │   ├── → Solución al bug anterior
  │   └── → Trade-off: más preciso pero más memoria
  │
  ④ Token Bucket
  │   ├── → Concepto de tokens acumulados
  │   └── → Cálculo de refill lazy (al momento de la petición)
  │
  ⑤ Leaky Bucket
  │   ├── → Diferencia con Token Bucket
  │   └── → Cuándo suavizar vs cuándo permitir ráfagas
  │
  ⑥ System Design
      ├── → Rate limiter distribuido (Redis + Lua scripts)
      ├── → Rate limiting por IP, usuario, endpoint
      └── → Headers HTTP: X-RateLimit-Limit, Retry-After
```

## 📚 Recursos

```
  Recursos
  ├── "System Design Interview" — Alex Xu (Capítulo Rate Limiter)
  ├── Stripe Engineering Blog — "Rate Limiters"
  ├── Cloudflare Blog — "How we handle DDoS at scale"
  ├── RFC 6585 — HTTP 429 Too Many Requests
  └── Redis documentation — INCR + EXPIRE pattern
```

## 🚀 Siguientes Pasos

```
  Después de dominar Rate Limiting →
  ├── Circuit Breaker pattern
  ├── Bulkhead pattern
  ├── Distributed rate limiting
  │   ├── Redis con operaciones atómicas
  │   └── Consistent hashing para distribución
  ├── API Gateway (Kong, AWS API Gateway)
  └── System Design: diseñar un rate limiter para 1M usuarios
```

---

> **💡 Consejo:** La pregunta clave en una entrevista no es solo "implementa un
> rate limiter", sino "¿qué algoritmo elegirías y por qué?". Practica justificar
> los trade-offs: precisión vs memoria vs complejidad de implementación.
