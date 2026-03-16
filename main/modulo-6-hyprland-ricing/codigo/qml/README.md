# Sub-módulo 6.3: Pergaminos Digitales — Quickshell & QML

## ¿Qué es QML?

**QML** (Qt Markup Language) es un lenguaje **declarativo** de interfaces de usuario
desarrollado por The Qt Company. A diferencia de los lenguajes imperativos donde
describes *cómo* construir la interfaz paso a paso, en QML describes *qué* quieres
que aparezca y el framework se encarga del resto.

```qml
// Ejemplo básico: un rectángulo con texto
Rectangle {
    width: 200; height: 100
    color: "#2d1b00"
    Text {
        text: "¡Hola, aventurero!"
        anchors.centerIn: parent
    }
}
```

### Características principales de QML:
- **Declarativo**: defines la estructura visual como un árbol de objetos
- **Reactivo**: las propiedades se enlazan automáticamente (property bindings)
- **Animaciones nativas**: transiciones fluidas integradas en el lenguaje
- **JavaScript embebido**: lógica dinámica dentro de los componentes
- **Extensible con C++/Python**: backends potentes para lógica compleja

## ¿Qué es Quickshell?

**Quickshell** es un shell basado en **Qt6** diseñado para compositores Wayland
(como Hyprland). Es una alternativa moderna a herramientas como:

| Herramienta | Lenguaje       | Paradigma    |
|-------------|----------------|--------------|
| **eww**     | Yuck (Lisp)    | Declarativo  |
| **AGS**     | JavaScript/TS  | Imperativo   |
| **Quickshell** | **QML**     | **Declarativo** |

### Ventajas de Quickshell:
- Aprovecha todo el ecosistema Qt6 (gráficos, animaciones, multimedia)
- QML permite crear interfaces complejas con menos código
- Soporte nativo para efectos gráficos avanzados (shaders, partículas)
- Integración directa con el protocolo Wayland

## Efecto Parallax en Widgets

El **efecto parallax** crea profundidad visual moviendo capas a diferentes
velocidades según la posición del cursor. En QML esto se logra con:

1. **MouseArea** para capturar la posición del cursor
2. **Property bindings** que calculan el desplazamiento de cada capa
3. **Behavior** para suavizar las transiciones

```qml
// Parallax simplificado
Rectangle {
    // La capa de fondo se mueve lentamente
    x: mouseArea.mouseX * 0.02
    Behavior on x { NumberAnimation { duration: 200 } }
}
```

## El Enfoque de zacoons

El usuario **zacoons** en r/unixporn utilizó Quickshell para crear widgets con
temática de fantasía medieval, incluyendo:

- **Pergaminos interactivos** que reaccionan al movimiento del mouse
- **Barras de estado** estilizadas como elementos de RPG
- **Efectos de partículas** simulando polvo y magia
- **Animaciones fluidas** para transiciones entre escritorios virtuales

## Archivos en este directorio

| Archivo | Descripción |
|---------|-------------|
| `ScrollWidget.qml` | Widget de pergamino interactivo con efecto parallax |
| `StatusBar.qml` | Barra de estado con temática de fantasía |
| `test_qml_structure.py` | Validación estructural de los archivos QML |

## ⚠️ Nota importante

Los archivos QML aquí son **demos estructurales**. Quickshell requiere una
sesión Wayland activa con un compositor compatible (como Hyprland) para
ejecutarse. En entornos CI/CD o sin servidor gráfico, solo podemos validar
la estructura sintáctica de los archivos, no renderizarlos.

Para ejecutar estos widgets necesitarías:
1. Un sistema Linux con Wayland
2. Hyprland (u otro compositor compatible)
3. Quickshell instalado (`pacman -S quickshell` en Arch)
4. Iniciar con: `quickshell -p ./ScrollWidget.qml`
