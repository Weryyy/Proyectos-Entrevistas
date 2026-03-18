"""
Tests para el Módulo 8: Rate Limiter.

Se monkeypatcha time.time() para que las pruebas sean deterministas
y no dependan del reloj del sistema.

Ejecutar con:
    pytest test_rate_limiter.py -v
"""

import pytest
import time as time_module

from rate_limiter import (
    FixedWindowRateLimiter,
    LeakyBucketRateLimiter,
    SlidingWindowLogRateLimiter,
    TokenBucketRateLimiter,
)


# ─────────────────────────────────────────────────────────────────────────────
# Fixture: reloj controlable
# ─────────────────────────────────────────────────────────────────────────────


class FakeClock:
    """Reloj falso para controlar time.time() en los tests."""

    def __init__(self, start: float = 1_000.0) -> None:
        self.current = start

    def __call__(self) -> float:
        return self.current

    def advance(self, seconds: float) -> None:
        self.current += seconds


@pytest.fixture
def fake_clock(monkeypatch):
    """Reemplaza time.time() con un reloj controlable."""
    clock = FakeClock()
    import rate_limiter as rl_module
    monkeypatch.setattr(rl_module.time, "time", clock)
    return clock


# ─────────────────────────────────────────────────────────────────────────────
# FIXED WINDOW COUNTER
# ─────────────────────────────────────────────────────────────────────────────


class TestFixedWindowRateLimiter:
    def test_permite_hasta_el_limite(self, fake_clock):
        limiter = FixedWindowRateLimiter(max_requests=3, window_seconds=10.0)
        assert limiter.allow_request("a") is True
        assert limiter.allow_request("a") is True
        assert limiter.allow_request("a") is True

    def test_bloquea_despues_del_limite(self, fake_clock):
        limiter = FixedWindowRateLimiter(max_requests=3, window_seconds=10.0)
        for _ in range(3):
            limiter.allow_request("a")
        assert limiter.allow_request("a") is False

    def test_reinicia_en_nueva_ventana(self, fake_clock):
        limiter = FixedWindowRateLimiter(max_requests=2, window_seconds=10.0)
        limiter.allow_request("a")
        limiter.allow_request("a")
        assert limiter.allow_request("a") is False

        # Avanzar más allá de la ventana
        fake_clock.advance(11.0)
        assert limiter.allow_request("a") is True

    def test_clientes_independientes(self, fake_clock):
        limiter = FixedWindowRateLimiter(max_requests=1, window_seconds=10.0)
        assert limiter.allow_request("cliente-1") is True
        assert limiter.allow_request("cliente-2") is True
        # El primer cliente ya llegó a su límite
        assert limiter.allow_request("cliente-1") is False
        # El segundo también
        assert limiter.allow_request("cliente-2") is False

    def test_primera_peticion_siempre_permitida(self, fake_clock):
        limiter = FixedWindowRateLimiter(max_requests=5, window_seconds=60.0)
        assert limiter.allow_request("nuevo") is True


# ─────────────────────────────────────────────────────────────────────────────
# SLIDING WINDOW LOG
# ─────────────────────────────────────────────────────────────────────────────


class TestSlidingWindowLogRateLimiter:
    def test_permite_hasta_el_limite(self, fake_clock):
        limiter = SlidingWindowLogRateLimiter(max_requests=3, window_seconds=10.0)
        assert limiter.allow_request("a") is True
        assert limiter.allow_request("a") is True
        assert limiter.allow_request("a") is True

    def test_bloquea_despues_del_limite(self, fake_clock):
        limiter = SlidingWindowLogRateLimiter(max_requests=3, window_seconds=10.0)
        for _ in range(3):
            limiter.allow_request("a")
        assert limiter.allow_request("a") is False

    def test_ventana_deslizante_expira_entradas_antiguas(self, fake_clock):
        limiter = SlidingWindowLogRateLimiter(max_requests=2, window_seconds=10.0)
        limiter.allow_request("a")
        limiter.allow_request("a")
        assert limiter.allow_request("a") is False

        # Avanzar 11s: las dos peticiones anteriores salen de la ventana
        fake_clock.advance(11.0)
        assert limiter.allow_request("a") is True
        assert limiter.allow_request("a") is True
        assert limiter.allow_request("a") is False

    def test_ventana_parcialmente_expirada(self, fake_clock):
        """Solo expiran las peticiones fuera de la ventana, no todas."""
        limiter = SlidingWindowLogRateLimiter(max_requests=3, window_seconds=10.0)
        # t=1000: petición 1 y 2
        limiter.allow_request("a")
        limiter.allow_request("a")
        # t=1005: petición 3
        fake_clock.advance(5.0)
        limiter.allow_request("a")
        # t=1011: peticiones 1 y 2 expiran (>10s), petición 3 sigue dentro
        fake_clock.advance(6.0)
        # Solo 1 petición en ventana → podemos añadir 2 más
        assert limiter.allow_request("a") is True
        assert limiter.allow_request("a") is True
        assert limiter.allow_request("a") is False

    def test_clientes_independientes(self, fake_clock):
        limiter = SlidingWindowLogRateLimiter(max_requests=1, window_seconds=5.0)
        assert limiter.allow_request("x") is True
        assert limiter.allow_request("y") is True
        assert limiter.allow_request("x") is False


# ─────────────────────────────────────────────────────────────────────────────
# TOKEN BUCKET
# ─────────────────────────────────────────────────────────────────────────────


class TestTokenBucketRateLimiter:
    def test_rafaga_inicial_hasta_capacidad(self, fake_clock):
        limiter = TokenBucketRateLimiter(capacity=5, refill_rate=1.0)
        for _ in range(5):
            assert limiter.allow_request("a") is True

    def test_bloquea_cuando_cubo_vacio(self, fake_clock):
        limiter = TokenBucketRateLimiter(capacity=3, refill_rate=1.0)
        for _ in range(3):
            limiter.allow_request("a")
        assert limiter.allow_request("a") is False

    def test_recarga_con_tiempo(self, fake_clock):
        limiter = TokenBucketRateLimiter(capacity=3, refill_rate=2.0)
        for _ in range(3):
            limiter.allow_request("a")
        assert limiter.allow_request("a") is False

        # Avanzar 1s → se añaden 2 tokens → cubo tiene 2
        fake_clock.advance(1.0)
        assert limiter.allow_request("a") is True
        assert limiter.allow_request("a") is True
        assert limiter.allow_request("a") is False

    def test_no_supera_capacidad_maxima(self, fake_clock):
        limiter = TokenBucketRateLimiter(capacity=3, refill_rate=10.0)
        # Avanzar 100s: refill sería 1000 tokens, pero está limitado a capacidad=3
        fake_clock.advance(100.0)
        for _ in range(3):
            assert limiter.allow_request("a") is True
        assert limiter.allow_request("a") is False

    def test_peticion_con_multiples_tokens(self, fake_clock):
        limiter = TokenBucketRateLimiter(capacity=10, refill_rate=1.0)
        # Consumir 6 tokens de una vez
        assert limiter.allow_request("a", tokens=6) is True
        # Solo quedan 4 → no puede consumir 5
        assert limiter.allow_request("a", tokens=5) is False
        # Pero sí puede consumir 4
        assert limiter.allow_request("a", tokens=4) is True

    def test_clientes_independientes(self, fake_clock):
        limiter = TokenBucketRateLimiter(capacity=1, refill_rate=1.0)
        assert limiter.allow_request("x") is True
        assert limiter.allow_request("y") is True
        assert limiter.allow_request("x") is False
        assert limiter.allow_request("y") is False


# ─────────────────────────────────────────────────────────────────────────────
# LEAKY BUCKET
# ─────────────────────────────────────────────────────────────────────────────


class TestLeakyBucketRateLimiter:
    def test_permite_hasta_capacidad(self, fake_clock):
        limiter = LeakyBucketRateLimiter(capacity=3, leak_rate=1.0)
        assert limiter.allow_request("a") is True
        assert limiter.allow_request("a") is True
        assert limiter.allow_request("a") is True

    def test_bloquea_cuando_cubo_lleno(self, fake_clock):
        limiter = LeakyBucketRateLimiter(capacity=3, leak_rate=1.0)
        for _ in range(3):
            limiter.allow_request("a")
        assert limiter.allow_request("a") is False

    def test_vaciado_parcial_con_tiempo(self, fake_clock):
        limiter = LeakyBucketRateLimiter(capacity=3, leak_rate=1.0)
        for _ in range(3):
            limiter.allow_request("a")
        assert limiter.allow_request("a") is False

        # Avanzar 1s → leak_rate=1 → el nivel baja en 1 → hay espacio para 1
        fake_clock.advance(1.0)
        assert limiter.allow_request("a") is True
        assert limiter.allow_request("a") is False

    def test_vaciado_total_con_tiempo(self, fake_clock):
        limiter = LeakyBucketRateLimiter(capacity=3, leak_rate=1.0)
        for _ in range(3):
            limiter.allow_request("a")
        # Avanzar 10s → el cubo se vacía completamente
        fake_clock.advance(10.0)
        for _ in range(3):
            assert limiter.allow_request("a") is True
        assert limiter.allow_request("a") is False

    def test_suavizado_del_trafico(self, fake_clock):
        """El cubo no puede ir por debajo de 0 aunque pase mucho tiempo."""
        limiter = LeakyBucketRateLimiter(capacity=5, leak_rate=2.0)
        # Sin peticiones previas, avanzar tiempo no afecta (nivel ya es 0)
        fake_clock.advance(100.0)
        # Puede aceptar hasta capacidad=5 peticiones
        for _ in range(5):
            assert limiter.allow_request("a") is True
        assert limiter.allow_request("a") is False

    def test_clientes_independientes(self, fake_clock):
        limiter = LeakyBucketRateLimiter(capacity=1, leak_rate=1.0)
        assert limiter.allow_request("nave-1") is True
        assert limiter.allow_request("nave-2") is True
        assert limiter.allow_request("nave-1") is False
        assert limiter.allow_request("nave-2") is False
