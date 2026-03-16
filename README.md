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
| 1   | **El Corazón del Rendimiento** (LRU Cache)        | Estructuras de datos      | Python               |
| 2   | **Orquestador de Misiones** (DAG & Task Manager)  | Grafos y planificación    | Python               |
| 3   | **El Rastreador Cortés** (Web Crawler)             | Concurrencia y redes      | JavaScript (Node.js) |
| 4   | **Simulador de Inferencia de LLM**                | Sistemas y optimización   | Python               |
| 5   | **El Detective de Código** (Sampling Profiler)     | Sistemas de bajo nivel    | C                    |

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