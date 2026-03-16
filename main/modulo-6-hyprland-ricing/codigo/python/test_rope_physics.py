"""
test_rope_physics.py — Tests para la Física de Cuerdas
Sub-módulo 6.4: Física de Cuerdas (Rope Physics)

Suite de tests usando pytest para validar la implementación de la
simulación de cuerdas con integración de Verlet.
"""

import math
import pytest

from rope_physics import Point, Constraint, Rope, Simulation


# =============================================================================
# Tests de la clase Point
# =============================================================================


class TestPoint:
    """Tests para la clase Point (partícula con física de Verlet)."""

    def test_point_creation(self):
        """Un punto debe inicializarse con la posición dada y en reposo."""
        p = Point(3.0, 5.0)
        assert p.x == 3.0
        assert p.y == 5.0
        # La posición anterior debe ser igual a la actual (sin velocidad inicial)
        assert p.prev_x == 3.0
        assert p.prev_y == 5.0
        assert p.pinned is False
        assert p.mass == 1.0

    def test_point_creation_pinned(self):
        """Un punto fijado debe tener pinned=True."""
        p = Point(0.0, 0.0, pinned=True)
        assert p.pinned is True

    def test_point_creation_custom_mass(self):
        """Se puede crear un punto con masa personalizada."""
        p = Point(1.0, 2.0, mass=2.5)
        assert p.mass == 2.5


# =============================================================================
# Tests de la clase Rope
# =============================================================================


class TestRope:
    """Tests para la clase Rope (cadena de puntos conectados)."""

    def test_rope_creation(self):
        """La cuerda debe tener el número correcto de puntos y restricciones."""
        cuerda = Rope(0, 0, num_segments=5, segment_length=1.0)
        # Con 5 segmentos hay 6 puntos (num_segments + 1)
        assert len(cuerda.points) == 6
        # Y exactamente 5 restricciones (una por segmento)
        assert len(cuerda.constraints) == 5

    def test_rope_initial_positions(self):
        """Los puntos iniciales deben estar en línea horizontal equidistante."""
        cuerda = Rope(0, 0, num_segments=3, segment_length=2.0)
        assert cuerda.points[0].x == pytest.approx(0.0)
        assert cuerda.points[1].x == pytest.approx(2.0)
        assert cuerda.points[2].x == pytest.approx(4.0)
        assert cuerda.points[3].x == pytest.approx(6.0)
        # Todos los puntos deben empezar a la misma altura (y=0)
        for p in cuerda.points:
            assert p.y == pytest.approx(0.0)

    def test_gravity_moves_points_down(self):
        """La gravedad debe mover los puntos no fijados hacia abajo (y positivo)."""
        cuerda = Rope(0, 0, num_segments=3, segment_length=1.0, gravity=9.8)
        y_inicial = cuerda.points[1].y

        # Ejecutamos varios pasos de simulación
        for _ in range(20):
            cuerda.update(0.016)

        # Los puntos libres deben haber caído (y aumenta hacia abajo)
        assert cuerda.points[1].y > y_inicial, (
            "Los puntos libres deben caer por gravedad"
        )

    def test_pinned_point_stays(self):
        """Un punto fijado no debe moverse por gravedad ni física."""
        cuerda = Rope(0, 0, num_segments=5, segment_length=1.0)
        cuerda.pin(0)  # Fijamos el primer punto

        x_original = cuerda.points[0].x
        y_original = cuerda.points[0].y

        # Ejecutamos muchos pasos de simulación
        for _ in range(100):
            cuerda.update(0.016)

        # El punto fijado no debe haberse movido
        assert cuerda.points[0].x == pytest.approx(x_original)
        assert cuerda.points[0].y == pytest.approx(y_original)

    def test_constraint_satisfaction(self):
        """Las restricciones deben mantener la distancia aproximada entre puntos."""
        cuerda = Rope(0, 0, num_segments=5, segment_length=2.0)
        cuerda.pin(0)

        # Dejamos que la cuerda caiga y se estabilice
        for _ in range(500):
            cuerda.update(0.016)

        # Verificamos que cada segmento mantiene aproximadamente su longitud
        for restriccion in cuerda.constraints:
            dx = restriccion.point_b.x - restriccion.point_a.x
            dy = restriccion.point_b.y - restriccion.point_a.y
            distancia = math.sqrt(dx * dx + dy * dy)
            # Permitimos un 20% de desviación (la simulación es aproximada)
            assert distancia == pytest.approx(restriccion.rest_length, rel=0.2), (
                f"Distancia {distancia:.3f} difiere mucho de "
                f"rest_length {restriccion.rest_length:.3f}"
            )

    def test_verlet_integration(self):
        """La integración de Verlet debe usar la velocidad implícita (pos - prev_pos)."""
        cuerda = Rope(0, 0, num_segments=2, segment_length=1.0, gravity=0.0)
        punto = cuerda.points[1]  # Un punto libre (no fijado)

        # Le damos una "velocidad" moviendo la posición anterior
        # Si prev está en (0.9, 0) y actual en (1.0, 0), la velocidad es (0.1, 0)
        punto.prev_x = punto.x - 0.1
        punto.prev_y = punto.y - 0.05

        x_antes = punto.x
        y_antes = punto.y

        cuerda.update(0.016)

        # El punto debe haberse movido en la dirección de la velocidad implícita
        # (ignoramos las restricciones que pueden ajustar la posición)
        # Solo verificamos que la posición cambió
        cambio_x = punto.x - x_antes
        cambio_y = punto.y - y_antes
        movimiento = math.sqrt(cambio_x**2 + cambio_y**2)
        assert movimiento > 0, "El punto debe moverse por la velocidad implícita de Verlet"

    def test_move_pinned_point(self):
        """Mover un punto fijado debe actualizar su posición correctamente."""
        cuerda = Rope(0, 0, num_segments=3, segment_length=1.0)
        cuerda.pin(0)

        # Movemos el punto fijado a una nueva posición
        cuerda.move_point(0, 10.0, 5.0)

        assert cuerda.points[0].x == pytest.approx(10.0)
        assert cuerda.points[0].y == pytest.approx(5.0)
        # prev también debe actualizarse para evitar saltos
        assert cuerda.points[0].prev_x == pytest.approx(10.0)
        assert cuerda.points[0].prev_y == pytest.approx(5.0)

    def test_pin_and_unpin(self):
        """Pin y unpin deben cambiar el estado de fijación de un punto."""
        cuerda = Rope(0, 0, num_segments=3, segment_length=1.0)

        assert cuerda.points[2].pinned is False
        cuerda.pin(2)
        assert cuerda.points[2].pinned is True
        cuerda.unpin(2)
        assert cuerda.points[2].pinned is False


# =============================================================================
# Tests de estabilidad y simulación
# =============================================================================


class TestSimulation:
    """Tests para la clase Simulation y estabilidad general."""

    def test_multiple_steps_stability(self):
        """La simulación debe permanecer estable después de muchos pasos."""
        cuerda = Rope(0, 0, num_segments=10, segment_length=1.5, gravity=9.8)
        cuerda.pin(0)
        sim = Simulation(cuerda, dt=0.016)

        # Ejecutamos 1000 pasos (equivalente a ~16 segundos de simulación)
        for _ in range(1000):
            sim.step()

        # Verificamos que ningún punto tiene valores NaN o infinitos
        for punto in cuerda.points:
            assert math.isfinite(punto.x), f"x es {punto.x} (no finito)"
            assert math.isfinite(punto.y), f"y es {punto.y} (no finito)"

        # Verificamos que los puntos no se han alejado absurdamente
        for punto in cuerda.points:
            assert abs(punto.x) < 1000, f"x={punto.x} es absurdamente grande"
            assert abs(punto.y) < 1000, f"y={punto.y} es absurdamente grande"

    def test_ascii_render(self):
        """La visualización ASCII debe producir una cadena no vacía."""
        cuerda = Rope(0, 0, num_segments=5, segment_length=2.0)
        cuerda.pin(0)

        # Dejamos caer la cuerda un poco
        for _ in range(50):
            cuerda.update(0.016)

        resultado = cuerda.render_ascii(width=40, height=20)

        assert isinstance(resultado, str)
        assert len(resultado) > 0, "El render ASCII no debe estar vacío"
        # Debe contener al menos un carácter de punto (● o █)
        assert "●" in resultado or "█" in resultado, (
            "El render debe contener caracteres de punto"
        )

    def test_get_state(self):
        """get_state debe retornar la información correcta de todos los puntos."""
        cuerda = Rope(0, 0, num_segments=3, segment_length=1.0)
        cuerda.pin(0)
        sim = Simulation(cuerda)

        estado = sim.get_state()

        assert len(estado) == 4  # 3 segmentos = 4 puntos
        assert estado[0]["pinned"] is True
        assert estado[1]["pinned"] is False
        assert "x" in estado[0]
        assert "y" in estado[0]
        assert "index" in estado[0]


# =============================================================================
# Punto de entrada para ejecución directa
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
