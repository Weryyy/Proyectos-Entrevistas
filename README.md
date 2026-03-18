# 🏆 The Anthropic Gauntlet — Proyectos de Entrevistas Técnicas

Repositorio de aprendizaje inspirado en el proceso de entrevistas técnicas de Anthropic,
basado en [este video](https://www.youtube.com/watch?v=yeuJ4hSmT3s).

**Objetivo:** Dominar conceptos de entrevistas técnicas de alto nivel a través de proyectos
prácticos y divertidos. Cada módulo aborda un tema clave que aparece frecuentemente en
entrevistas de empresas de tecnología de primer nivel.

---

## 📚 Módulos

| #   | Módulo                                            | Concepto                  | Lenguaje             |
| --- | ------------------------------------------------- | ------------------------- | -------------------- |
| 1   | **El Corazón del Rendimiento** (LRU Cache)        | Estructuras de datos       | Python               |
| 2   | **Orquestador de Misiones** (DAG & Task Manager)  | Grafos y planificación     | Python               |
| 3   | **El Rastreador Cortés** (Web Crawler)             | Concurrencia y redes       | JavaScript (Node.js) |
| 4   | **Simulador de Inferencia de LLM**                | Sistemas y optimización    | Python               |
| 5   | **El Detective de Código** (Sampling Profiler)     | Sistemas de bajo nivel     | C                    |
| 6   | **El Artesano del Escritorio** (Hyprland Ricing)   | Linux, Wayland, plugins    | C++ / Bash / QML / Python |
| 7   | **The Terminal Playground** (CLI Tools)             | Piping, streams, animación | Python               |
| 8   | **El Guardián de Tráfico** (Rate Limiter)          | Algoritmos de control      | Python               |
| 9   | **El Explorador de Mundos** (Reinforcement Learning) | IA y aprendizaje automático | Python             |
| 10  | **El Constructor de Lenguajes** (Mini Compilador)  | Compiladores e intérpretes | Python               |
| 11  | **El Motor de Búsqueda Semántica** (Vector Search) | Búsqueda vectorial y IA    | Python               |
| 12  | **Servidor HTTP Concurrente**                      | Sockets y concurrencia     | C                    |
| 13  | **El Laboratorio Virtual** (Proxmox & Homelab)     | Virtualización y automatización | Python / Bash   |

### 📌 Videos de Inspiración

- [Proceso de entrevistas de Anthropic](https://www.youtube.com/watch?v=yeuJ4hSmT3s) — Módulos 1-5
- [Rivendell Hyprland Ricing](https://www.youtube.com/watch?v=DxEKF0cuEzc) — Módulo 6
  ([Repo Rivendell](https://codeberg.org/zacoons/rivendell-hyprdots))
- [The Art of Linux CLIs](https://www.youtube.com/watch?v=KdoaiGTIBY4) — Módulo 7
- [Experiencia completa con Arch Linux](https://www.youtube.com/watch?v=uZDPXFQYz0Q) — Módulo 7
- [Ardens — Proxmox Homelab Series](https://www.youtube.com/@ardens_dev) — Módulo 13

### 🗺️ Mapas Mentales

Cada módulo incluye un archivo `mapa-mental.md` con un mapa conceptual del camino de
aprendizaje recomendado, prerequisitos, conceptos clave y siguientes pasos.

---

## 📁 Estructura del Proyecto

```
Proyectos-Entrevistas/
├── README.md
├── DIRECTRICES_AGENTE.md
├── .gitignore
├── deploy.bat                  # Script de despliegue para Windows
├── deploy.sh                   # Script de despliegue para Linux/Mac
├── docker/
│   └── Dockerfile
└── main/
    ├── modulo-1-lru-cache/
    ├── modulo-2-dag-task-manager/
    ├── modulo-3-web-crawler/
    ├── modulo-4-llm-inference/
    ├── modulo-5-sampling-profiler/
    ├── modulo-6-hyprland-ricing/
    │   ├── guia-arch-linux/        # Tutorial instalación Arch
    │   └── codigo/{cpp,shell,qml,python}/
    ├── modulo-7-cli-terminal-playground/
    │   ├── guia-arch-uso/          # Guía uso diario de Arch
    │   └── codigo/python/
    └── lenguajes/
        ├── python/
        ├── javascript/
        └── c/
```

---

## 🚀 Instalación y Ejecución

Todo el entorno está containerizado con **Docker**. No necesitas instalar Python, Node.js ni
GCC en tu máquina local.

### Windows

```bat
deploy.bat
```

### Linux / Mac

```bash
chmod +x deploy.sh
bash deploy.sh
```

El script construirá la imagen Docker, montará el directorio actual y te dará un menú
interactivo para seleccionar qué módulo ejecutar o correr todas las pruebas.

---

## 🤖 Directrices para Agentes de IA

Si eres un agente de IA contribuyendo a este repositorio, consulta el archivo
[`DIRECTRICES_AGENTE.md`](DIRECTRICES_AGENTE.md) para conocer las reglas de estructura,
estilo y organización del código.

---

## 📄 Licencia

Este proyecto está bajo la licencia [MIT](https://opensource.org/licenses/MIT).

Hecho con 🧠 y ☕ para aprender y crecer como ingeniero de software.