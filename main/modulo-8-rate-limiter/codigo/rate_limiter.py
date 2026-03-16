"""
Módulo 8: Rate Limiter — Cuatro algoritmos implementados desde cero.

Un Rate Limiter controla cuántas peticiones puede hacer un cliente en un período
de tiempo. Es un componente fundamental en APIs, gateways y sistemas distribuidos.

Algoritmos implementados:
  1. FixedWindowRateLimiter    — Ventana de tiempo fija, O(1) tiempo y espacio.
  2. SlidingWindowLogRateLimiter — Log de timestamps, O(n) tiempo y espacio.
  3. TokenBucketRateLimiter    — Tokens acumulables, O(1), permite ráfagas.
  4. LeakyBucketRateLimiter    — Cola con agujero, O(1), suaviza el tráfico.

Lore: Eres el Guardián de la Puerta Galáctica. Estas son tus cuatro técnicas
ancestrales de control de flujo interestelar.
"""

import time
from collections import defaultdict, deque


# ─────────────────────────────────────────────────────────────────────────────
# 1. FIXED WINDOW COUNTER
# ─────────────────────────────────────────────────────────────────────────────


class FixedWindowRateLimiter:
    """
    Ventana de tiempo fija: cada ventana tiene un contador que se reinicia
    al inicio de la siguiente ventana.

    Arquitectura por cliente:
      { client_id → (window_start_timestamp, request_count) }

    Complejidad:
      - allow_request: O(1) tiempo, O(1) espacio por cliente
      - Espacio total: O(C) donde C = número de clientes distintos

    Limitación conocida: un cliente puede hacer 2×max_requests en el intervalo
    [fin_ventana - ε, inicio_ventana_siguiente + ε], porque se cuentan en dos
    ventanas separadas.
    """

    def __init__(self, max_requests: int, window_seconds: float) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        # { client_id → [window_start, count] }
        self._windows: dict[str, list] = defaultdict(lambda: [0.0, 0])

    def allow_request(self, client_id: str) -> bool:
        """Retorna True si la petición está dentro del límite, False si se bloquea."""
        now = time.time()
        state = self._windows[client_id]
        window_start, count = state

        # ¿Estamos en una nueva ventana?
        if now - window_start >= self.window_seconds:
            state[0] = now
            state[1] = 1
            return True

        if count < self.max_requests:
            state[1] += 1
            return True

        return False


# ─────────────────────────────────────────────────────────────────────────────
# 2. SLIDING WINDOW LOG
# ─────────────────────────────────────────────────────────────────────────────


class SlidingWindowLogRateLimiter:
    """
    Ventana deslizante con log de timestamps: guarda el momento exacto de cada
    petición. La ventana siempre mira los últimos `window_seconds` desde ahora.

    Arquitectura por cliente:
      { client_id → deque([t1, t2, t3, ...]) }  — timestamps ordenados

    Complejidad:
      - allow_request: O(n) donde n = peticiones en la ventana actual
      - Espacio: O(n) por cliente (un timestamp por petición)

    Ventaja sobre Fixed Window: no sufre el spike en el límite de ventana.
    Desventaja: usa más memoria que los enfoques O(1).
    """

    def __init__(self, max_requests: int, window_seconds: float) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        # { client_id → deque de timestamps }
        self._logs: dict[str, deque] = defaultdict(deque)

    def allow_request(self, client_id: str) -> bool:
        """Retorna True si la petición está dentro del límite, False si se bloquea."""
        now = time.time()
        log = self._logs[client_id]
        cutoff = now - self.window_seconds

        # Eliminar timestamps fuera de la ventana actual (más antiguos que cutoff)
        while log and log[0] <= cutoff:
            log.popleft()

        if len(log) < self.max_requests:
            log.append(now)
            return True

        return False


# ─────────────────────────────────────────────────────────────────────────────
# 3. TOKEN BUCKET
# ─────────────────────────────────────────────────────────────────────────────


class TokenBucketRateLimiter:
    """
    Cubo de tokens: el cubo se rellena con tokens a tasa constante (`refill_rate`
    tokens/segundo). Cada petición consume uno o más tokens.

    Arquitectura por cliente:
      { client_id → [tokens_actuales, ultimo_timestamp] }

    El refill es "lazy": los tokens se calculan al momento de la petición,
    no en un hilo de fondo. Esto hace la implementación O(1).

    Complejidad:
      - allow_request: O(1) tiempo y espacio por cliente

    Permite ráfagas: si un cliente acumuló tokens puede enviar muchas peticiones
    de golpe hasta agotar el cubo. Ideal para APIs que quieren ser permisivas
    con clientes bien comportados.
    """

    def __init__(self, capacity: int, refill_rate: float) -> None:
        """
        Args:
            capacity:    Número máximo de tokens que puede almacenar el cubo.
            refill_rate: Tokens añadidos por segundo (puede ser fraccionario).
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        # { client_id → [tokens_float, last_refill_time] }
        self._buckets: dict[str, list] = defaultdict(lambda: [float(capacity), time.time()])

    def allow_request(self, client_id: str, tokens: int = 1) -> bool:
        """
        Retorna True si hay suficientes tokens para la petición y los consume.
        Retorna False si no hay suficientes tokens.

        Args:
            client_id: Identificador único del cliente.
            tokens:    Número de tokens que requiere esta petición (default=1).
        """
        now = time.time()
        bucket = self._buckets[client_id]

        # Calcular cuántos tokens se añaden desde el último acceso
        elapsed = now - bucket[1]
        bucket[1] = now
        bucket[0] = min(self.capacity, bucket[0] + elapsed * self.refill_rate)

        if bucket[0] >= tokens:
            bucket[0] -= tokens
            return True

        return False


# ─────────────────────────────────────────────────────────────────────────────
# 4. LEAKY BUCKET
# ─────────────────────────────────────────────────────────────────────────────


class LeakyBucketRateLimiter:
    """
    Cubo con agujero: las peticiones "llenan" el cubo; el agujero "drena" a tasa
    constante. Si el cubo está lleno, la petición se descarta.

    En esta implementación sin cola real, el "nivel" del cubo es un float que
    representa cuántas peticiones están "pendientes de procesar". Sube en 1
    con cada petición y baja a tasa `leak_rate` con el tiempo.

    Arquitectura por cliente:
      { client_id → [nivel_actual, ultimo_timestamp] }

    Complejidad:
      - allow_request: O(1) tiempo y espacio por cliente

    Garantiza un flujo de salida uniforme. Ideal para suavizar tráfico
    en routers y sistemas de QoS.
    """

    def __init__(self, capacity: int, leak_rate: float) -> None:
        """
        Args:
            capacity:  Tamaño máximo del cubo (peticiones en tránsito).
            leak_rate: Peticiones procesadas por segundo.
        """
        self.capacity = capacity
        self.leak_rate = leak_rate
        # { client_id → [nivel_float, last_leak_time] }
        self._buckets: dict[str, list] = defaultdict(lambda: [0.0, time.time()])

    def allow_request(self, client_id: str) -> bool:
        """Retorna True si hay espacio en el cubo, False si está lleno."""
        now = time.time()
        bucket = self._buckets[client_id]

        # El cubo se vacía (leak) con el tiempo transcurrido
        elapsed = now - bucket[1]
        bucket[1] = now
        bucket[0] = max(0.0, bucket[0] - elapsed * self.leak_rate)

        if bucket[0] < self.capacity:
            bucket[0] += 1.0
            return True

        return False


# ─────────────────────────────────────────────────────────────────────────────
# DEMO
# ─────────────────────────────────────────────────────────────────────────────


def _demo_fixed_window() -> None:
    print("\n🔲 Fixed Window Counter (5 req / 1s)")
    limiter = FixedWindowRateLimiter(max_requests=5, window_seconds=1.0)
    cliente = "nave-alfa"
    for i in range(7):
        resultado = limiter.allow_request(cliente)
        estado = "✅ PERMITIDO" if resultado else "❌ BLOQUEADO"
        print(f"  Petición {i + 1}: {estado}")


def _demo_sliding_window() -> None:
    print("\n📜 Sliding Window Log (5 req / 1s)")
    limiter = SlidingWindowLogRateLimiter(max_requests=5, window_seconds=1.0)
    cliente = "nave-beta"
    for i in range(7):
        resultado = limiter.allow_request(cliente)
        estado = "✅ PERMITIDO" if resultado else "❌ BLOQUEADO"
        print(f"  Petición {i + 1}: {estado}")


def _demo_token_bucket() -> None:
    print("\n🪣 Token Bucket (capacidad=5, refill=2/s)")
    limiter = TokenBucketRateLimiter(capacity=5, refill_rate=2.0)
    cliente = "nave-gamma"
    print("  Ráfaga inicial:")
    for i in range(6):
        resultado = limiter.allow_request(cliente)
        estado = "✅ PERMITIDO" if resultado else "❌ BLOQUEADO"
        print(f"    Petición {i + 1}: {estado}")
    print("  Esperando 1 segundo para recargar tokens...")
    time.sleep(1.0)
    resultado = limiter.allow_request(cliente)
    print(f"  Petición tras espera: {'✅ PERMITIDO' if resultado else '❌ BLOQUEADO'}")


def _demo_leaky_bucket() -> None:
    print("\n💧 Leaky Bucket (capacidad=3, leak=1/s)")
    limiter = LeakyBucketRateLimiter(capacity=3, leak_rate=1.0)
    cliente = "nave-delta"
    print("  Ráfaga inicial (llenando el cubo):")
    for i in range(5):
        resultado = limiter.allow_request(cliente)
        estado = "✅ PERMITIDO" if resultado else "❌ BLOQUEADO"
        print(f"    Petición {i + 1}: {estado}")
    print("  Esperando 2 segundos (el cubo se vacía parcialmente)...")
    time.sleep(2.0)
    resultado = limiter.allow_request(cliente)
    print(f"  Petición tras espera: {'✅ PERMITIDO' if resultado else '❌ BLOQUEADO'}")


if __name__ == "__main__":
    print("=" * 55)
    print("  MÓDULO 8 — El Guardián de Tráfico: Rate Limiter  ")
    print("=" * 55)

    _demo_fixed_window()
    _demo_sliding_window()
    _demo_token_bucket()
    _demo_leaky_bucket()

    print("\n¡Misión completa, Guardián! La Puerta Galáctica permanece segura. 🌌")
