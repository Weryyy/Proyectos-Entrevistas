// =============================================================================
// ScrollWidget.qml — Pergamino Digital Interactivo
// Sub-módulo 6.3: Pergaminos Digitales (Quickshell & QML)
// =============================================================================
// Este archivo demuestra un widget de pergamino/scroll con efecto parallax.
// QML es un lenguaje DECLARATIVO: describimos QUÉ queremos ver, no CÓMO dibujarlo.
// Cada elemento se anida dentro de otro formando un árbol visual.
// =============================================================================

import QtQuick 2.15          // Módulo base de QML para elementos visuales
import QtQuick.Controls 2.15 // Controles de interfaz (botones, texto, etc.)

// --- Elemento raíz: el pergamino completo ---
// Rectangle es el bloque fundamental de construcción en QML.
// Todas las propiedades (width, height, color) son "bindings" reactivos:
// si cambian, la interfaz se actualiza automáticamente.
Rectangle {
    id: pergamino                    // Identificador único para referenciar este elemento
    width: 400                       // Ancho del pergamino en píxeles
    height: 600                      // Alto del pergamino
    color: "#f4e4c1"                 // Color base: tono pergamino/papiro antiguo
    radius: 8                        // Esquinas ligeramente redondeadas
    border.color: "#8b6914"          // Borde dorado oscuro, como un marco medieval
    border.width: 3

    // --- Propiedades personalizadas ---
    // En QML podemos declarar propiedades con tipos específicos.
    // Estas propiedades son reactivas: cualquier binding que las use
    // se recalcula automáticamente cuando cambian.
    property real parallaxX: 0.0     // Desplazamiento horizontal del parallax
    property real parallaxY: 0.0     // Desplazamiento vertical del parallax
    property string estadoActual: "Reposo"  // Estado actual del pergamino

    // --- Capa de fondo con efecto parallax ---
    // Esta capa se mueve LENTAMENTE siguiendo el cursor, creando
    // la ilusión de profundidad (efecto parallax).
    Rectangle {
        id: fondoParallax
        anchors.fill: parent         // Ocupa todo el espacio del padre
        color: "#e8d5a3"             // Tono ligeramente más oscuro
        opacity: 0.6                 // Semi-transparente para efecto de capas

        // El desplazamiento se calcula desde las propiedades parallax del padre.
        // El factor 0.3 hace que esta capa se mueva MÁS LENTO que el cursor,
        // creando la sensación de estar "más lejos" (parallax).
        x: pergamino.parallaxX * 0.3
        y: pergamino.parallaxY * 0.3

        // --- Behavior: animación implícita ---
        // Cuando 'x' o 'y' cambian, en vez de saltar al nuevo valor,
        // se animan suavemente durante 200ms con curva easeOutQuad.
        Behavior on x {
            NumberAnimation { duration: 200; easing.type: Easing.OutQuad }
        }
        Behavior on y {
            NumberAnimation { duration: 200; easing.type: Easing.OutQuad }
        }
    }

    // --- Título del pergamino ---
    Text {
        id: tituloPergamino
        text: "📜 Pergamino del Aventurero"
        font.family: "Serif"         // Fuente con serifa para estilo medieval
        font.pixelSize: 22
        font.bold: true
        color: "#4a3000"             // Marrón oscuro, como tinta antigua
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top: parent.top
        anchors.topMargin: 20

        // Esta capa de texto se mueve con factor 0.5 (velocidad media)
        // para crear un efecto parallax de profundidad intermedia.
        x: pergamino.parallaxX * 0.5

        Behavior on x {
            NumberAnimation { duration: 150; easing.type: Easing.OutCubic }
        }
    }

    // --- Indicador de estado ---
    // Muestra información sobre la posición del cursor y el estado actual.
    Text {
        id: infoEstado
        text: "Estado: " + pergamino.estadoActual +
              "\nParallax X: " + pergamino.parallaxX.toFixed(1) +
              "\nParallax Y: " + pergamino.parallaxY.toFixed(1)
        font.pixelSize: 14
        color: "#6b4c12"
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 15
        anchors.horizontalCenter: parent.horizontalCenter
        horizontalAlignment: Text.AlignHCenter

        // Animación de opacidad para aparición suave
        opacity: mouseDetector.containsMouse ? 1.0 : 0.4
        Behavior on opacity {
            NumberAnimation { duration: 300 }
        }
    }

    // --- Área de detección del mouse ---
    // MouseArea captura todos los eventos del cursor dentro del pergamino.
    // hoverEnabled permite detectar movimiento sin necesidad de click.
    MouseArea {
        id: mouseDetector
        anchors.fill: parent         // Cubre todo el pergamino
        hoverEnabled: true           // Detecta movimiento sin click

        // --- onPositionChanged ---
        // Se ejecuta cada vez que el cursor se mueve dentro del área.
        // Calculamos el desplazamiento parallax relativo al CENTRO del widget.
        onPositionChanged: {
            // mouse.x y mouse.y dan la posición actual del cursor
            // Restamos la mitad del ancho/alto para centrar el efecto
            pergamino.parallaxX = (mouse.x - pergamino.width / 2) * 0.1
            pergamino.parallaxY = (mouse.y - pergamino.height / 2) * 0.1
            pergamino.estadoActual = "Siguiendo cursor"
        }

        // Cuando el cursor sale del área, volvemos al estado de reposo
        onExited: {
            pergamino.parallaxX = 0
            pergamino.parallaxY = 0
            pergamino.estadoActual = "Reposo"
        }
    }
}
