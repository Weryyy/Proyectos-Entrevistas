"""
test_qml_structure.py — Validación Estructural de Archivos QML
Sub-módulo 6.3: Pergaminos Digitales (Quickshell & QML)

Dado que Quickshell requiere una sesión Wayland activa para renderizar widgets,
este script valida la ESTRUCTURA de los archivos QML usando análisis estático:
- Existencia y contenido de los archivos
- Presencia de elementos QML requeridos (import, elementos raíz, propiedades)
- Balanceo correcto de llaves {} y comillas
- Patrones sintácticos válidos mediante expresiones regulares
"""

import os
import re
import pytest

# =============================================================================
# Configuración: rutas a los archivos QML que vamos a validar
# =============================================================================

# Obtenemos el directorio donde está este archivo de tests
DIRECTORIO_QML = os.path.dirname(os.path.abspath(__file__))

# Lista de archivos QML esperados en este sub-módulo
ARCHIVOS_QML = [
    os.path.join(DIRECTORIO_QML, "ScrollWidget.qml"),
    os.path.join(DIRECTORIO_QML, "StatusBar.qml"),
]


def leer_archivo(ruta):
    """Lee y retorna el contenido completo de un archivo."""
    with open(ruta, "r", encoding="utf-8") as f:
        return f.read()


# =============================================================================
# Tests de existencia y contenido básico
# =============================================================================


class TestExistenciaArchivos:
    """Verifica que los archivos QML existen y no están vacíos."""

    @pytest.mark.parametrize("ruta", ARCHIVOS_QML)
    def test_archivo_existe(self, ruta):
        """Cada archivo QML debe existir en el directorio del sub-módulo."""
        assert os.path.isfile(ruta), f"No se encontró el archivo: {ruta}"

    @pytest.mark.parametrize("ruta", ARCHIVOS_QML)
    def test_archivo_no_vacio(self, ruta):
        """Cada archivo QML debe tener contenido (no estar vacío)."""
        contenido = leer_archivo(ruta)
        assert len(contenido.strip()) > 0, f"El archivo está vacío: {ruta}"

    @pytest.mark.parametrize("ruta", ARCHIVOS_QML)
    def test_archivo_tiene_longitud_minima(self, ruta):
        """Los archivos QML deben tener al menos 500 caracteres de contenido."""
        contenido = leer_archivo(ruta)
        assert len(contenido) >= 500, (
            f"El archivo es demasiado corto ({len(contenido)} chars): {ruta}"
        )


# =============================================================================
# Tests de elementos QML requeridos
# =============================================================================


class TestElementosQML:
    """Verifica la presencia de elementos fundamentales de QML."""

    @pytest.mark.parametrize("ruta", ARCHIVOS_QML)
    def test_tiene_import_qtquick(self, ruta):
        """Todo archivo QML debe importar QtQuick, el módulo base."""
        contenido = leer_archivo(ruta)
        # Buscamos 'import QtQuick' seguido de una versión (2.x o sin versión)
        patron = r"import\s+QtQuick\s+\d+\.\d+"
        assert re.search(patron, contenido), (
            f"Falta 'import QtQuick X.X' en: {ruta}"
        )

    @pytest.mark.parametrize("ruta", ARCHIVOS_QML)
    def test_tiene_elemento_raiz(self, ruta):
        """Debe existir un elemento raíz (Rectangle o Item) en el nivel superior."""
        contenido = leer_archivo(ruta)
        # El elemento raíz suele ser Rectangle o Item seguido de '{'
        patron = r"^(Rectangle|Item)\s*\{" 
        assert re.search(patron, contenido, re.MULTILINE), (
            f"No se encontró elemento raíz (Rectangle/Item) en: {ruta}"
        )

    @pytest.mark.parametrize("ruta", ARCHIVOS_QML)
    def test_tiene_declaracion_de_propiedad(self, ruta):
        """Los widgets deben declarar al menos una propiedad personalizada."""
        contenido = leer_archivo(ruta)
        # En QML las propiedades se declaran con 'property <tipo> <nombre>'
        patron = r"property\s+(real|string|int|bool|var|color)\s+\w+"
        assert re.search(patron, contenido), (
            f"No se encontró declaración 'property' en: {ruta}"
        )

    def test_scroll_widget_tiene_mousearea(self):
        """ScrollWidget debe incluir MouseArea para el efecto parallax."""
        ruta = os.path.join(DIRECTORIO_QML, "ScrollWidget.qml")
        contenido = leer_archivo(ruta)
        assert "MouseArea" in contenido, (
            "ScrollWidget.qml debe contener MouseArea para el parallax"
        )

    def test_status_bar_tiene_layout(self):
        """StatusBar debe usar algún tipo de layout (Row, RowLayout, etc.)."""
        ruta = os.path.join(DIRECTORIO_QML, "StatusBar.qml")
        contenido = leer_archivo(ruta)
        tiene_layout = ("RowLayout" in contenido or
                        "Row" in contenido or
                        "ColumnLayout" in contenido)
        assert tiene_layout, (
            "StatusBar.qml debe contener un layout (Row/RowLayout)"
        )


# =============================================================================
# Tests de estructura sintáctica
# =============================================================================


class TestEstructuraSintactica:
    """Valida la estructura sintáctica básica de los archivos QML."""

    @pytest.mark.parametrize("ruta", ARCHIVOS_QML)
    def test_llaves_balanceadas(self, ruta):
        """Las llaves de apertura y cierre deben estar balanceadas."""
        contenido = leer_archivo(ruta)
        # Eliminamos los comentarios de línea para no contar llaves en comentarios
        lineas = contenido.split("\n")
        contenido_limpio = ""
        for linea in lineas:
            # Removemos comentarios de línea (//)
            idx_comentario = linea.find("//")
            if idx_comentario >= 0:
                linea = linea[:idx_comentario]
            contenido_limpio += linea + "\n"

        # Eliminamos strings para no contar llaves dentro de cadenas de texto
        contenido_limpio = re.sub(r'"[^"]*"', '""', contenido_limpio)

        aperturas = contenido_limpio.count("{")
        cierres = contenido_limpio.count("}")
        assert aperturas == cierres, (
            f"Llaves desbalanceadas en {ruta}: "
            f"{aperturas} aperturas vs {cierres} cierres"
        )

    @pytest.mark.parametrize("ruta", ARCHIVOS_QML)
    def test_sin_llaves_vacias_sospechosas(self, ruta):
        """No debería haber elementos completamente vacíos como 'Rectangle {}'."""
        contenido = leer_archivo(ruta)
        # Un elemento vacío sería algo como 'Tipo { }' sin nada dentro
        # Esto generalmente indica un error (se olvidó el contenido)
        patron = r"(Rectangle|Item|Text|MouseArea|Row|Column)\s*\{\s*\}"
        coincidencias = re.findall(patron, contenido)
        assert len(coincidencias) == 0, (
            f"Se encontraron elementos vacíos sospechosos en {ruta}: {coincidencias}"
        )

    @pytest.mark.parametrize("ruta", ARCHIVOS_QML)
    def test_tiene_animaciones(self, ruta):
        """Los widgets deben incluir algún tipo de animación QML."""
        contenido = leer_archivo(ruta)
        tiene_animacion = (
            "NumberAnimation" in contenido or
            "Behavior" in contenido or
            "SequentialAnimation" in contenido or
            "ParallelAnimation" in contenido or
            "PropertyAnimation" in contenido
        )
        assert tiene_animacion, (
            f"No se encontró ninguna animación en: {ruta}"
        )


# =============================================================================
# Punto de entrada para ejecución directa
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
