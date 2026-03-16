"""
rope_physics.py — Física de Cuerdas con Integración de Verlet
Sub-módulo 6.4: Física de Cuerdas (Rope Physics)

Implementación educativa de simulación de cuerdas usando el método de
integración de Verlet. Inspirado en el enfoque de zacoons para herramientas
de screenshot con física interactiva en Valle/Qt Quick.

Solo usa la biblioteca estándar de Python (math).
"""

import math


# =============================================================================
# Clase Point: representa una partícula/punto de la cuerda
# =============================================================================

class Point:
    """
    Un punto en el espacio 2D con física de Verlet.

    En la integración de Verlet, NO almacenamos la velocidad explícitamente.
    En su lugar, la velocidad se infiere de la diferencia entre la posición
    actual y la posición anterior:
        velocidad_implícita = posición_actual - posición_anterior

    Atributos:
        x, y: posición actual del punto
        prev_x, prev_y: posición en el paso de tiempo anterior
        pinned: si True, el punto no se mueve (está fijado/anclado)
        mass: masa del punto (afecta cómo responde a fuerzas)
    """

    def __init__(self, x, y, pinned=False, mass=1.0):
        """Inicializa un punto en la posición (x, y)."""
        self.x = x
        self.y = y
        # La posición anterior se inicializa igual a la actual
        # (es decir, el punto comienza en reposo, sin velocidad)
        self.prev_x = x
        self.prev_y = y
        self.pinned = pinned
        self.mass = mass

    def __repr__(self):
        estado = "📌" if self.pinned else "⚪"
        return f"{estado} Point({self.x:.2f}, {self.y:.2f})"


# =============================================================================
# Clase Constraint: conexión rígida entre dos puntos
# =============================================================================

class Constraint:
    """
    Una restricción de distancia entre dos puntos.

    Intenta mantener la distancia entre point_a y point_b igual a
    rest_length. La stiffness (rigidez) controla qué tan fuerte es
    la corrección: 1.0 = totalmente rígido, 0.0 = sin efecto.

    Atributos:
        point_a, point_b: los dos puntos conectados
        rest_length: la distancia ideal entre los puntos
        stiffness: rigidez de la conexión (0.0 a 1.0)
    """

    def __init__(self, point_a, point_b, rest_length=None, stiffness=0.8):
        """
        Crea una restricción entre dos puntos.

        Si no se especifica rest_length, se calcula automáticamente
        como la distancia actual entre los puntos.
        """
        self.point_a = point_a
        self.point_b = point_b
        self.stiffness = stiffness

        if rest_length is None:
            # Calculamos la distancia actual como longitud de reposo
            dx = point_b.x - point_a.x
            dy = point_b.y - point_a.y
            self.rest_length = math.sqrt(dx * dx + dy * dy)
        else:
            self.rest_length = rest_length

    def satisfy(self):
        """
        Corrige las posiciones de los puntos para satisfacer la restricción.

        El algoritmo:
        1. Calcula la distancia actual entre los puntos
        2. Calcula cuánto difiere de la longitud de reposo
        3. Mueve ambos puntos (proporcionalmente) para corregir la diferencia
        """
        dx = self.point_b.x - self.point_a.x
        dy = self.point_b.y - self.point_a.y
        distancia = math.sqrt(dx * dx + dy * dy)

        # Evitamos división por cero si los puntos están en la misma posición
        if distancia < 1e-10:
            return

        # Diferencia relativa respecto a la longitud de reposo
        diferencia = (self.rest_length - distancia) / distancia

        # Desplazamiento necesario para cada eje, multiplicado por rigidez
        offset_x = dx * diferencia * 0.5 * self.stiffness
        offset_y = dy * diferencia * 0.5 * self.stiffness

        # Solo movemos los puntos que NO están fijados (pinned)
        if not self.point_a.pinned:
            self.point_a.x -= offset_x
            self.point_a.y -= offset_y
        if not self.point_b.pinned:
            self.point_b.x += offset_x
            self.point_b.y += offset_y


# =============================================================================
# Clase Rope: una cuerda compuesta de puntos y restricciones
# =============================================================================

class Rope:
    """
    Una cuerda física compuesta de una cadena de puntos conectados.

    La cuerda se crea como una línea recta de puntos equidistantes,
    conectados por restricciones de distancia. La simulación de Verlet
    más las restricciones crean un comportamiento realista de cuerda.

    Atributos:
        points: lista de Point que forman la cuerda
        constraints: lista de Constraint que conectan puntos adyacentes
        gravity: fuerza de gravedad (m/s²)
    """

    def __init__(self, start_x, start_y, num_segments, segment_length, gravity=9.8):
        """
        Crea una cuerda horizontal partiendo de (start_x, start_y).

        Args:
            start_x, start_y: posición del primer punto
            num_segments: número de segmentos (se crean num_segments+1 puntos)
            segment_length: longitud de cada segmento
            gravity: aceleración gravitatoria
        """
        self.gravity = gravity
        self.points = []
        self.constraints = []

        # Creamos los puntos en línea horizontal
        for i in range(num_segments + 1):
            x = start_x + i * segment_length
            y = start_y
            punto = Point(x, y)
            self.points.append(punto)

        # Conectamos cada par de puntos adyacentes con una restricción
        for i in range(num_segments):
            restriccion = Constraint(
                self.points[i],
                self.points[i + 1],
                rest_length=segment_length
            )
            self.constraints.append(restriccion)

    def apply_gravity(self, dt):
        """
        Aplica la fuerza de gravedad a todos los puntos no fijados.

        La gravedad se aplica como una aceleración en el eje Y positivo
        (hacia abajo). En Verlet, la aceleración se añade directamente
        a la posición: pos += aceleración × dt².
        """
        for punto in self.points:
            if not punto.pinned:
                # En Verlet, la aceleración se aplica así:
                # nueva_pos = pos + (pos - prev_pos) + accel * dt²
                # Aquí solo aplicamos la parte de la aceleración
                punto.y += self.gravity * dt * dt

    def apply_constraints(self, iterations=5):
        """
        Satisface las restricciones de distancia iterativamente.

        Más iteraciones = cuerda más rígida y precisa, pero más costoso.
        Típicamente 3-10 iteraciones son suficientes para resultados buenos.
        """
        for _ in range(iterations):
            for restriccion in self.constraints:
                restriccion.satisfy()

    def update(self, dt):
        """
        Realiza un paso completo de la simulación.

        El orden es importante:
        1. Integración de Verlet (mover puntos según su inercia)
        2. Aplicar gravedad
        3. Satisfacer restricciones (múltiples iteraciones)
        """
        # Paso 1: Integración de Verlet para cada punto libre
        for punto in self.points:
            if not punto.pinned:
                # Calculamos la "velocidad" implícita
                vel_x = punto.x - punto.prev_x
                vel_y = punto.y - punto.prev_y

                # Guardamos la posición actual como "anterior"
                punto.prev_x = punto.x
                punto.prev_y = punto.y

                # Nueva posición = actual + velocidad (+ aceleración en el paso siguiente)
                punto.x += vel_x
                punto.y += vel_y

        # Paso 2: Aplicar gravedad
        self.apply_gravity(dt)

        # Paso 3: Satisfacer restricciones
        self.apply_constraints(iterations=5)

    def pin(self, index):
        """Fija un punto para que no se mueva con la física."""
        if 0 <= index < len(self.points):
            self.points[index].pinned = True

    def unpin(self, index):
        """Libera un punto para que se mueva con la física."""
        if 0 <= index < len(self.points):
            self.points[index].pinned = False

    def move_point(self, index, x, y):
        """
        Mueve un punto fijado a una nueva posición.

        Esto simula el "arrastre" interactivo. Solo funciona con
        puntos fijados (pinned) para evitar interferir con la física.
        """
        if 0 <= index < len(self.points) and self.points[index].pinned:
            self.points[index].x = x
            self.points[index].y = y
            # También actualizamos prev para evitar un salto brusco
            self.points[index].prev_x = x
            self.points[index].prev_y = y

    def render_ascii(self, width=60, height=30):
        """
        Genera una visualización ASCII de la cuerda.

        Mapea las coordenadas de los puntos a una cuadrícula de caracteres
        para poder ver la cuerda en la terminal.

        Returns:
            str: representación ASCII de la cuerda
        """
        # Encontramos los límites de la simulación
        if not self.points:
            return ""

        min_x = min(p.x for p in self.points)
        max_x = max(p.x for p in self.points)
        min_y = min(p.y for p in self.points)
        max_y = max(p.y for p in self.points)

        # Añadimos un margen para que los puntos no queden en el borde
        rango_x = max(max_x - min_x, 1.0)
        rango_y = max(max_y - min_y, 1.0)

        # Creamos la cuadrícula vacía
        cuadricula = [["·" for _ in range(width)] for _ in range(height)]

        # Colocamos cada punto en la cuadrícula
        for i, punto in enumerate(self.points):
            # Mapeamos coordenadas del mundo a coordenadas de cuadrícula
            col = int((punto.x - min_x) / rango_x * (width - 1))
            fila = int((punto.y - min_y) / rango_y * (height - 1))

            # Aseguramos que estamos dentro de los límites
            col = max(0, min(width - 1, col))
            fila = max(0, min(height - 1, fila))

            # Usamos diferentes caracteres para puntos fijados y libres
            if punto.pinned:
                cuadricula[fila][col] = "█"
            else:
                cuadricula[fila][col] = "●"

        # Convertimos la cuadrícula a texto
        lineas = ["".join(fila) for fila in cuadricula]
        return "\n".join(lineas)


# =============================================================================
# Clase Simulation: gestiona el bucle de simulación
# =============================================================================

class Simulation:
    """
    Gestiona la simulación de la cuerda.

    Encapsula la cuerda y proporciona métodos para avanzar la simulación
    paso a paso y consultar el estado actual.
    """

    def __init__(self, rope, dt=0.016):
        """
        Args:
            rope: instancia de Rope a simular
            dt: paso de tiempo (por defecto ~60 FPS)
        """
        self.rope = rope
        self.dt = dt
        self.paso_actual = 0

    def step(self):
        """Avanza la simulación un paso de tiempo."""
        self.rope.update(self.dt)
        self.paso_actual += 1

    def get_state(self):
        """
        Retorna el estado actual de todos los puntos.

        Returns:
            list[dict]: lista con la posición y estado de cada punto
        """
        estado = []
        for i, punto in enumerate(self.rope.points):
            estado.append({
                "index": i,
                "x": punto.x,
                "y": punto.y,
                "pinned": punto.pinned,
            })
        return estado


# =============================================================================
# Demostración: cuerda colgante con visualización ASCII
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("🧵 Simulación de Física de Cuerdas — Integración de Verlet")
    print("=" * 60)
    print()

    # Creamos una cuerda de 10 segmentos, cada uno de 2 unidades de largo
    cuerda = Rope(
        start_x=5.0,
        start_y=0.0,
        num_segments=10,
        segment_length=2.0,
        gravity=9.8
    )

    # Fijamos el primer punto (la cuerda "cuelga" desde la izquierda)
    cuerda.pin(0)

    # Creamos la simulación
    sim = Simulation(cuerda, dt=0.016)

    # Simulamos varios pasos para que la cuerda caiga y se estabilice
    print("Simulando 200 pasos de física...")
    print()

    # Mostramos el estado en algunos momentos clave
    for paso in range(200):
        sim.step()

        # Mostramos visualización en pasos específicos
        if paso in [0, 49, 99, 199]:
            print(f"--- Paso {paso + 1} ---")
            print(cuerda.render_ascii(width=50, height=20))
            print()

    # Estado final
    print("Estado final de los puntos:")
    for info in sim.get_state():
        estado = "📌 fijado" if info["pinned"] else "⚪ libre"
        print(f"  Punto {info['index']:2d}: "
              f"({info['x']:7.2f}, {info['y']:7.2f}) {estado}")

    print()
    print("✅ Simulación completada exitosamente")
