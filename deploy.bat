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
echo   6) Ejecutar TODAS las pruebas
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
    docker run --rm -v "%cd%":/app anthropic-gauntlet bash -c "cd /app/main/modulo-3-web-crawler && node codigo/javascript/index.js || echo 'No hay código disponible aún.'"
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
