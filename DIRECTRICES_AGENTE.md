# 🤖 Directrices para Agentes de IA

## Objetivo del Repositorio

Este repositorio es un campo de entrenamiento para dominar conceptos de entrevistas técnicas
de alto nivel, inspirado en el proceso de entrevistas de Anthropic. Cada módulo es un proyecto
práctico que cubre un tema clave.

---

## 📏 Reglas de Estructura del Código

### Organización de módulos

- Cada módulo vive en su propia carpeta dentro de `main/`:
  - `main/modulo-1-lru-cache/`
  - `main/modulo-2-dag-task-manager/`
  - `main/modulo-3-web-crawler/`
  - `main/modulo-4-llm-inference/`
  - `main/modulo-5-sampling-profiler/`
  - `main/modulo-6-hyprland-ricing/`
  - `main/modulo-7-cli-terminal-playground/`

### Separación por lenguaje

- Dentro de cada módulo, el código debe estar separado por lenguaje en subcarpetas bajo
  `codigo/`. Ejemplo:
  ```
  main/modulo-1-lru-cache/
  └── codigo/
      └── python/
          ├── lru_cache.py
          └── test_lru_cache.py
  ```

### Tutoriales de lenguaje

- Por cada lenguaje utilizado en el repositorio, se debe incluir:
  - **Tutorial básico:** Fundamentos del lenguaje en `main/lenguajes/{lenguaje}/tutorial-basico/`
  - **Tutorial aplicado:** Uso del lenguaje aplicado al contexto del proyecto en
    `main/lenguajes/{lenguaje}/tutorial-aplicado/`

### Mapas mentales de aprendizaje

- Cada módulo debe incluir un archivo `mapa-mental.md` con un mapa conceptual en texto
  que muestre: prerequisitos, conceptos clave, camino de aprendizaje y siguientes pasos.

### Archivos en la raíz del repositorio

Solo los siguientes archivos y carpetas deben existir en la raíz:

- `README.md`
- `DIRECTRICES_AGENTE.md`
- `.gitignore`
- `deploy.bat`
- `deploy.sh`
- `docker/`
- `main/`

No se deben crear carpetas adicionales en la raíz sin justificación.

---

## 🛠️ Tecnologías Utilizadas y Alternativas Modernas

| Tecnología            | Versión / Estándar | Alternativa Moderna          | Notas                                           |
| --------------------- | ------------------ | ---------------------------- | ----------------------------------------------- |
| **Python**            | 3.11+              | Python 3.12+ (nuevas features) | Lenguaje principal para módulos 1, 2, 4 y 7     |
| **Node.js**           | 18+                | Deno o Bun                   | Usado en módulo 3 (Web Crawler)                 |
| **C**                 | C17                | Rust (seguridad de memoria)  | Usado en módulo 5 (Sampling Profiler)           |
| **C++**               | C++17              | Rust                         | Usado en módulo 6 (Hyprland Plugins, 9-slice)   |
| **Bash/Shell**        | Bash 5+            | Nushell, Fish                | Usado en módulo 6 (IPC) y módulo 7 (scripts)    |
| **QML**               | Qt 6               | GTK4 + Blueprint             | Usado en módulo 6 (Quickshell widgets)           |
| **Docker**            | —                  | —                            | Containerización del entorno de desarrollo       |
| **pytest**            | —                  | —                            | Framework de testing para Python                 |
| **Jest / Node test runner** | —            | Vitest                       | Framework de testing para JavaScript             |

---

## 🐳 Automatización con Docker

- La instalación y ejecución del entorno se realiza mediante Docker.
- En **Windows**, ejecutar `deploy.bat`.
- En **Linux/Mac**, ejecutar `bash deploy.sh`.
- Los scripts construyen la imagen Docker, montan el proyecto y permiten seleccionar qué
  módulo ejecutar de forma interactiva.
- No se requiere instalación local de dependencias: todo corre dentro del contenedor.

---

## ✅ Buenas Prácticas para el Agente

1. **No modificar archivos fuera de `main/`** sin instrucción explícita.
2. **Agregar tests** para todo código nuevo.
3. **Documentar** cada módulo con un `README.md` propio dentro de su carpeta.
4. **Seguir la convención de nombres** existente (kebab-case para carpetas, snake_case para
   archivos Python, camelCase para archivos JavaScript).
5. **Comentar el código** en español cuando sea necesario.
