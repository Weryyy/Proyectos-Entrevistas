#ifndef NINE_SLICE_HPP
#define NINE_SLICE_HPP

#include <string>
#include <vector>
#include <stdexcept>
#include <iostream>
#include <cstdint>

// ============================================================
// nine_slice.hpp — Motor de 9-Slice Scaling
// Sub-módulo 6.1: El Arquitecto de Bordes
//
// Este archivo define las clases para implementar el escalado
// de imágenes mediante la técnica de 9 regiones (9-slice).
// ============================================================

// Representa un píxel RGBA simple
struct Pixel {
    uint8_t r, g, b, a;
    Pixel() : r(0), g(0), b(0), a(255) {}
    Pixel(uint8_t r, uint8_t g, uint8_t b, uint8_t a = 255)
        : r(r), g(g), b(b), a(a) {}
    bool operator==(const Pixel& other) const {
        return r == other.r && g == other.g && b == other.b && a == other.a;
    }
    bool operator!=(const Pixel& other) const { return !(*this == other); }
};

// Imagen simple en memoria (buffer de píxeles 2D)
class Image {
private:
    std::vector<Pixel> data_;
    int width_;
    int height_;

public:
    Image();
    Image(int width, int height);
    Image(int width, int height, Pixel fill);
    ~Image();

    // Semántica de copia y movimiento
    Image(const Image& other);
    Image(Image&& other) noexcept;
    Image& operator=(const Image& other);
    Image& operator=(Image&& other) noexcept;

    int width() const;
    int height() const;
    bool empty() const;

    Pixel get(int x, int y) const;
    void set(int x, int y, Pixel pixel);

    // Extraer una sub-región rectangular de la imagen
    Image subimage(int x, int y, int w, int h) const;

    // Imprimir como arte ASCII (para depuración/visualización)
    void print_ascii() const;
};

// Define los márgenes para el recorte de 9 regiones
struct SliceMargins {
    int top;
    int right;
    int bottom;
    int left;

    SliceMargins(int top, int right, int bottom, int left)
        : top(top), right(right), bottom(bottom), left(left) {}
    SliceMargins(int all) : top(all), right(all), bottom(all), left(all) {}
};

// Las 9 regiones extraídas de una imagen
struct NineSliceRegions {
    Image top_left, top_center, top_right;
    Image middle_left, middle_center, middle_right;
    Image bottom_left, bottom_center, bottom_right;
};

// Motor principal de 9-slice scaling
class NineSliceScaler {
private:
    Image source_;
    SliceMargins margins_;
    NineSliceRegions regions_;
    bool sliced_;

    // Escalar una región al tamaño objetivo usando muestreo nearest-neighbor
    static Image scale_region(const Image& src, int target_width, int target_height);

    // Copiar una imagen fuente sobre un destino en la posición indicada
    static void blit(Image& dest, const Image& src, int dest_x, int dest_y);

public:
    NineSliceScaler(const Image& source, SliceMargins margins);
    ~NineSliceScaler();

    // Realizar el corte (extraer 9 regiones de la imagen fuente)
    void slice();

    // Renderizar el borde al tamaño total dado (dimensiones de ventana)
    Image render(int target_width, int target_height) const;

    // Obtener las regiones individuales (para inspección/testing)
    const NineSliceRegions& regions() const;

    bool is_sliced() const;
};

#endif // NINE_SLICE_HPP
