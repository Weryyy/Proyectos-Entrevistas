#!/usr/bin/env bash
# ============================================================
# deploy.sh — Script de despliegue para Linux/Mac
# Construye y ejecuta el entorno Docker del proyecto
# ============================================================

set -e

# --- Verificar que Docker está instalado ---
if ! command -v docker &> /dev/null; then
    echo "[ERROR] Docker no está instalado o no se encuentra en el PATH."
    echo "        Descárgalo desde https://www.docker.com/products/docker-desktop"
    exit 1
fi

echo "============================================================"
echo "  The Anthropic Gauntlet — Entorno de Desarrollo"
echo "============================================================"
echo ""

# --- Construir la imagen Docker ---
echo "[INFO] Construyendo la imagen Docker..."
docker build -t anthropic-gauntlet -f docker/Dockerfile .
echo "[OK] Imagen construida exitosamente."
echo ""

# --- Función del menú interactivo ---
show_menu() {
    echo "============================================================"
    echo "  Selecciona una opción:"
    echo "============================================================"
    echo "  1) Módulo 1 — El Corazón del Rendimiento (LRU Cache)"
    echo "  2) Módulo 2 — Orquestador de Misiones (DAG & Task Manager)"
    echo "  3) Módulo 3 — El Rastreador Cortés (Web Crawler)"
    echo "  4) Módulo 4 — Simulador de Inferencia de LLM"
    echo "  5) Módulo 5 — El Detective de Código (Sampling Profiler)"
    echo "  6) Ejecutar TODAS las pruebas"
    echo "  0) Salir"
    echo "============================================================"
}

# --- Ejecutar el contenedor según la opción seleccionada ---
run_module() {
    local module_dir="$1"
    local cmd="$2"
    docker run --rm -v "$(pwd)":/app anthropic-gauntlet bash -c "$cmd"
}

# --- Bucle principal del menú ---
while true; do
    show_menu
    read -rp "Tu elección: " opcion

    case "$opcion" in
        1)
            echo "[INFO] Ejecutando Módulo 1 — LRU Cache..."
            run_module "modulo-1-lru-cache" \
                "cd /app/main/modulo-1-lru-cache && pytest codigo/python/ -v || echo 'No hay tests disponibles aún.'"
            ;;
        2)
            echo "[INFO] Ejecutando Módulo 2 — DAG & Task Manager..."
            run_module "modulo-2-dag-task-manager" \
                "cd /app/main/modulo-2-dag-task-manager && pytest codigo/python/ -v || echo 'No hay tests disponibles aún.'"
            ;;
        3)
            echo "[INFO] Ejecutando Módulo 3 — Web Crawler..."
            run_module "modulo-3-web-crawler" \
                "cd /app/main/modulo-3-web-crawler && node --test codigo/javascript/test_crawler.js || echo 'No hay tests disponibles aún.'"
            ;;
        4)
            echo "[INFO] Ejecutando Módulo 4 — Simulador de Inferencia de LLM..."
            run_module "modulo-4-llm-inference" \
                "cd /app/main/modulo-4-llm-inference && pytest codigo/python/ -v || echo 'No hay tests disponibles aún.'"
            ;;
        5)
            echo "[INFO] Ejecutando Módulo 5 — Sampling Profiler..."
            run_module "modulo-5-sampling-profiler" \
                "cd /app/main/modulo-5-sampling-profiler && if [ -f codigo/c/Makefile ]; then make -C codigo/c/ run; else echo 'No hay código disponible aún.'; fi"
            ;;
        6)
            echo "[INFO] Ejecutando TODAS las pruebas..."
            run_module "all" \
                "cd /app && python -m pytest main/ -v --ignore=main/lenguajes; echo '--- Pruebas finalizadas ---'"
            ;;
        0)
            echo "[INFO] Saliendo..."
            exit 0
            ;;
        *)
            echo "[AVISO] Opción no válida. Intenta de nuevo."
            ;;
    esac
    echo ""
done
