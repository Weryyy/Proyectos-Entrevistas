# Sub-módulo 6.4: Física de Cuerdas — Rope Physics con Integración de Verlet

## ¿Qué es la Integración de Verlet?

La **integración de Verlet** es un método numérico para simular el movimiento
de partículas en sistemas físicos. A diferencia del método de Euler (que usa
velocidad explícita), Verlet calcula la nueva posición basándose en la
**posición actual** y la **posición anterior**:

```
nueva_posición = 2 × posición_actual − posición_anterior + aceleración × dt²
```

### ¿Por qué Verlet y no Euler?

| Característica     | Euler              | Verlet              |
|--------------------|--------------------|---------------------|
| Estabilidad        | Baja               | **Alta**            |
| Conserva energía   | No                 | **Aproximadamente** |
| Complejidad        | Simple             | Simple              |
| Velocidad explícita| Sí                 | **No (implícita)**  |

La velocidad en Verlet está **implícita** en la diferencia entre la posición
actual y la anterior. Esto lo hace especialmente estable para simulaciones
con restricciones (constraints), como las cuerdas.

## ¿Qué son los Constraints (Restricciones)?

En una simulación de cuerda, cada segmento tiene una **longitud de reposo**
que debe mantenerse. Después de mover las partículas con Verlet, las
distancias entre puntos conectados pueden violarse. Los constraints se
satisfacen iterativamente:

```
1. Calcular la distancia actual entre dos puntos conectados
2. Calcular la diferencia con la longitud de reposo
3. Mover ambos puntos hacia/desde el otro para corregir la distancia
4. Repetir N veces (más iteraciones = más precisión)
```

Este proceso se llama **relajación de restricciones** y es la clave para
que la cuerda se comporte de manera realista.

## El Enfoque de zacoons

El usuario **zacoons** implementó física de cuerdas para una herramienta
de capturas de pantalla en **Valle** (framework basado en Qt Quick). La
cuerda conectaba visualmente el área de selección con un punto de anclaje,
creando una interacción lúdica e intuitiva.

### Aplicaciones en ricing:
- **Herramienta de screenshot**: la selección "cuelga" de una cuerda
- **Decoraciones de ventanas**: cuerdas que conectan elementos visuales
- **Animaciones orgánicas**: movimiento natural sin keyframes manuales
- **Efectos de partículas**: cadenas de puntos con gravedad

## Implementación en Python

Nuestra implementación incluye:

1. **`Point`**: partícula con posición, posición anterior, masa y estado de fijación
2. **`Constraint`**: conexión entre dos puntos con longitud de reposo y rigidez
3. **`Rope`**: cadena de puntos conectados que forman la cuerda
4. **`Simulation`**: bucle principal que coordina la física

### Características:
- **Solo biblioteca estándar** de Python (sin NumPy ni dependencias externas)
- **Visualización ASCII** para depuración en terminal
- **Puntos fijables** (pinned) que no se mueven con la gravedad
- **Arrastre interactivo** de puntos fijados

## Archivos en este directorio

| Archivo | Descripción |
|---------|-------------|
| `rope_physics.py` | Implementación completa de la simulación de cuerdas |
| `test_rope_physics.py` | Suite de tests con pytest |

## Ejecución

```bash
# Ejecutar la demostración con visualización ASCII
python rope_physics.py

# Ejecutar los tests
pytest test_rope_physics.py -v
```
