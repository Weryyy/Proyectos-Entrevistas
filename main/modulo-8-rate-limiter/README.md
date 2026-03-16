# Módulo 8: El Guardián de Tráfico — Rate Limiter

## 🧠 Concepto Técnico

Un **Rate Limiter** (limitador de tasa) es un mecanismo que controla cuántas peticiones
puede hacer un cliente a un sistema en un período de tiempo determinado.

### ¿Por qué es crucial en entrevistas?

Empresas como **Google**, **Stripe**, **Cloudflare** y **Anthropic** preguntan sobre
rate limiting porque aparece en casi todos los sistemas distribuidos reales:

- Las APIs de pago (Stripe) limitan peticiones para evitar fraude y sobrecarga.
- Las CDNs (Cloudflare) protegen contra ataques DDoS.
- Los modelos de lenguaje (Anthropic) controlan el consumo de recursos de GPU.
- Las APIs públicas (Google Maps, Twitter) monetizan el acceso por niveles de uso.

Sin rate limiting, un solo cliente malicioso o con un bug podría derribar todo un servicio.

---

## 🚀 Lore: La Guardia de la Puerta Galáctica

> *Eres el Guardián de la Puerta Galáctica: el único punto de entrada a la red de
> comunicaciones interestelar. Millones de naves intentan enviar mensajes cada segundo.*
>
> *Tu misión es garantizar que ninguna nave monopolice el canal de comunicación.
> Cada nave tiene una cuota: si intenta enviar demasiados mensajes demasiado rápido,
> su señal es bloqueada. Solo así el canal permanece abierto para todas las civilizaciones.*
>
> *Tienes cuatro técnicas ancestrales de control de flujo a tu disposición.
> Cada una tiene sus virtudes y sus limitaciones. Debes elegir sabiamente.*

---

## 📐 Los Cuatro Algoritmos

### 1. Fixed Window Counter (Ventana Fija)

Divide el tiempo en ventanas fijas (ej. cada 60 segundos). Cuenta peticiones por ventana.

```
Tiempo →  0s        60s       120s      180s
          │          │          │          │
          ▼          ▼          ▼          ▼
Ventana:  [  W1   ] [  W2   ] [  W3   ]

W1: ████████░░  8/10 peticiones → OK
    ██████████  10/10 peticiones → OK
    ██████████! 11/10 → BLOQUEADO

W2: Reinicia a 0 en t=60s → primeras 10 permitidas de nuevo

⚠️  Problema: Un cliente puede enviar 10 al final de W1 + 10 al inicio de W2
    = 20 peticiones en solo 1 segundo (en el límite de ventanas).
```

- **Tiempo:** O(1) — solo incrementar un contador
- **Espacio:** O(1) por cliente — un contador y un timestamp

---

### 2. Sliding Window Log (Ventana Deslizante con Log)

Guarda el timestamp exacto de cada petición. La ventana "desliza" con el tiempo actual.

```
Tiempo actual: t=100s, ventana=60s → Solo cuenta desde t=40s

Log del cliente:   [t=35] [t=50] [t=72] [t=88] [t=99]
                     ✗ expirado │    ✓    ✓     ✓     ✓
                                │←── ventana activa ──→│

Peticiones válidas: 4  →  Si límite=5: PERMITIR
```

- **Tiempo:** O(n) para limpiar entradas antiguas (n = peticiones en ventana)
- **Espacio:** O(n) por cliente — guarda todos los timestamps

---

### 3. Token Bucket (Cubo de Tokens)

Un cubo se llena con tokens a tasa constante. Cada petición consume un token.
Permite **ráfagas** hasta la capacidad del cubo.

```
Cubo (capacidad=10):

t=0s:   ██████████  10 tokens (lleno)
        Petición → consume 1 → 9 tokens
        Petición → consume 1 → 8 tokens
        ... ráfaga de 10 peticiones posible

Refill: +1 token/segundo automáticamente

t=5s:   Si el cubo estaba vacío:  ░░░░░░░░░░
        Ahora:                    █████░░░░░  5 tokens (5s × 1/s)

⚡ Permite ráfagas: un cliente puede enviar muchas peticiones si acumuló tokens.
```

- **Tiempo:** O(1) — calcular tokens desde último acceso
- **Espacio:** O(1) por cliente — tokens actuales y timestamp

---

### 4. Leaky Bucket (Cubo con Agujero)

Las peticiones entran en una cola (el cubo). Salen a tasa constante (el "agujero").
**Suaviza** el tráfico de salida independientemente del patrón de entrada.

```
Entrada (irregular):  ████  ██  ████████  ██
                         ↓↓↓↓
                    ┌──────────────┐
                    │   CUBO       │  ← Cola FIFO
                    │  cap=5       │
                    │  [p1][p2][p3]│
                    └──────┬───────┘
                           │ leak_rate = 2 req/s
                    Salida (uniforme): ██ ██ ██ ██ ██

Si el cubo está lleno: BLOQUEADO (petición descartada)
```

- **Tiempo:** O(1) — calcular cuánto se vació desde el último acceso
- **Espacio:** O(1) por cliente — nivel actual y timestamp

---

## 📊 Tabla de Comparación

| Algoritmo             | Tiempo  | Espacio  | Permite Ráfagas | Tráfico Suave | Problema Principal         |
|-----------------------|---------|----------|-----------------|---------------|----------------------------|
| Fixed Window Counter  | O(1)    | O(1)     | Sí (en límites) | No            | Spike en límite de ventana |
| Sliding Window Log    | O(n)    | O(n)     | No              | Sí            | Memoria por timestamps     |
| Token Bucket          | O(1)    | O(1)     | ✅ Sí           | No            | Ráfagas pueden ser grandes |
| Leaky Bucket          | O(1)    | O(1)     | No              | ✅ Sí         | Cola puede llenarse        |

---

## ▶️ Cómo Ejecutar

### Ejecución directa (demo interactivo)

```bash
cd main/modulo-8-rate-limiter/codigo
python rate_limiter.py
```

### Ejecutar las pruebas

```bash
cd main/modulo-8-rate-limiter/codigo
pytest test_rate_limiter.py -v
```

### Requisitos

- Python 3.10+
- pytest (`pip install pytest`)

---

## 📁 Estructura del Módulo

```
modulo-8-rate-limiter/
├── README.md                    # Este archivo
├── mapa-mental.md               # Mapa mental del módulo
└── codigo/
    ├── rate_limiter.py          # Los cuatro algoritmos implementados
    └── test_rate_limiter.py     # Suite de pruebas con pytest
```
