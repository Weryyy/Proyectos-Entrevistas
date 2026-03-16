// =============================================================================
// StatusBar.qml — Barra de Estado con Temática de Fantasía
// Sub-módulo 6.3: Pergaminos Digitales (Quickshell & QML)
// =============================================================================
// Una barra de estado estilizada como elemento de RPG/fantasía medieval.
// Demuestra Row layouts, animaciones de opacidad/escala, y estilizado temático.
// =============================================================================

import QtQuick 2.15
import QtQuick.Layouts 1.15       // Para RowLayout y otros layouts

// --- Elemento raíz: la barra de estado completa ---
Rectangle {
    id: barraEstado
    width: 800                      // Ancho típico de una barra superior
    height: 48                      // Altura compacta
    color: "#1a0f0a"                // Fondo oscuro como madera quemada
    border.color: "#c9a84c"         // Borde dorado como ornamento medieval
    border.width: 2
    radius: 4

    // Propiedad para controlar la opacidad global de los elementos
    property real elementosOpacidad: 1.0

    // --- Layout principal: distribuye los elementos horizontalmente ---
    // RowLayout organiza sus hijos en una fila con espaciado automático.
    RowLayout {
        anchors.fill: parent
        anchors.margins: 8          // Margen interno
        spacing: 20                 // Espacio entre cada módulo

        // === MÓDULO 1: Reloj con estilo rúnico ===
        // Simula un reloj con tipografía de fantasía
        Rectangle {
            id: moduloReloj
            Layout.preferredWidth: 120
            Layout.fillHeight: true
            color: "transparent"

            Text {
                id: textoReloj
                // En un entorno real, usaríamos Date() de JavaScript para la hora
                text: "⏰ XII:XXX"
                font.family: "Serif"
                font.pixelSize: 18
                font.bold: true
                color: "#e8c547"     // Dorado brillante para el reloj
                anchors.centerIn: parent

                // --- Animación de escala al iniciar ---
                // SequentialAnimation ejecuta animaciones en secuencia.
                // Aquí hacemos un efecto de "aparición" al cargar el widget.
                SequentialAnimation on scale {
                    running: true     // Se ejecuta automáticamente al crear
                    NumberAnimation { from: 0.0; to: 1.1; duration: 300 }
                    NumberAnimation { from: 1.1; to: 1.0; duration: 150 }
                }
            }
        }

        // === MÓDULO 2: Indicador de espacios de trabajo (workspaces) ===
        // Muestra los escritorios virtuales como iconos de escudo
        Rectangle {
            id: moduloWorkspaces
            Layout.preferredWidth: 200
            Layout.fillHeight: true
            color: "transparent"

            Row {
                anchors.centerIn: parent
                spacing: 12

                // --- Repetidor: crea múltiples elementos desde un modelo ---
                // Repeater genera N copias de su delegado (el Rectangle interno).
                // Aquí creamos 5 indicadores de workspace.
                Repeater {
                    model: 5          // 5 escritorios virtuales

                    Rectangle {
                        width: 24
                        height: 24
                        radius: 12    // Círculo perfecto (radio = mitad del lado)
                        // El primer workspace está "activo" (dorado), los demás apagados
                        color: index === 0 ? "#c9a84c" : "#3d2b1f"
                        border.color: "#8b7332"
                        border.width: 1

                        Text {
                            text: (index + 1).toString()
                            font.pixelSize: 12
                            color: index === 0 ? "#1a0f0a" : "#8b7332"
                            anchors.centerIn: parent
                        }

                        // Animación suave de opacidad
                        opacity: index === 0 ? 1.0 : 0.6
                        Behavior on opacity {
                            NumberAnimation { duration: 250 }
                        }
                    }
                }
            }
        }

        // === MÓDULO 3: Estadísticas del sistema ===
        // CPU, memoria, etc. estilizados como barras de vida de RPG
        Rectangle {
            id: moduloStats
            Layout.fillWidth: true    // Ocupa el espacio restante
            Layout.fillHeight: true
            color: "transparent"

            Row {
                anchors.centerIn: parent
                spacing: 16

                // --- Barra de CPU (como barra de vida) ---
                Column {
                    Text {
                        text: "⚔️ CPU"
                        font.pixelSize: 11
                        color: "#a08050"
                    }
                    Rectangle {
                        width: 80; height: 8
                        color: "#2a1a10"
                        radius: 4
                        Rectangle {
                            width: parent.width * 0.45  // 45% de uso simulado
                            height: parent.height
                            color: "#4CAF50"            // Verde = saludable
                            radius: 4
                        }
                    }
                }

                // --- Barra de Memoria (como barra de maná) ---
                Column {
                    Text {
                        text: "🛡️ MEM"
                        font.pixelSize: 11
                        color: "#a08050"
                    }
                    Rectangle {
                        width: 80; height: 8
                        color: "#2a1a10"
                        radius: 4
                        Rectangle {
                            width: parent.width * 0.62  // 62% de uso simulado
                            height: parent.height
                            color: "#2196F3"            // Azul = maná/memoria
                            radius: 4
                        }
                    }
                }
            }
        }
    }
}
