// ============================================================
// test_nine_slice.cpp — Tests unitarios para el Motor de 9-Slice
// Sub-módulo 6.1: El Arquitecto de Bordes
//
// Usa assert() para verificaciones — no requiere framework externo.
// Cada test está documentado en español explicando qué se verifica.
// ============================================================

#ifndef TESTING
#define TESTING
#endif
#include "nine_slice.cpp"
#include <cassert>
#include <iostream>
#include <sstream>

static int tests_passed = 0;
static int tests_total = 0;

#define RUN_TEST(func) do { \
    tests_total++; \
    std::cout << "  Ejecutando: " #func "... "; \
    try { \
        func(); \
        tests_passed++; \
        std::cout << "✓ OK\n"; \
    } catch (const std::exception& e) { \
        std::cout << "✗ FALLÓ: " << e.what() << "\n"; \
    } catch (...) { \
        std::cout << "✗ FALLÓ: excepción desconocida\n"; \
    } \
} while(0)

// ============================================================
// Test 1: Crear imagen y verificar dimensiones
// ============================================================
void test_image_creation() {
    // Imagen vacía
    Image empty;
    assert(empty.width() == 0);
    assert(empty.height() == 0);
    assert(empty.empty());

    // Imagen con dimensiones
    Image img(10, 20);
    assert(img.width() == 10);
    assert(img.height() == 20);
    assert(!img.empty());

    // Imagen con relleno
    Pixel red(255, 0, 0);
    Image filled(5, 5, red);
    assert(filled.width() == 5);
    assert(filled.height() == 5);
    assert(filled.get(0, 0) == red);
    assert(filled.get(4, 4) == red);
}

// ============================================================
// Test 2: Leer y escribir píxeles
// ============================================================
void test_image_pixel_access() {
    Image img(3, 3);

    // Verificar que los píxeles por defecto son negros con alfa=255
    Pixel black(0, 0, 0, 255);
    assert(img.get(0, 0) == black);

    // Escribir y leer un píxel
    Pixel green(0, 255, 0);
    img.set(1, 1, green);
    assert(img.get(1, 1) == green);
    assert(img.get(0, 0) == black); // Los demás no cambian

    // Verificar que el acceso fuera de rango lanza excepción
    bool threw = false;
    try {
        img.get(3, 0); // x fuera de rango
    } catch (const std::out_of_range&) {
        threw = true;
    }
    assert(threw);

    threw = false;
    try {
        img.set(0, 3, green); // y fuera de rango
    } catch (const std::out_of_range&) {
        threw = true;
    }
    assert(threw);
}

// ============================================================
// Test 3: Extraer sub-regiones
// ============================================================
void test_image_subimage() {
    // Crear imagen 4×4 con patrón conocido
    Image img(4, 4);
    for (int y = 0; y < 4; ++y) {
        for (int x = 0; x < 4; ++x) {
            img.set(x, y, Pixel(static_cast<uint8_t>(x * 60),
                                static_cast<uint8_t>(y * 60), 0));
        }
    }

    // Extraer sub-región 2×2 desde (1,1)
    Image sub = img.subimage(1, 1, 2, 2);
    assert(sub.width() == 2);
    assert(sub.height() == 2);
    assert(sub.get(0, 0) == img.get(1, 1));
    assert(sub.get(1, 0) == img.get(2, 1));
    assert(sub.get(0, 1) == img.get(1, 2));
    assert(sub.get(1, 1) == img.get(2, 2));

    // Sub-región fuera de rango debe lanzar excepción
    bool threw = false;
    try {
        img.subimage(3, 3, 2, 2); // Excede los límites
    } catch (const std::out_of_range&) {
        threw = true;
    }
    assert(threw);
}

// ============================================================
// Test 4: Copiar imágenes (deep copy)
// ============================================================
void test_image_copy_semantics() {
    Pixel blue(0, 0, 255);
    Image original(3, 3, blue);

    // Copia mediante constructor
    Image copy(original);
    assert(copy.width() == 3);
    assert(copy.height() == 3);
    assert(copy.get(0, 0) == blue);

    // Modificar la copia no afecta al original (deep copy)
    Pixel red(255, 0, 0);
    copy.set(0, 0, red);
    assert(copy.get(0, 0) == red);
    assert(original.get(0, 0) == blue); // ¡El original no cambió!

    // Copia mediante operador de asignación
    Image assigned;
    assigned = original;
    assert(assigned.get(1, 1) == blue);
    assigned.set(1, 1, red);
    assert(original.get(1, 1) == blue); // Original intacto
}

// ============================================================
// Test 5: Mover imágenes (transferencia de propiedad)
// ============================================================
void test_image_move_semantics() {
    Pixel green(0, 255, 0);
    Image original(4, 4, green);

    // Movimiento mediante constructor
    Image moved(std::move(original));
    assert(moved.width() == 4);
    assert(moved.height() == 4);
    assert(moved.get(0, 0) == green);

    // El original queda vacío después del movimiento
    assert(original.empty());

    // Movimiento mediante operador de asignación
    Image target;
    target = std::move(moved);
    assert(target.width() == 4);
    assert(target.height() == 4);
    assert(moved.empty());
}

// ============================================================
// Test 6: Márgenes válidos producen 9 regiones correctas
// ============================================================
void test_slice_margins_valid() {
    // Crear imagen 10×10 con colores distintos por zona
    Image img(10, 10);
    Pixel corner(255, 0, 0);
    Pixel edge(0, 255, 0);
    Pixel center(0, 0, 255);

    for (int y = 0; y < 10; ++y) {
        for (int x = 0; x < 10; ++x) {
            bool is_top = y < 2, is_bottom = y >= 8;
            bool is_left = x < 2, is_right = x >= 8;

            if ((is_top || is_bottom) && (is_left || is_right))
                img.set(x, y, corner);
            else if (is_top || is_bottom || is_left || is_right)
                img.set(x, y, edge);
            else
                img.set(x, y, center);
        }
    }

    NineSliceScaler scaler(img, SliceMargins(2));
    assert(!scaler.is_sliced());
    scaler.slice();
    assert(scaler.is_sliced());

    const auto& r = scaler.regions();

    // Verificar dimensiones de las regiones
    assert(r.top_left.width() == 2 && r.top_left.height() == 2);
    assert(r.top_center.width() == 6 && r.top_center.height() == 2);
    assert(r.top_right.width() == 2 && r.top_right.height() == 2);
    assert(r.middle_left.width() == 2 && r.middle_left.height() == 6);
    assert(r.middle_center.width() == 6 && r.middle_center.height() == 6);
    assert(r.middle_right.width() == 2 && r.middle_right.height() == 6);
    assert(r.bottom_left.width() == 2 && r.bottom_left.height() == 2);
    assert(r.bottom_center.width() == 6 && r.bottom_center.height() == 2);
    assert(r.bottom_right.width() == 2 && r.bottom_right.height() == 2);

    // Verificar contenido: esquinas deben ser rojas
    assert(r.top_left.get(0, 0) == corner);
    assert(r.top_right.get(1, 1) == corner);
    assert(r.bottom_left.get(0, 0) == corner);
    assert(r.bottom_right.get(1, 1) == corner);

    // Bordes deben ser verdes
    assert(r.top_center.get(0, 0) == edge);
    assert(r.middle_left.get(0, 0) == edge);

    // Centro debe ser azul
    assert(r.middle_center.get(0, 0) == center);
}

// ============================================================
// Test 7: Márgenes que exceden dimensiones lanzan error
// ============================================================
void test_slice_margins_invalid() {
    Image img(6, 6);

    // Márgenes horizontales exceden el ancho
    NineSliceScaler scaler1(img, SliceMargins(1, 4, 1, 4));
    bool threw = false;
    try {
        scaler1.slice(); // left(4) + right(4) = 8 > 6
    } catch (const std::invalid_argument&) {
        threw = true;
    }
    assert(threw);

    // Márgenes verticales exceden la altura
    NineSliceScaler scaler2(img, SliceMargins(4, 1, 4, 1));
    threw = false;
    try {
        scaler2.slice(); // top(4) + bottom(4) = 8 > 6
    } catch (const std::invalid_argument&) {
        threw = true;
    }
    assert(threw);
}

// ============================================================
// Test 8: Renderizar a tamaño mayor que la fuente
// ============================================================
void test_render_larger() {
    Pixel fill(128, 128, 128);
    Image img(8, 8, fill);
    NineSliceScaler scaler(img, SliceMargins(2));
    scaler.slice();

    // Renderizar a 20×20 (mayor que 8×8)
    Image result = scaler.render(20, 20);
    assert(result.width() == 20);
    assert(result.height() == 20);

    // Todos los píxeles deben ser del mismo color (imagen uniforme)
    for (int y = 0; y < 20; ++y) {
        for (int x = 0; x < 20; ++x) {
            assert(result.get(x, y) == fill);
        }
    }
}

// ============================================================
// Test 9: Las esquinas mantienen su tamaño original
// ============================================================
void test_render_corners_preserved() {
    // Crear imagen con esquinas de color único
    Image img(10, 10, Pixel(0, 0, 0));
    Pixel corner_color(255, 0, 0);
    int margin = 3;

    // Pintar solo la esquina superior izquierda
    for (int y = 0; y < margin; ++y) {
        for (int x = 0; x < margin; ++x) {
            img.set(x, y, corner_color);
        }
    }

    NineSliceScaler scaler(img, SliceMargins(margin));
    scaler.slice();

    // Renderizar a 30×30
    Image result = scaler.render(30, 30);

    // La esquina superior izquierda debe mantener sus 3×3 píxeles rojos
    for (int y = 0; y < margin; ++y) {
        for (int x = 0; x < margin; ++x) {
            assert(result.get(x, y) == corner_color);
        }
    }

    // El píxel justo fuera de la esquina no debe ser rojo
    assert(result.get(margin, 0) != corner_color);
    assert(result.get(0, margin) != corner_color);
}

// ============================================================
// Test 10: Los bordes se estiran correctamente
// ============================================================
void test_render_edges_stretch() {
    // Crear imagen 8×8 con borde superior de color conocido
    Image img(8, 8, Pixel(0, 0, 0));
    Pixel edge_color(0, 200, 0);
    int margin = 2;

    // Pintar el borde superior central (entre las esquinas)
    for (int x = margin; x < 8 - margin; ++x) {
        for (int y = 0; y < margin; ++y) {
            img.set(x, y, edge_color);
        }
    }

    NineSliceScaler scaler(img, SliceMargins(margin));
    scaler.slice();

    // Renderizar a 20×20: el borde superior se estira de 4px a 16px de ancho
    Image result = scaler.render(20, 20);

    // Todo el borde superior (entre esquinas) debe ser verde
    for (int x = margin; x < 20 - margin; ++x) {
        for (int y = 0; y < margin; ++y) {
            assert(result.get(x, y) == edge_color);
        }
    }
}

// ============================================================
// Test 11: El escalado nearest-neighbor funciona
// ============================================================
void test_scale_region() {
    // Crear imagen 2×2 con patrón de tablero
    Image src(2, 2);
    Pixel white(255, 255, 255);
    Pixel black(0, 0, 0);
    src.set(0, 0, white);
    src.set(1, 0, black);
    src.set(0, 1, black);
    src.set(1, 1, white);

    // Escalar a 4×4 — cada píxel se duplica
    // Accedemos a scale_region a través del pipeline de render.
    // Para testear directamente, creamos un scaler y verificamos el render.
    Image full(4, 4);
    // Fila superior: white white black black
    // Fila 2:        white white black black
    // Fila 3:        black black white white
    // Fila 4:        black black white white

    // Usamos un scaler con márgenes 0 para que todo sea "centro"
    // y se escale completamente
    NineSliceScaler scaler(src, SliceMargins(0, 0, 0, 0));
    scaler.slice();
    Image scaled = scaler.render(4, 4);

    // Verificar el patrón de tablero escalado
    assert(scaled.get(0, 0) == white);
    assert(scaled.get(1, 0) == white);
    assert(scaled.get(2, 0) == black);
    assert(scaled.get(3, 0) == black);
    assert(scaled.get(0, 2) == black);
    assert(scaled.get(1, 2) == black);
    assert(scaled.get(2, 2) == white);
    assert(scaled.get(3, 2) == white);
}

// ============================================================
// Test 12: Pipeline completo: crear → rebanar → renderizar
// ============================================================
void test_full_pipeline() {
    // Simular un borde decorativo completo
    int src_size = 12;
    int margin = 3;
    Image border(src_size, src_size);

    Pixel tl(255, 0, 0), tr(0, 255, 0), bl(0, 0, 255), br(255, 255, 0);
    Pixel top_edge(200, 100, 100), bottom_edge(100, 100, 200);
    Pixel left_edge(100, 200, 100), right_edge(200, 200, 100);
    Pixel center(128, 128, 128);

    for (int y = 0; y < src_size; ++y) {
        for (int x = 0; x < src_size; ++x) {
            bool is_t = y < margin, is_b = y >= src_size - margin;
            bool is_l = x < margin, is_r = x >= src_size - margin;

            if (is_t && is_l) border.set(x, y, tl);
            else if (is_t && is_r) border.set(x, y, tr);
            else if (is_b && is_l) border.set(x, y, bl);
            else if (is_b && is_r) border.set(x, y, br);
            else if (is_t) border.set(x, y, top_edge);
            else if (is_b) border.set(x, y, bottom_edge);
            else if (is_l) border.set(x, y, left_edge);
            else if (is_r) border.set(x, y, right_edge);
            else border.set(x, y, center);
        }
    }

    // Crear scaler, dividir, renderizar
    NineSliceScaler scaler(border, SliceMargins(margin));
    scaler.slice();
    Image result = scaler.render(24, 18);

    assert(result.width() == 24);
    assert(result.height() == 18);

    // Verificar esquinas: deben mantener el color original
    assert(result.get(0, 0) == tl);
    assert(result.get(2, 2) == tl);    // Dentro de la esquina sup-izq
    assert(result.get(23, 0) == tr);
    assert(result.get(0, 17) == bl);
    assert(result.get(23, 17) == br);

    // Verificar borde superior (entre esquinas)
    assert(result.get(margin, 0) == top_edge);
    assert(result.get(12, 1) == top_edge);

    // Verificar centro
    assert(result.get(12, 9) == center);

    // Verificar que render sin slice() lanza error
    NineSliceScaler unsliced(border, SliceMargins(margin));
    bool threw = false;
    try {
        unsliced.render(20, 20);
    } catch (const std::logic_error&) {
        threw = true;
    }
    assert(threw);
}

// ============================================================
// MAIN — Ejecutar todos los tests
// ============================================================
int main() {
    std::cout << "╔══════════════════════════════════════════════════╗\n";
    std::cout << "║  Tests: Sub-módulo 6.1 — El Arquitecto de Bordes║\n";
    std::cout << "╚══════════════════════════════════════════════════╝\n\n";

    RUN_TEST(test_image_creation);
    RUN_TEST(test_image_pixel_access);
    RUN_TEST(test_image_subimage);
    RUN_TEST(test_image_copy_semantics);
    RUN_TEST(test_image_move_semantics);
    RUN_TEST(test_slice_margins_valid);
    RUN_TEST(test_slice_margins_invalid);
    RUN_TEST(test_render_larger);
    RUN_TEST(test_render_corners_preserved);
    RUN_TEST(test_render_edges_stretch);
    RUN_TEST(test_scale_region);
    RUN_TEST(test_full_pipeline);

    std::cout << "\n══════════════════════════════════════════════════\n";
    std::cout << "  Resultado: " << tests_passed << "/" << tests_total << " tests pasaron";
    if (tests_passed == tests_total) {
        std::cout << " ✓ ¡Todos correctos!\n";
    } else {
        std::cout << " ✗ Algunos tests fallaron.\n";
    }
    std::cout << "══════════════════════════════════════════════════\n";

    return (tests_passed == tests_total) ? 0 : 1;
}
