#!/usr/bin/env bash
# ============================================================
# test_ipc_events.sh — Suite de Tests para el Sistema IPC
# Sub-módulo 6.2: El Sentido del Oído
#
# Ejecuta aserciones sobre el sistema de eventos simulado.
# NOTA: Ejecutar `chmod +x test_ipc_events.sh` antes de usar.
# ============================================================

set -uo pipefail

# --- Contadores ---
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_RUN=0
CURRENT_TEST=""

# --- Colores ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

# --- Funciones de aserción ---

assert_equals() {
    local expected="$1"
    local actual="$2"
    local msg="${3:-"Se esperaba '$expected', se obtuvo '$actual'"}"

    if [[ "$expected" == "$actual" ]]; then
        TESTS_PASSED=$((TESTS_PASSED + 1))
        echo -e "  ${GREEN}✓${NC} $msg"
    else
        TESTS_FAILED=$((TESTS_FAILED + 1))
        echo -e "  ${RED}✗${NC} $msg"
        echo -e "    Esperado: ${YELLOW}$expected${NC}"
        echo -e "    Obtenido: ${YELLOW}$actual${NC}"
    fi
    TESTS_RUN=$((TESTS_RUN + 1))
}

assert_contains() {
    local haystack="$1"
    local needle="$2"
    local msg="${3:-"'$haystack' debe contener '$needle'"}"

    if [[ "$haystack" == *"$needle"* ]]; then
        TESTS_PASSED=$((TESTS_PASSED + 1))
        echo -e "  ${GREEN}✓${NC} $msg"
    else
        TESTS_FAILED=$((TESTS_FAILED + 1))
        echo -e "  ${RED}✗${NC} $msg"
        echo -e "    Texto: ${YELLOW}$haystack${NC}"
        echo -e "    No contiene: ${YELLOW}$needle${NC}"
    fi
    TESTS_RUN=$((TESTS_RUN + 1))
}

assert_file_exists() {
    local filepath="$1"
    local msg="${2:-"El archivo '$filepath' debe existir"}"

    if [[ -e "$filepath" ]]; then
        TESTS_PASSED=$((TESTS_PASSED + 1))
        echo -e "  ${GREEN}✓${NC} $msg"
    else
        TESTS_FAILED=$((TESTS_FAILED + 1))
        echo -e "  ${RED}✗${NC} $msg"
    fi
    TESTS_RUN=$((TESTS_RUN + 1))
}

assert_fifo_exists() {
    local filepath="$1"
    local msg="${2:-"La FIFO '$filepath' debe existir"}"

    if [[ -p "$filepath" ]]; then
        TESTS_PASSED=$((TESTS_PASSED + 1))
        echo -e "  ${GREEN}✓${NC} $msg"
    else
        TESTS_FAILED=$((TESTS_FAILED + 1))
        echo -e "  ${RED}✗${NC} $msg"
    fi
    TESTS_RUN=$((TESTS_RUN + 1))
}

assert_not_exists() {
    local filepath="$1"
    local msg="${2:-"'$filepath' no debe existir"}"

    if [[ ! -e "$filepath" ]]; then
        TESTS_PASSED=$((TESTS_PASSED + 1))
        echo -e "  ${GREEN}✓${NC} $msg"
    else
        TESTS_FAILED=$((TESTS_FAILED + 1))
        echo -e "  ${RED}✗${NC} $msg"
    fi
    TESTS_RUN=$((TESTS_RUN + 1))
}

assert_exit_code() {
    local expected="$1"
    local actual="$2"
    local msg="${3:-"Código de salida debe ser $expected"}"
    assert_equals "$expected" "$actual" "$msg"
}

# --- Cargar el módulo bajo prueba ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Importar funciones sin ejecutar la demo
# Primero debemos desactivar el trap del módulo
source_module() {
    # Guardar y restaurar traps
    trap '' EXIT
    # shellcheck source=ipc_event_system.sh
    source "$SCRIPT_DIR/ipc_event_system.sh"
    trap - EXIT
}

# ============================================================
# Tests
# ============================================================

test_fifo_creation() {
    echo "TEST: La FIFO se crea correctamente"

    local test_pipe="${TMPDIR:-/tmp}/test_fifo_$$"
    EVENT_PIPE="$test_pipe"
    SOUND_LOG="${TMPDIR:-/tmp}/test_sound_log_$$"

    setup_ipc 2>/dev/null

    assert_fifo_exists "$test_pipe" "FIFO creada en el filesystem"
    assert_file_exists "$SOUND_LOG" "Archivo de log de sonidos creado"

    # Limpieza
    rm -f "$test_pipe" "$SOUND_LOG"
}

test_event_parsing() {
    echo "TEST: Los eventos se parsean correctamente"

    local test_pipe="${TMPDIR:-/tmp}/test_parse_$$"
    local test_log="${TMPDIR:-/tmp}/test_parse_log_$$"
    EVENT_PIPE="$test_pipe"
    SOUND_LOG="$test_log"
    : > "$SOUND_LOG"

    configure_sounds

    # Capturar output del procesamiento
    local output
    output=$(process_event "windowopenev>>kitty,Terminal" 2>&1)

    assert_contains "$output" "Tipo: windowopenev" "Tipo de evento parseado"
    assert_contains "$output" "Clase: kitty" "Clase de ventana parseada"
    assert_contains "$output" "Título: Terminal" "Título de ventana parseado"

    # Limpieza
    rm -f "$test_log"
}

test_sound_mapping() {
    echo "TEST: Los sonidos se mapean según la configuración"

    local test_log="${TMPDIR:-/tmp}/test_mapping_log_$$"
    SOUND_LOG="$test_log"
    : > "$SOUND_LOG"

    configure_sounds

    process_event "windowopenev>>kitty,Terminal" >/dev/null 2>&1
    local log_content
    log_content=$(cat "$SOUND_LOG")

    assert_contains "$log_content" "scroll_unfurl.wav" \
        "Abrir kitty reproduce scroll_unfurl.wav"

    : > "$SOUND_LOG"
    process_event "destroywindow>>firefox,Mozilla Firefox" >/dev/null 2>&1
    log_content=$(cat "$SOUND_LOG")

    assert_contains "$log_content" "door_close.wav" \
        "Cerrar firefox reproduce door_close.wav"

    # Limpieza
    rm -f "$test_log"
}

test_wildcard_matching() {
    echo "TEST: Los wildcards funcionan para eventos genéricos"

    local test_log="${TMPDIR:-/tmp}/test_wildcard_log_$$"
    SOUND_LOG="$test_log"
    : > "$SOUND_LOG"

    configure_sounds

    process_event "workspace>>3,workspace-3" >/dev/null 2>&1
    local log_content
    log_content=$(cat "$SOUND_LOG")

    assert_contains "$log_content" "page_turn.wav" \
        "Cambio de workspace reproduce page_turn.wav via wildcard"

    # Limpieza
    rm -f "$test_log"
}

test_cleanup_on_exit() {
    echo "TEST: Los recursos se liberan al terminar"

    local test_pipe="${TMPDIR:-/tmp}/test_cleanup_$$"
    local test_log="${TMPDIR:-/tmp}/test_cleanup_log_$$"
    EVENT_PIPE="$test_pipe"
    SOUND_LOG="$test_log"

    # Crear recursos manualmente
    mkfifo "$test_pipe"
    touch "$test_log"

    # Verificar que existen
    assert_fifo_exists "$test_pipe" "FIFO existe antes de limpieza"
    assert_file_exists "$test_log" "Log existe antes de limpieza"

    # Ejecutar limpieza
    cleanup_ipc 2>/dev/null

    # Verificar que se eliminaron
    assert_not_exists "$test_pipe" "FIFO eliminada tras limpieza"
    assert_not_exists "$test_log" "Log eliminado tras limpieza"
}

test_multiple_events() {
    echo "TEST: Múltiples eventos se procesan en secuencia"

    local test_log="${TMPDIR:-/tmp}/test_multi_log_$$"
    SOUND_LOG="$test_log"
    : > "$SOUND_LOG"

    configure_sounds

    process_event "windowopenev>>kitty,Terminal" >/dev/null 2>&1
    process_event "windowopenev>>firefox,Browser" >/dev/null 2>&1
    process_event "destroywindow>>kitty,Terminal" >/dev/null 2>&1

    local log_lines
    log_lines=$(wc -l < "$SOUND_LOG")

    assert_equals "3" "$log_lines" "Se registraron 3 sonidos en el log"

    local log_content
    log_content=$(cat "$SOUND_LOG")

    assert_contains "$log_content" "scroll_unfurl.wav" "Primer sonido: scroll_unfurl"
    assert_contains "$log_content" "door_open.wav" "Segundo sonido: door_open"
    assert_contains "$log_content" "paper_crumple.wav" "Tercer sonido: paper_crumple"

    # Limpieza
    rm -f "$test_log"
}

test_unknown_event() {
    echo "TEST: Eventos desconocidos no causan errores"

    local test_log="${TMPDIR:-/tmp}/test_unknown_log_$$"
    SOUND_LOG="$test_log"
    : > "$SOUND_LOG"

    configure_sounds

    local output
    output=$(process_event "unknownevent>>unknown_app,Unknown" 2>&1)
    local exit_code=$?

    assert_contains "$output" "Sin sonido asignado" \
        "Evento desconocido reporta que no tiene sonido"

    assert_equals "1" "$exit_code" \
        "Código de salida 1 para evento sin sonido"

    local log_lines
    log_lines=$(wc -l < "$SOUND_LOG")
    assert_equals "0" "$log_lines" "No se registró ningún sonido"

    # Limpieza
    rm -f "$test_log"
}

test_sound_log_creation() {
    echo "TEST: El log de sonidos se crea y registra correctamente"

    local test_log="${TMPDIR:-/tmp}/test_logfile_$$"
    SOUND_LOG="$test_log"
    : > "$SOUND_LOG"

    configure_sounds

    play_sound "test_sound.wav" "test:event" >/dev/null

    assert_file_exists "$SOUND_LOG" "Archivo de log existe"

    local log_content
    log_content=$(cat "$SOUND_LOG")

    assert_contains "$log_content" "[SOUND]" "Log contiene prefijo [SOUND]"
    assert_contains "$log_content" "test_sound.wav" "Log contiene nombre del archivo"
    assert_contains "$log_content" "test:event" "Log contiene info del evento"

    # Limpieza
    rm -f "$test_log"
}

test_full_demo() {
    echo "TEST: La demo completa se ejecuta sin errores"

    local output
    output=$("$SCRIPT_DIR/ipc_event_system.sh" 2>&1)
    local exit_code=$?

    assert_equals "0" "$exit_code" "Demo termina con código 0"
    assert_contains "$output" "Completada exitosamente" \
        "Demo reporta ejecución exitosa"
    assert_contains "$output" "scroll_unfurl.wav" \
        "Demo reproduce sonido de pergamino"
    assert_contains "$output" "paper_crumple.wav" \
        "Demo reproduce sonido de papel arrugado"
    assert_contains "$output" "page_turn.wav" \
        "Demo reproduce sonido de pasar página"
}

# ============================================================
# Runner principal
# ============================================================

main() {
    echo "============================================================"
    echo "  🧪 Tests — Sub-módulo 6.2: El Sentido del Oído"
    echo "============================================================"
    echo ""

    # Cargar módulo bajo prueba
    source_module

    test_fifo_creation
    echo ""

    test_event_parsing
    echo ""

    test_sound_mapping
    echo ""

    test_wildcard_matching
    echo ""

    test_cleanup_on_exit
    echo ""

    test_multiple_events
    echo ""

    test_unknown_event
    echo ""

    test_sound_log_creation
    echo ""

    test_full_demo
    echo ""

    # --- Resumen ---
    echo "============================================================"
    echo "  Resultados: $TESTS_RUN tests ejecutados"
    echo -e "  ${GREEN}Pasaron: $TESTS_PASSED${NC}"
    if [[ $TESTS_FAILED -gt 0 ]]; then
        echo -e "  ${RED}Fallaron: $TESTS_FAILED${NC}"
    else
        echo -e "  Fallaron: 0"
    fi
    echo "============================================================"

    if [[ $TESTS_FAILED -gt 0 ]]; then
        exit 1
    fi
    exit 0
}

main "$@"
