// ============================================================
// nine_slice.cpp — Implementación del Motor de 9-Slice Scaling
// Sub-módulo 6.1: El Arquitecto de Bordes
//
// Este archivo contiene la implementación completa del sistema
// de 9-slice scaling, una técnica fundamental para renderizar
// bordes de ventana personalizados en compositores como Hyprland.
// ============================================================

#include "nine_slice.hpp"
#include <algorithm>
#include <sstream>

// ============================================================
//  CLASE IMAGE — Buffer de píxeles 2D
// ============================================================

// Constructor por defecto: imagen vacía (0×0)
Image::Image() : width_(0), height_(0) {}

// Constructor con dimensiones: crea imagen negra (píxeles por defecto)
Image::Image(int width, int height)
    : data_(static_cast<size_t>(width * height)), width_(width), height_(height) {
    // El vector se inicializa con Pixel() por defecto (negro, alfa=255).
    // Usamos static_cast para evitar warnings de conversión signed→unsigned.
    if (width < 0 || height < 0) {
        throw std::invalid_argument("Las dimensiones de la imagen deben ser >= 0");
    }
}

// Constructor con color de relleno
Image::Image(int width, int height, Pixel fill)
    : data_(static_cast<size_t>(width * height), fill), width_(width), height_(height) {
    if (width < 0 || height < 0) {
        throw std::invalid_argument("Las dimensiones de la imagen deben ser >= 0");
    }
}

// ---------------------------------------------------------------
// Destructor — RAII en acción
// ---------------------------------------------------------------
// En C++, el destructor se llama automáticamente cuando un objeto
// sale de su ámbito (scope). Esto es el corazón del patrón RAII:
// los recursos se liberan de forma determinista, sin necesidad de
// llamar manualmente a free() o delete.
//
// En un plugin real de Hyprland, aquí liberaríamos:
//   - Texturas de GPU (glDeleteTextures)
//   - Buffers de Wayland (wl_buffer_destroy)
//   - Handles de shm (close/munmap)
//
// En nuestro caso educativo, std::vector maneja su propia memoria,
// pero el destructor nos permite observar cuándo ocurre la limpieza.
// ---------------------------------------------------------------
Image::~Image() {
    // En modo educativo, podemos descomentar la siguiente línea
    // para ver cuándo se destruyen las imágenes:
    // std::cerr << "[~Image] Liberando imagen de " << width_ << "x" << height_
    //           << " (" << data_.size() << " píxeles)" << std::endl;

    // std::vector<Pixel> se destruye automáticamente aquí (RAII).
    // No necesitamos hacer nada explícito — esa es la belleza del patrón.
}

// ---------------------------------------------------------------
// Constructor de copia — Copia profunda
// ---------------------------------------------------------------
// Cuando copiamos una imagen, creamos un duplicado COMPLETO del
// buffer de píxeles. Esto es seguro pero potencialmente costoso
// para imágenes grandes.
Image::Image(const Image& other)
    : data_(other.data_), width_(other.width_), height_(other.height_) {
    // std::vector implementa copia profunda internamente.
    // Cada Image posee su propia copia independiente de los datos.
}

// ---------------------------------------------------------------
// Constructor de movimiento — Transferencia de propiedad
// ---------------------------------------------------------------
// El movimiento es mucho más eficiente que la copia: en lugar de
// duplicar los datos, simplemente "robamos" el buffer interno del
// objeto fuente. El objeto fuente queda en un estado válido pero
// vacío (moved-from state).
//
// Esto es crucial para rendimiento en compositores gráficos donde
// se crean y destruyen imágenes constantemente.
Image::Image(Image&& other) noexcept
    : data_(std::move(other.data_)), width_(other.width_), height_(other.height_) {
    // Dejamos el objeto fuente en estado vacío
    other.width_ = 0;
    other.height_ = 0;
}

// Operador de asignación por copia
Image& Image::operator=(const Image& other) {
    if (this != &other) {
        data_ = other.data_;
        width_ = other.width_;
        height_ = other.height_;
    }
    return *this;
}

// Operador de asignación por movimiento
Image& Image::operator=(Image&& other) noexcept {
    if (this != &other) {
        data_ = std::move(other.data_);
        width_ = other.width_;
        height_ = other.height_;
        other.width_ = 0;
        other.height_ = 0;
    }
    return *this;
}

int Image::width() const { return width_; }
int Image::height() const { return height_; }
bool Image::empty() const { return width_ == 0 || height_ == 0; }

Pixel Image::get(int x, int y) const {
    if (x < 0 || x >= width_ || y < 0 || y >= height_) {
        throw std::out_of_range("Coordenadas fuera de los límites de la imagen: ("
            + std::to_string(x) + ", " + std::to_string(y) + ") en imagen de "
            + std::to_string(width_) + "x" + std::to_string(height_));
    }
    return data_[static_cast<size_t>(y * width_ + x)];
}

void Image::set(int x, int y, Pixel pixel) {
    if (x < 0 || x >= width_ || y < 0 || y >= height_) {
        throw std::out_of_range("Coordenadas fuera de los límites de la imagen: ("
            + std::to_string(x) + ", " + std::to_string(y) + ") en imagen de "
            + std::to_string(width_) + "x" + std::to_string(height_));
    }
    data_[static_cast<size_t>(y * width_ + x)] = pixel;
}

// ---------------------------------------------------------------
// subimage — Extraer una sub-región rectangular
// ---------------------------------------------------------------
// Esta función es fundamental para el 9-slice: nos permite extraer
// cada una de las 9 regiones de la imagen fuente.
Image Image::subimage(int x, int y, int w, int h) const {
    if (x < 0 || y < 0 || w < 0 || h < 0 ||
        x + w > width_ || y + h > height_) {
        throw std::out_of_range(
            "Sub-región fuera de los límites: (" + std::to_string(x) + ", "
            + std::to_string(y) + ", " + std::to_string(w) + "x" + std::to_string(h)
            + ") en imagen de " + std::to_string(width_) + "x" + std::to_string(height_));
    }

    Image result(w, h);
    for (int row = 0; row < h; ++row) {
        for (int col = 0; col < w; ++col) {
            result.set(col, row, get(x + col, y + row));
        }
    }
    return result;
}

// ---------------------------------------------------------------
// print_ascii — Visualización en terminal
// ---------------------------------------------------------------
// Mapea la luminosidad de cada píxel a un carácter ASCII.
// Útil para depuración cuando no tenemos un entorno gráfico
// (como en un servidor CI o una sesión SSH).
void Image::print_ascii() const {
    // Caracteres ordenados de más oscuro a más brillante
    const char* brightness = " .:-=+*#%@";
    const int levels = 10;

    for (int y = 0; y < height_; ++y) {
        for (int x = 0; x < width_; ++x) {
            Pixel p = get(x, y);
            // Calcular luminosidad percibida (fórmula ITU-R BT.601)
            int lum = (299 * p.r + 587 * p.g + 114 * p.b) / 1000;
            int index = (lum * (levels - 1)) / 255;
            index = std::max(0, std::min(levels - 1, index));
            std::cout << brightness[index] << brightness[index];
        }
        std::cout << '\n';
    }
}


// ============================================================
//  CLASE NINESLICESCALER — Motor de 9-Slice
// ============================================================

NineSliceScaler::NineSliceScaler(const Image& source, SliceMargins margins)
    : source_(source), margins_(margins), sliced_(false) {}

NineSliceScaler::~NineSliceScaler() {
    // Aquí es donde se liberan los recursos del scaler.
    // En un plugin de Hyprland, liberaríamos las texturas GPU
    // de cada una de las 9 regiones cacheadas.
    // Gracias a RAII, las Images dentro de NineSliceRegions
    // se destruyen automáticamente al destruirse este objeto.
}

// ---------------------------------------------------------------
// slice() — Dividir la imagen fuente en 9 regiones
// ---------------------------------------------------------------
//
// La imagen se divide así (donde L=left, R=right, T=top, B=bottom):
//
//     0         L                  W-R        W
//     ┌─────────┬──────────────────┬─────────┐ 0
//     │ top_left│   top_center     │top_right│
//     ├─────────┼──────────────────┼─────────┤ T
//     │ mid_left│   mid_center     │mid_right│
//     ├─────────┼──────────────────┼─────────┤ H-B
//     │ bot_left│   bot_center     │bot_right│
//     └─────────┴──────────────────┴─────────┘ H
//
void NineSliceScaler::slice() {
    int w = source_.width();
    int h = source_.height();
    int L = margins_.left;
    int R = margins_.right;
    int T = margins_.top;
    int B = margins_.bottom;

    // Validar que los márgenes no excedan las dimensiones de la imagen
    if (L + R > w) {
        throw std::invalid_argument(
            "Los márgenes horizontales (" + std::to_string(L) + " + "
            + std::to_string(R) + " = " + std::to_string(L + R)
            + ") exceden el ancho de la imagen (" + std::to_string(w) + ")");
    }
    if (T + B > h) {
        throw std::invalid_argument(
            "Los márgenes verticales (" + std::to_string(T) + " + "
            + std::to_string(B) + " = " + std::to_string(T + B)
            + ") exceden la altura de la imagen (" + std::to_string(h) + ")");
    }

    // Dimensiones de la zona central
    int center_w = w - L - R;
    int center_h = h - T - B;

    // Fila superior: esquinas fijas + borde horizontal
    regions_.top_left     = source_.subimage(0,           0, L,        T);
    regions_.top_center   = source_.subimage(L,           0, center_w, T);
    regions_.top_right    = source_.subimage(w - R,       0, R,        T);

    // Fila central: bordes verticales + centro expandible
    regions_.middle_left   = source_.subimage(0,           T, L,        center_h);
    regions_.middle_center = source_.subimage(L,           T, center_w, center_h);
    regions_.middle_right  = source_.subimage(w - R,       T, R,        center_h);

    // Fila inferior: esquinas fijas + borde horizontal
    regions_.bottom_left   = source_.subimage(0,           h - B, L,        B);
    regions_.bottom_center = source_.subimage(L,           h - B, center_w, B);
    regions_.bottom_right  = source_.subimage(w - R,       h - B, R,        B);

    sliced_ = true;
}

// ---------------------------------------------------------------
// scale_region — Escalado nearest-neighbor
// ---------------------------------------------------------------
// El muestreo de vecino más cercano (nearest-neighbor) es el método
// más simple de escalado: para cada píxel del destino, encontramos
// el píxel más cercano en la fuente.
//
// Ventajas: rápido, preserva bordes nítidos (ideal para pixel art)
// Desventajas: puede producir artefactos de aliasing
//
// En producción, un compositor como Hyprland usaría interpolación
// bilineal o incluso bicúbica para bordes más suaves, pero para
// fines educativos, nearest-neighbor es perfecto.
Image NineSliceScaler::scale_region(const Image& src, int target_width, int target_height) {
    if (src.empty() || target_width <= 0 || target_height <= 0) {
        return Image(target_width, target_height);
    }

    Image result(target_width, target_height);

    for (int y = 0; y < target_height; ++y) {
        for (int x = 0; x < target_width; ++x) {
            // Mapear coordenadas del destino al origen
            // Fórmula: src_coord = dest_coord * src_size / dest_size
            int src_x = x * src.width() / target_width;
            int src_y = y * src.height() / target_height;

            // Clamping para evitar accesos fuera de rango
            src_x = std::min(src_x, src.width() - 1);
            src_y = std::min(src_y, src.height() - 1);

            result.set(x, y, src.get(src_x, src_y));
        }
    }

    return result;
}

// ---------------------------------------------------------------
// blit — Copiar píxeles de una imagen a otra
// ---------------------------------------------------------------
// "Blit" viene de "bit block transfer", una operación fundamental
// en gráficos por computadora. Copia los píxeles de src sobre dest
// en la posición (dest_x, dest_y).
void NineSliceScaler::blit(Image& dest, const Image& src, int dest_x, int dest_y) {
    for (int y = 0; y < src.height(); ++y) {
        for (int x = 0; x < src.width(); ++x) {
            int dx = dest_x + x;
            int dy = dest_y + y;
            if (dx >= 0 && dx < dest.width() && dy >= 0 && dy < dest.height()) {
                dest.set(dx, dy, src.get(x, y));
            }
        }
    }
}

// ---------------------------------------------------------------
// render — Componer las 9 regiones en el tamaño final
// ---------------------------------------------------------------
// Esta es la función principal del 9-slice scaling. Toma las 9
// regiones extraídas y las compone en una imagen del tamaño
// objetivo (típicamente el tamaño de la ventana + decoraciones).
//
// Distribución del espacio:
//   - Las esquinas mantienen su tamaño original (no se escalan)
//   - Los bordes horizontales se estiran al ancho disponible
//   - Los bordes verticales se estiran a la altura disponible
//   - El centro se estira en ambas direcciones
//
// Esto garantiza que las esquinas decorativas nunca se deformen,
// los bordes se adaptan suavemente, y el centro rellena el espacio.
Image NineSliceScaler::render(int target_width, int target_height) const {
    if (!sliced_) {
        throw std::logic_error(
            "Debe llamar a slice() antes de render(). "
            "Las 9 regiones aún no han sido extraídas.");
    }

    int L = margins_.left;
    int R = margins_.right;
    int T = margins_.top;
    int B = margins_.bottom;

    // Validar que el tamaño objetivo puede contener al menos las esquinas
    if (target_width < L + R || target_height < T + B) {
        throw std::invalid_argument(
            "El tamaño objetivo (" + std::to_string(target_width) + "x"
            + std::to_string(target_height) + ") es menor que la suma de márgenes ("
            + std::to_string(L + R) + "x" + std::to_string(T + B) + ")");
    }

    // Dimensiones del área central en el resultado
    int center_w = target_width - L - R;
    int center_h = target_height - T - B;

    // Crear la imagen de salida
    Image output(target_width, target_height);

    // --- Fila superior ---
    // Esquina superior izquierda: tamaño fijo (L × T)
    blit(output, regions_.top_left, 0, 0);

    // Borde superior: se estira horizontalmente a center_w × T
    if (center_w > 0 && T > 0) {
        Image scaled_top = scale_region(regions_.top_center, center_w, T);
        blit(output, scaled_top, L, 0);
    }

    // Esquina superior derecha: tamaño fijo (R × T)
    blit(output, regions_.top_right, target_width - R, 0);

    // --- Fila central ---
    // Borde izquierdo: se estira verticalmente a L × center_h
    if (L > 0 && center_h > 0) {
        Image scaled_left = scale_region(regions_.middle_left, L, center_h);
        blit(output, scaled_left, 0, T);
    }

    // Centro: se estira en ambas direcciones a center_w × center_h
    if (center_w > 0 && center_h > 0) {
        Image scaled_center = scale_region(regions_.middle_center, center_w, center_h);
        blit(output, scaled_center, L, T);
    }

    // Borde derecho: se estira verticalmente a R × center_h
    if (R > 0 && center_h > 0) {
        Image scaled_right = scale_region(regions_.middle_right, R, center_h);
        blit(output, scaled_right, target_width - R, T);
    }

    // --- Fila inferior ---
    // Esquina inferior izquierda: tamaño fijo (L × B)
    blit(output, regions_.bottom_left, 0, target_height - B);

    // Borde inferior: se estira horizontalmente a center_w × B
    if (center_w > 0 && B > 0) {
        Image scaled_bottom = scale_region(regions_.bottom_center, center_w, B);
        blit(output, scaled_bottom, L, target_height - B);
    }

    // Esquina inferior derecha: tamaño fijo (R × B)
    blit(output, regions_.bottom_right, target_width - R, target_height - B);

    return output;
}

const NineSliceRegions& NineSliceScaler::regions() const {
    if (!sliced_) {
        throw std::logic_error("Debe llamar a slice() antes de acceder a las regiones.");
    }
    return regions_;
}

bool NineSliceScaler::is_sliced() const { return sliced_; }


// ============================================================
//  PROGRAMA PRINCIPAL — Demostración de 9-Slice Scaling
// ============================================================
#ifndef TESTING

// Crear una imagen de borde de ejemplo con colores distintos por región.
// Usamos una imagen de 12×12 donde cada zona de 3px tiene un color único.
static Image create_sample_border() {
    int size = 12;
    Image img(size, size);

    // Definir colores por zona para fácil identificación visual
    Pixel corner_tl(255, 100, 100);   // Rojo claro — esquinas sup-izq
    Pixel corner_tr(100, 255, 100);   // Verde claro — esquinas sup-der
    Pixel corner_bl(100, 100, 255);   // Azul claro — esquinas inf-izq
    Pixel corner_br(255, 255, 100);   // Amarillo — esquinas inf-der
    Pixel edge_top(200, 150, 150);    // Rosa — borde superior
    Pixel edge_bottom(150, 150, 200); // Lavanda — borde inferior
    Pixel edge_left(150, 200, 150);   // Menta — borde izquierdo
    Pixel edge_right(200, 200, 150);  // Crema — borde derecho
    Pixel center(180, 180, 180);      // Gris — centro

    int margin = 3;

    for (int y = 0; y < size; ++y) {
        for (int x = 0; x < size; ++x) {
            bool is_top    = (y < margin);
            bool is_bottom = (y >= size - margin);
            bool is_left   = (x < margin);
            bool is_right  = (x >= size - margin);

            Pixel p = center; // Por defecto: centro

            if (is_top && is_left)        p = corner_tl;
            else if (is_top && is_right)  p = corner_tr;
            else if (is_bottom && is_left)  p = corner_bl;
            else if (is_bottom && is_right) p = corner_br;
            else if (is_top)              p = edge_top;
            else if (is_bottom)           p = edge_bottom;
            else if (is_left)             p = edge_left;
            else if (is_right)            p = edge_right;

            img.set(x, y, p);
        }
    }

    return img;
}

int main() {
    std::cout << "╔══════════════════════════════════════════════════╗\n";
    std::cout << "║  Sub-módulo 6.1: El Arquitecto de Bordes        ║\n";
    std::cout << "║  Demostración de 9-Slice Scaling                 ║\n";
    std::cout << "╚══════════════════════════════════════════════════╝\n\n";

    // --- Paso 1: Crear la imagen fuente ---
    std::cout << "=== Paso 1: Imagen fuente (12×12) ===\n";
    std::cout << "Cada zona tiene un color distinto para identificar las regiones.\n\n";
    Image source = create_sample_border();
    source.print_ascii();

    // --- Paso 2: Crear el scaler y dividir en 9 regiones ---
    std::cout << "\n=== Paso 2: Dividir en 9 regiones (márgenes de 3px) ===\n";
    SliceMargins margins(3);
    NineSliceScaler scaler(source, margins);
    scaler.slice();
    std::cout << "¡Imagen dividida exitosamente en 9 regiones!\n";

    // Mostrar las regiones individuales
    const auto& regions = scaler.regions();
    std::cout << "\n  Esquina superior izquierda ("
              << regions.top_left.width() << "×" << regions.top_left.height() << "):\n";
    regions.top_left.print_ascii();

    std::cout << "\n  Borde superior ("
              << regions.top_center.width() << "×" << regions.top_center.height() << "):\n";
    regions.top_center.print_ascii();

    std::cout << "\n  Centro ("
              << regions.middle_center.width() << "×" << regions.middle_center.height() << "):\n";
    regions.middle_center.print_ascii();

    // --- Paso 3: Renderizar a diferentes tamaños ---
    std::cout << "\n=== Paso 3: Renderizar a 20×15 ===\n";
    std::cout << "Las esquinas mantienen su tamaño (3×3), los bordes se estiran.\n\n";
    Image rendered_small = scaler.render(20, 15);
    rendered_small.print_ascii();

    std::cout << "\n=== Paso 4: Renderizar a 30×20 ===\n";
    std::cout << "Mismo borde, ventana más grande — las esquinas siguen intactas.\n\n";
    Image rendered_large = scaler.render(30, 20);
    rendered_large.print_ascii();

    // --- Demostración RAII ---
    std::cout << "\n=== Demostración RAII ===\n";
    std::cout << "Los objetos Image se destruyen automáticamente al salir del scope.\n";
    std::cout << "En un plugin de Hyprland, esto liberaría las texturas de GPU.\n";
    {
        std::cout << "  Entrando en scope interno...\n";
        Image temp(5, 5, Pixel(255, 0, 0));
        std::cout << "  Imagen temporal creada (5×5, roja)\n";
        std::cout << "  Saliendo del scope — el destructor se llamará automáticamente\n";
    }
    std::cout << "  ¡Scope cerrado! La imagen temporal ha sido destruida.\n";

    std::cout << "\n✓ Demostración completada exitosamente.\n";
    return 0;
}

#endif // TESTING
