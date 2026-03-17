@echo off
REM ============================================================
REM deploy.bat — Script de despliegue para Windows
REM Construye y ejecuta el entorno Docker del proyecto
REM ============================================================

setlocal enabledelayedexpansion

REM --- Verificar que Docker está instalado ---
where docker >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Docker no está instalado o no se encuentra en el PATH.
    echo         Descárgalo desde https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

echo ============================================================
echo   The Anthropic Gauntlet — Entorno de Desarrollo
echo ============================================================
echo.

REM --- Construir la imagen Docker ---
echo [INFO] Construyendo la imagen Docker...
docker build -t anthropic-gauntlet -f docker/Dockerfile .
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Falló la construcción de la imagen Docker.
    pause
    exit /b 1
)
echo [OK] Imagen construida exitosamente.
echo.

REM --- Menú de selección ---
:menu
echo ============================================================
echo   Selecciona una opción:
echo ============================================================
echo   1) Módulo 1 — El Corazón del Rendimiento (LRU Cache)
echo   2) Módulo 2 — Orquestador de Misiones (DAG ^& Task Manager)
echo   3) Módulo 3 — El Rastreador Cortés (Web Crawler)
echo   4) Módulo 4 — Simulador de Inferencia de LLM
echo   5) Módulo 5 — El Detective de Código (Sampling Profiler)
echo   6) Módulo 6 — El Artesano del Escritorio (Hyprland Ricing)
echo   7) Módulo 7 — The Terminal Playground (CLI Tools)
echo   8) Módulo 8 — El Guardián de Tráfico (Rate Limiter)
echo   9) Módulo 9 — El Explorador de Mundos (Reinforcement Learning)
echo  10) Módulo 10 — El Constructor de Lenguajes (Mini Compilador)
echo  11) Módulo 11 — El Motor de Búsqueda Semántica (Vector Search)
echo  12) Módulo 12 — Servidor HTTP Concurrente (C ^+ pthreads)
echo  13) Módulo 13 — El Laboratorio Virtual (Proxmox ^& Homelab)
echo  99) Ejecutar TODAS las pruebas
echo   0) Salir
echo ============================================================
set /p opcion="Tu elección: "

REM --- Ejecutar el contenedor según la opción seleccionada ---
if "%opcion%"=="1" (
    echo [INFO] Ejecutando Módulo 1 — LRU Cache...
    docker run --rm -v "%cd%":/app anthropic-gauntlet bash -c "cd /app/main/modulo-1-lru-cache && pytest codigo/python/ -v || echo 'No hay tests disponibles aún.'"
    goto menu
)
if "%opcion%"=="2" (
    echo [INFO] Ejecutando Módulo 2 — DAG ^& Task Manager...
    docker run --rm -v "%cd%":/app anthropic-gauntlet bash -c "cd /app/main/modulo-2-dag-task-manager && pytest codigo/python/ -v || echo 'No hay tests disponibles aún.'"
    goto menu
)
if "%opcion%"=="3" (
    echo [INFO] Ejecutando Módulo 3 — Web Crawler...
    docker run --rm -v "%cd%":/app anthropic-gauntlet bash -c "cd /app/main/modulo-3-web-crawler && node --test codigo/javascript/test_crawler.js || echo 'No hay tests disponibles aún.'"
    goto menu
)
if "%opcion%"=="4" (
    echo [INFO] Ejecutando Módulo 4 — Simulador de Inferencia de LLM...
    docker run --rm -v "%cd%":/app anthropic-gauntlet bash -c "cd /app/main/modulo-4-llm-inference && pytest codigo/python/ -v || echo 'No hay tests disponibles aún.'"
    goto menu
)
if "%opcion%"=="5" (
    echo [INFO] Ejecutando Módulo 5 — Sampling Profiler...
    docker run --rm -v "%cd%":/app anthropic-gauntlet bash -c "cd /app/main/modulo-5-sampling-profiler && if [ -f codigo/c/Makefile ]; then make -C codigo/c/ run; else echo 'No hay código disponible aún.'; fi"
    goto menu
)
if "%opcion%"=="6" (
    echo [INFO] Ejecutando Módulo 6 — Hyprland Ricing...
    docker run --rm -v "%cd%":/app anthropic-gauntlet bash -c "cd /app/main/modulo-6-hyprland-ricing && pytest codigo/python/ codigo/qml/ -v || echo 'No hay tests disponibles aún.'; if [ -f codigo/cpp/Makefile ]; then make -C codigo/cpp/ test; fi"
    goto menu
)
if "%opcion%"=="7" (
    echo [INFO] Ejecutando Módulo 7 — Terminal Playground...
    docker run --rm -v "%cd%":/app anthropic-gauntlet bash -c "cd /app/main/modulo-7-cli-terminal-playground && pytest codigo/python/test_cli_tools.py -v || echo 'No hay tests disponibles aún.'"
    goto menu
)
if "%opcion%"=="8" (
    echo [INFO] Ejecutando Módulo 8 — Rate Limiter...
    docker run --rm -v "%cd%":/app anthropic-gauntlet bash -c "cd /app/main/modulo-8-rate-limiter && pytest codigo/python/ -v || echo 'No hay tests disponibles aún.'"
    goto menu
)
if "%opcion%"=="9" (
    echo [INFO] Ejecutando Módulo 9 — Reinforcement Learning...
    docker run --rm -v "%cd%":/app anthropic-gauntlet bash -c "cd /app/main/modulo-9-reinforcement-learning && pytest codigo/python/ -v || echo 'No hay tests disponibles aún.'"
    goto menu
)
if "%opcion%"=="10" (
    echo [INFO] Ejecutando Módulo 10 — Mini Compilador...
    docker run --rm -v "%cd%":/app anthropic-gauntlet bash -c "cd /app/main/modulo-10-mini-compilador && pytest codigo/python/ -v || echo 'No hay tests disponibles aún.'"
    goto menu
)
if "%opcion%"=="11" (
    echo [INFO] Ejecutando Módulo 11 — Vector Search...
    docker run --rm -v "%cd%":/app anthropic-gauntlet bash -c "cd /app/main/modulo-11-vector-search && pytest codigo/python/ -v || echo 'No hay tests disponibles aún.'"
    goto menu
)
if "%opcion%"=="12" (
    echo [INFO] Ejecutando Módulo 12 — Servidor HTTP Concurrente...
    docker run --rm -v "%cd%":/app anthropic-gauntlet bash -c "cd /app/main/modulo-12-http-server-concurrente/codigo/c && if [ -f Makefile ]; then make test; else echo 'No hay código disponible aún.'; fi"
    goto menu
)
if "%opcion%"=="13" (
    echo [INFO] Ejecutando Módulo 13 — Proxmox ^& Homelab...
    docker run --rm -v "%cd%":/app anthropic-gauntlet bash -c "cd /app/main/modulo-13-proxmox-homelab && pytest codigo/python/test_proxmox.py -v || echo 'No hay tests disponibles aún.'"
    goto menu
)
if "%opcion%"=="99" (
    echo [INFO] Ejecutando TODAS las pruebas...
    docker run --rm -v "%cd%":/app anthropic-gauntlet bash -c "cd /app && python -m pytest main/ -v --ignore=main/lenguajes; echo '--- Pruebas finalizadas ---'"
    goto menu
)
if "%opcion%"=="0" (
    echo [INFO] Saliendo...
    exit /b 0
)

echo [AVISO] Opción no válida. Intenta de nuevo.
goto menu
