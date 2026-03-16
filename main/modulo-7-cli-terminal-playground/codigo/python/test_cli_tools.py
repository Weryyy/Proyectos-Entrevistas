#!/usr/bin/env python3
"""
Tests para los retos del Terminal Playground (Módulo 7).

Ejecutar con: pytest test_cli_tools.py -v
"""
import json
import os
import sys

import pytest

# ──────────────────────────────────────────────
# Configurar el path para importar los módulos del proyecto
# ──────────────────────────────────────────────
_CODIGO_DIR = os.path.dirname(os.path.abspath(__file__))
if _CODIGO_DIR not in sys.path:
    sys.path.insert(0, _CODIGO_DIR)

_DATOS_DIR = os.path.join(_CODIGO_DIR, "..", "..", "datos")

import fortune_cowsay  # noqa: E402
import typo_punisher   # noqa: E402
import neofetch_clone   # noqa: E402
import bonsai_generator  # noqa: E402


# ══════════════════════════════════════════════
# Tests para fortune_cowsay (Reto 1)
# ══════════════════════════════════════════════
class TestFortuneCowsay:
    """Tests del Oráculo y el Mensajero."""

    def test_fortune_returns_string(self):
        """fortune() devuelve una cadena no vacía."""
        resultado = fortune_cowsay.fortune()
        assert isinstance(resultado, str)
        assert len(resultado) > 0

    def test_fortune_has_autor(self):
        """fortune() incluye texto y autor (separado por —)."""
        resultado = fortune_cowsay.fortune()
        assert "—" in resultado

    def test_cowsay_basic(self):
        """cowsay() genera arte ASCII con el mensaje."""
        resultado = fortune_cowsay.cowsay("Hola mundo")
        assert "Hola mundo" in resultado
        # Debe contener bordes de la burbuja
        assert "_" in resultado
        assert "-" in resultado

    def test_cowsay_wraps_long_text(self):
        """cowsay() envuelve texto largo correctamente."""
        texto_largo = "Esta es una frase muy larga que debería ser envuelta " \
                      "automáticamente por la función cowsay para que quepa " \
                      "dentro de la burbuja de diálogo del personaje."
        resultado = fortune_cowsay.cowsay(texto_largo)
        # Debe contener la burbuja completa
        assert "_" in resultado
        assert "-" in resultado

    def test_cowsay_characters(self):
        """Diferentes personajes generan arte diferente."""
        vaca = fortune_cowsay.cowsay("test", character="cow")
        dragon = fortune_cowsay.cowsay("test", character="dragon")
        wizard = fortune_cowsay.cowsay("test", character="wizard")

        # Los tres deben contener el mensaje
        for resultado in [vaca, dragon, wizard]:
            assert "test" in resultado

        # Pero el arte del personaje debe ser diferente
        # (extraemos solo la parte después de la burbuja)
        arte_vaca = vaca.split("---")[-1]
        arte_dragon = dragon.split("---")[-1]
        assert arte_vaca != arte_dragon

    def test_frases_json_valid(self):
        """El archivo frases.json es JSON válido con estructura correcta."""
        ruta_frases = os.path.join(_DATOS_DIR, "frases.json")
        assert os.path.exists(ruta_frases), f"No existe {ruta_frases}"

        with open(ruta_frases, "r", encoding="utf-8") as f:
            datos = json.load(f)

        assert "frases" in datos
        assert len(datos["frases"]) >= 15  # Al menos 15 frases
        for frase in datos["frases"]:
            assert "texto" in frase
            assert "autor" in frase
            assert len(frase["texto"]) > 0
            assert len(frase["autor"]) > 0

    def test_speech_bubble_contains_message(self):
        """La burbuja de diálogo contiene el mensaje original."""
        mensaje = "Recursión: ver recursión"
        burbuja = fortune_cowsay._construir_burbuja(mensaje)
        assert "Recursión" in burbuja
        assert "recursión" in burbuja


# ══════════════════════════════════════════════
# Tests para typo_punisher (Reto 2)
# ══════════════════════════════════════════════
class TestTypoPunisher:
    """Tests del Castigador de Typos."""

    def test_locomotive_frames_exist(self):
        """Existen al menos 2 frames de animación."""
        assert len(typo_punisher.FRAMES_LOCOMOTORA) >= 2

    def test_frames_are_consistent_height(self):
        """Todos los frames tienen la misma altura."""
        alturas = [len(frame) for frame in typo_punisher.FRAMES_LOCOMOTORA]
        assert len(set(alturas)) == 1, \
            f"Los frames tienen alturas diferentes: {alturas}"

    def test_smoke_generation(self):
        """La función de humo genera caracteres válidos."""
        humo = typo_punisher.generar_humo()
        assert isinstance(humo, list)
        assert len(humo) > 0
        # Cada línea de humo debe ser una cadena
        for linea in humo:
            assert isinstance(linea, str)

    def test_terminal_size_returns_tuple(self):
        """get_terminal_size() retorna dimensiones válidas."""
        size = typo_punisher.get_terminal_size()
        assert len(size) == 2
        assert size[0] > 0  # columnas
        assert size[1] > 0  # filas


# ══════════════════════════════════════════════
# Tests para neofetch_clone (Reto 3)
# ══════════════════════════════════════════════
class TestNeofetchClone:
    """Tests del Dashboard de Identidad."""

    def test_get_system_info_returns_dict(self):
        """get_system_info() devuelve un diccionario."""
        info = neofetch_clone.get_system_info()
        assert isinstance(info, dict)

    def test_system_info_has_required_keys(self):
        """La info del sistema contiene las claves requeridas."""
        info = neofetch_clone.get_system_info()
        claves_requeridas = ["os", "kernel", "uptime", "shell",
                             "cpu", "memory", "hostname", "user"]
        for clave in claves_requeridas:
            assert clave in info, f"Falta la clave '{clave}'"

    def test_ascii_logos_exist(self):
        """Existen los logos ASCII definidos."""
        assert "arch" in neofetch_clone.ASCII_LOGOS
        assert "python" in neofetch_clone.ASCII_LOGOS
        assert "default" in neofetch_clone.ASCII_LOGOS
        # Cada logo debe tener color y líneas
        for nombre, (color, lineas) in neofetch_clone.ASCII_LOGOS.items():
            assert isinstance(lineas, list), f"Logo '{nombre}' sin líneas"
            assert len(lineas) > 0, f"Logo '{nombre}' está vacío"

    def test_render_dashboard_produces_output(self):
        """render_dashboard() genera salida no vacía."""
        info = neofetch_clone.get_system_info()
        resultado = neofetch_clone.render_dashboard(info)
        assert isinstance(resultado, str)
        assert len(resultado) > 0

    def test_color_bar_output(self):
        """color_bar() genera salida con códigos ANSI."""
        barra = neofetch_clone.color_bar()
        assert isinstance(barra, str)
        assert len(barra) > 0
        # Debe contener códigos ANSI de escape
        assert "\033[" in barra

    def test_render_dashboard_contains_info(self):
        """render_dashboard() incluye la información del sistema."""
        info = neofetch_clone.get_system_info()
        resultado = neofetch_clone.render_dashboard(info)
        # Debe contener etiquetas del sistema
        assert "OS" in resultado or "Kernel" in resultado


# ══════════════════════════════════════════════
# Tests para bonsai_generator (Reto 4)
# ══════════════════════════════════════════════
class TestBonsaiGenerator:
    """Tests del Generador de Vida."""

    def test_tree_creation(self):
        """BonsaiTree se crea con dimensiones correctas."""
        arbol = bonsai_generator.BonsaiTree(60, 20)
        assert arbol.width == 60
        assert arbol.height == 20
        assert len(arbol.grid) == 20
        assert len(arbol.grid[0]) == 60

    def test_grow_places_characters(self):
        """grow() coloca caracteres en la cuadrícula."""
        arbol = bonsai_generator.BonsaiTree(40, 20)
        arbol.grow(20, 18, "up", 8)

        # Después de crecer, debe haber caracteres no vacíos en la cuadrícula
        caracteres_colocados = 0
        for fila in arbol.grid:
            for char, tipo in fila:
                if tipo != "vacio":
                    caracteres_colocados += 1

        assert caracteres_colocados > 0, "grow() no colocó ningún carácter"

    def test_render_produces_string(self):
        """render() genera una cadena no vacía."""
        arbol = bonsai_generator.BonsaiTree(40, 15)
        arbol.grow(20, 13, "up", 6)
        resultado = arbol.render()
        assert isinstance(resultado, str)
        assert len(resultado) > 0

    def test_pot_is_drawn(self):
        """El macetero se dibuja en la parte inferior."""
        arbol = bonsai_generator.BonsaiTree(40, 15)
        arbol.add_pot()

        # Buscar caracteres del macetero en las últimas filas
        tiene_maceta = False
        for fila in arbol.grid[-3:]:
            for char, tipo in fila:
                if tipo == "maceta":
                    tiene_maceta = True
                    break
            if tiene_maceta:
                break

        assert tiene_maceta, "No se encontró el macetero en la parte inferior"

    def test_tree_stays_in_bounds(self):
        """El árbol no se sale de los límites de la cuadrícula."""
        arbol = bonsai_generator.BonsaiTree(40, 20)
        arbol.grow(20, 18, "up", 15)
        arbol.add_leaves()

        # Si llegamos aquí sin IndexError, el árbol está en los límites.
        # Verificar que la cuadrícula mantiene sus dimensiones.
        assert len(arbol.grid) == 20
        for fila in arbol.grid:
            assert len(fila) == 40

    def test_crear_bonsai_completo(self):
        """crear_bonsai() genera un árbol completo con hojas y maceta."""
        arbol = bonsai_generator.crear_bonsai(50, 18)

        tipos_presentes = set()
        for fila in arbol.grid:
            for _, tipo in fila:
                if tipo != "vacio":
                    tipos_presentes.add(tipo)

        # Debe tener al menos tronco y maceta
        assert "tronco" in tipos_presentes or "rama" in tipos_presentes, \
            f"Tipos encontrados: {tipos_presentes}"
        assert "maceta" in tipos_presentes, \
            f"Tipos encontrados: {tipos_presentes}"

    def test_add_leaves_creates_foliage(self):
        """add_leaves() añade hojas cerca de las puntas."""
        arbol = bonsai_generator.BonsaiTree(50, 20)
        arbol.grow(25, 18, "up", 10)

        # Debe haber puntas de ramas registradas
        assert len(arbol.puntas_ramas) > 0

        arbol.add_leaves()

        # Verificar que se añadieron hojas
        hojas = 0
        for fila in arbol.grid:
            for _, tipo in fila:
                if tipo in ("hoja", "hoja_alt", "flor"):
                    hojas += 1

        assert hojas > 0, "add_leaves() no añadió ninguna hoja"
