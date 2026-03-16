# Sub-módulo 6.1: El Arquitecto de Bordes — 9-Slice Scaling

## ¿Qué es el 9-Slice Scaling?

El **9-slice scaling** (también conocido como *9-patch* o *border scaling*) es una técnica
de escalado de imágenes que permite redimensionar bordes decorativos a **cualquier tamaño**
sin distorsión visual.

La idea fundamental es dividir una imagen de borde en **9 regiones**:

```
┌─────────────┬─────────────────────────┬─────────────┐
│             │                         │             │
│  Esquina    │    Borde Superior       │  Esquina    │
│  Superior   │    (estira en X)        │  Superior   │
│  Izquierda  │                         │  Derecha    │
│  (fija)     │                         │  (fija)     │
├─────────────┼─────────────────────────┼─────────────┤
│             │                         │             │
│  Borde      │       Centro            │  Borde      │
│  Izquierdo  │    (estira en X e Y)    │  Derecho    │
│  (estira    │                         │  (estira    │
│   en Y)     │                         │   en Y)     │
│             │                         │             │
├─────────────┼─────────────────────────┼─────────────┤
│             │                         │             │
│  Esquina    │    Borde Inferior       │  Esquina    │
│  Inferior   │    (estira en X)        │  Inferior   │
│  Izquierda  │                         │  Derecha    │
│  (fija)     │                         │  (fija)     │
└─────────────┴─────────────────────────┴─────────────┘
```

### Reglas de escalado por región

| Región             | Escala en X | Escala en Y | Comportamiento                     |
|--------------------|:-----------:|:-----------:|------------------------------------|
| 4 Esquinas         |     ✗       |     ✗       | Tamaño fijo, nunca se deforman     |
| Borde Sup/Inf      |     ✓       |     ✗       | Se estiran solo horizontalmente    |
| Borde Izq/Der      |     ✗       |     ✓       | Se estiran solo verticalmente      |
| Centro             |     ✓       |     ✓       | Se estira en ambas direcciones     |

## ¿Por qué usar esto en Hyprland?

[Hyprland](https://hyprland.org/) es un compositor Wayland dinámico que permite una
personalización visual extrema a través de plugins en C++. Cuando queremos que cada
ventana tenga un **borde temático personalizado** (por ejemplo, bordes con texturas,
gradientes o patrones artísticos), el 9-slice scaling es la técnica ideal porque:

1. **Independencia del tamaño**: Una ventana puede tener cualquier dimensión y el borde
   se adapta perfectamente sin pixelarse ni deformarse.
2. **Eficiencia**: Solo necesitamos almacenar una imagen de borde pequeña; el escalado
   se hace en tiempo de renderizado.
3. **Consistencia visual**: Las esquinas decorativas mantienen siempre sus proporciones
   originales, mientras los bordes se repiten/estiran suavemente.

## Destructores y RAII en C++

Un concepto **crítico** para el desarrollo de plugins de Hyprland es el manejo correcto
de recursos mediante el patrón **RAII** (*Resource Acquisition Is Initialization*).

### ¿Qué es RAII?

RAII garantiza que los recursos (memoria, texturas GPU, handles de archivo) se adquieren
en el constructor y se liberan **automáticamente** en el destructor:

```cpp
class TexturaBorde {
    GLuint textura_id_;
public:
    TexturaBorde(const char* path) {
        // Constructor: carga la textura en la GPU
        glGenTextures(1, &textura_id_);
        // ... cargar datos ...
    }
    ~TexturaBorde() {
        // Destructor: libera la textura de la GPU
        glDeleteTextures(1, &textura_id_);
    }
};
```

### ¿Por qué es crucial en plugins de Hyprland?

En un compositor Wayland, los recursos gráficos están **compartidos con el servidor
de display**. Si un plugin no libera correctamente:

- **Texturas GPU** → fuga de memoria de video, eventualmente crashea el compositor
- **Buffers de superficie** → corrupción visual o segfaults
- **Handles de archivo** → agotamiento de file descriptors del sistema

Nuestro código implementa RAII en la clase `Image`: el destructor se encarga de limpiar
el buffer de píxeles, y los constructores de copia/movimiento manejan correctamente
la semántica de propiedad.

## Compilación y Ejecución

### Requisitos

- Compilador C++17 (g++ 8+ o clang++ 7+)
- Make

### Compilar todo

```bash
make all
```

### Ejecutar la demostración

```bash
make run
```

Esto crea una imagen de borde de ejemplo, la divide en 9 regiones y la renderiza
a diferentes tamaños, mostrando el resultado como arte ASCII en la terminal.

### Ejecutar los tests

```bash
make test
```

Los tests verifican:
- Creación y acceso a píxeles de imágenes
- Extracción de sub-regiones
- Semántica de copia y movimiento (RAII)
- Validación de márgenes
- Renderizado a diferentes tamaños
- Preservación de esquinas y estiramiento de bordes
- Pipeline completo de 9-slice scaling

### Limpiar

```bash
make clean
```

## Estructura de Archivos

```
cpp/
├── README.md              ← Este archivo
├── Makefile               ← Sistema de compilación
├── nine_slice.hpp         ← Definiciones de clases (Image, NineSliceScaler)
├── nine_slice.cpp         ← Implementación + programa principal de demostración
└── test_nine_slice.cpp    ← Tests unitarios con assert
```
