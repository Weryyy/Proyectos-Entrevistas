#!/usr/bin/env bash
# ============================================================
# ipc_event_system.sh — Sistema de Eventos IPC Simulado
# Sub-módulo 6.2: El Sentido del Oído
#
# Este script demuestra cómo funciona la comunicación entre
# procesos (IPC) para reaccionar a eventos del compositor.
#
# NOTA: Ejecutar `chmod +x ipc_event_system.sh` antes de usar.
# ============================================================

set -euo pipefail

# --- Configuración ---
# En un sistema real con Hyprland, usaríamos:
# SOCKET="$XDG_RUNTIME_DIR/hypr/$HYPRLAND_INSTANCE_SIGNATURE/.socket2.sock"
# Aquí simulamos con una FIFO (named pipe)

EVENT_PIPE="${TMPDIR:-/tmp}/hypr_events_$$"
SOUND_LOG="${TMPDIR:-/tmp}/sound_log_$$"
CONFIG_FILE=""

# === Clase: EventEmitter (simulador del compositor) ===
# En Hyprland real, el compositor emite eventos automáticamente.
# Nosotros los simulamos escribiendo en una FIFO.

setup_ipc() {
    # Crear la FIFO (named pipe) para comunicación
    # Las FIFOs son como tuberías con nombre en el filesystem
    # Permiten que un proceso escriba y otro lea, como un socket simplificado
    if [[ -p "$EVENT_PIPE" ]]; then
        rm "$EVENT_PIPE"
    fi
    mkfifo "$EVENT_PIPE"
    : > "$SOUND_LOG"
    echo "[IPC] Canal de eventos creado: $EVENT_PIPE"
}

cleanup_ipc() {
    # Limpieza de recursos — equivalente a un destructor
    rm -f "$EVENT_PIPE" "$SOUND_LOG"
    echo "[IPC] Recursos liberados"
}

# Trap para limpiar al salir (RAII en shell)
trap cleanup_ipc EXIT

emit_event() {
    local event_type="$1"
    local window_class="$2"
    local window_title="$3"

    # Formato de evento similar a Hyprland IPC:
    # eventtype>>data
    echo "${event_type}>>${window_class},${window_title}" > "$EVENT_PIPE" &
}

# === Clase: SoundReactor (reactor de sonidos) ===
# Mapea eventos a sonidos según reglas configurables

declare -A SOUND_MAP

configure_sounds() {
    # Configuración de sonidos por clase de ventana y tipo de evento
    # En Rivendell, zacoons usó sonidos temáticos de fantasía:
    # - Abrir terminal → sonido de pergamino desenrollándose
    # - Cerrar terminal → sonido de papel arrugándose

    SOUND_MAP["windowopenev:kitty"]="scroll_unfurl.wav"
    SOUND_MAP["windowopenev:Alacritty"]="scroll_unfurl.wav"
    SOUND_MAP["destroywindow:kitty"]="paper_crumple.wav"
    SOUND_MAP["destroywindow:Alacritty"]="paper_crumple.wav"
    SOUND_MAP["windowopenev:firefox"]="door_open.wav"
    SOUND_MAP["destroywindow:firefox"]="door_close.wav"
    SOUND_MAP["workspace:*"]="page_turn.wav"
}

play_sound() {
    local sound_file="$1"
    local event_info="$2"

    # En un sistema real usaríamos sox:
    # play -q "$SOUNDS_DIR/$sound_file"
    # O con pipewire/pw-play:
    # pw-play "$SOUNDS_DIR/$sound_file"

    # Simulación: registrar en log
    echo "[SOUND] Reproduciendo: $sound_file (evento: $event_info)" >> "$SOUND_LOG"
    echo "[🔊] $sound_file — $event_info"
}

process_event() {
    local raw_event="$1"

    # Parsear el evento (formato: tipo>>clase,título)
    local event_type="${raw_event%%>>*}"
    local event_data="${raw_event#*>>}"
    local window_class="${event_data%%,*}"
    local window_title="${event_data#*,}"

    echo "[EVENT] Tipo: $event_type | Clase: $window_class | Título: $window_title"

    # Buscar sonido específico para esta combinación
    local key="${event_type}:${window_class}"
    local sound="${SOUND_MAP[$key]:-}"

    if [[ -n "$sound" ]]; then
        play_sound "$sound" "$key"
        return 0
    fi

    # Buscar con wildcard
    local wildcard_key="${event_type}:*"
    local wildcard_sound="${SOUND_MAP[$wildcard_key]:-}"

    if [[ -n "$wildcard_sound" ]]; then
        play_sound "$wildcard_sound" "$wildcard_key"
        return 0
    fi

    echo "[EVENT] Sin sonido asignado para: $key"
    return 1
}

# === Listener principal ===
# Lee eventos de la FIFO y los procesa

start_listener() {
    echo "[LISTENER] Escuchando eventos en $EVENT_PIPE..."
    echo "[LISTENER] (En Hyprland real: socat -U - UNIX-CONNECT:\$SOCKET)"
    echo ""

    # Leer eventos continuamente de la FIFO
    while IFS= read -r event; do
        if [[ -n "$event" ]]; then
            process_event "$event"
        fi
    done < "$EVENT_PIPE"

    echo "[LISTENER] Fin de eventos"
}

# === Demo interactiva ===

run_demo() {
    echo "============================================================"
    echo "  🧝 El Sentido del Oído — Demo de IPC y Sonidos"
    echo "============================================================"
    echo ""

    setup_ipc
    configure_sounds

    # Iniciar listener en background
    start_listener &
    local listener_pid=$!

    # Esperar a que la FIFO esté lista
    sleep 0.2

    # Simular secuencia de eventos del compositor
    echo "--- Simulando eventos del compositor ---"
    echo ""

    emit_event "windowopenev" "kitty" "Terminal"
    sleep 0.3

    emit_event "windowopenev" "firefox" "Mozilla Firefox"
    sleep 0.3

    emit_event "workspace" "2" "workspace-2"
    sleep 0.3

    emit_event "destroywindow" "kitty" "Terminal"
    sleep 0.3

    emit_event "destroywindow" "firefox" "Mozilla Firefox"
    sleep 0.3

    # Cerrar la FIFO para que el listener termine
    exec 3>"$EVENT_PIPE"
    exec 3>&-

    wait $listener_pid 2>/dev/null

    echo ""
    echo "--- Registro de sonidos reproducidos ---"
    cat "$SOUND_LOG"
    echo ""
    echo "[DEMO] Completada exitosamente"
}

# === Función para uso como biblioteca (source) ===
# Si se ejecuta directamente, correr la demo
# Si se importa con 'source', solo cargar funciones

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    run_demo
fi
