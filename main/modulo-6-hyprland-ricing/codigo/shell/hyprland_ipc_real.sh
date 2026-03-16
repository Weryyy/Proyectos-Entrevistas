#!/usr/bin/env bash
# ============================================================
# hyprland_ipc_real.sh — Script REAL para Hyprland IPC
#
# NOTA: Este script requiere un sistema con Hyprland corriendo.
# Es un ejemplo de referencia basado en el proyecto Rivendell
# de zacoons. NO se ejecuta en CI.
#
# Para usarlo en tu sistema:
#   1. Copiar a ~/.config/hypr/scripts/
#   2. chmod +x hyprland_ipc_real.sh
#   3. Añadir a hyprland.conf:
#      exec-once = ~/.config/hypr/scripts/hyprland_ipc_real.sh
# ============================================================

set -euo pipefail

# --- Verificar que Hyprland está corriendo ---
# HYPRLAND_INSTANCE_SIGNATURE es una variable de entorno que
# Hyprland establece automáticamente al iniciar. Sin ella,
# no podemos localizar el socket IPC.
if [[ -z "${HYPRLAND_INSTANCE_SIGNATURE:-}" ]]; then
    echo "ERROR: Hyprland no está corriendo (HYPRLAND_INSTANCE_SIGNATURE no definida)"
    echo "Este script debe ejecutarse dentro de una sesión Hyprland."
    exit 1
fi

# --- Verificar dependencias ---
# socat: herramienta para conexiones bidireccionales de datos
# sox (play): reproductor de audio en línea de comandos
for cmd in socat play; do
    if ! command -v "$cmd" &>/dev/null; then
        echo "ERROR: '$cmd' no encontrado. Instalar con:"
        echo "  pacman -S socat sox    # Arch Linux"
        echo "  apt install socat sox  # Debian/Ubuntu"
        exit 1
    fi
done

# --- Configuración de rutas ---
# Hyprland crea sus sockets en $XDG_RUNTIME_DIR/hypr/<signature>/
# .socket.sock  → socket de comandos (hyprctl)
# .socket2.sock → socket de eventos (streaming)
XDG="${XDG_RUNTIME_DIR:-/run/user/$(id -u)}"
SOCKET_DIR="${XDG}/hypr/${HYPRLAND_INSTANCE_SIGNATURE}"
EVENT_SOCKET="${SOCKET_DIR}/.socket2.sock"

# Directorio donde almacenamos los archivos de sonido .wav/.ogg
SOUNDS_DIR="${HOME}/.config/hypr/sounds"

# Volumen de reproducción (0.0 a 1.0)
VOLUME="0.3"

# --- Verificar que el socket existe ---
if [[ ! -S "$EVENT_SOCKET" ]]; then
    echo "ERROR: Socket de eventos no encontrado: $EVENT_SOCKET"
    echo "Verificar que Hyprland está corriendo correctamente."
    exit 1
fi

# --- Mapeo de eventos a sonidos ---
# Formato: [evento:clase_ventana]=archivo_sonido
declare -A SOUND_MAP=(
    # Terminales: sonido de pergamino
    ["windowopenev:kitty"]="scroll_unfurl.wav"
    ["windowopenev:Alacritty"]="scroll_unfurl.wav"
    ["windowopenev:foot"]="scroll_unfurl.wav"
    ["destroywindow:kitty"]="paper_crumple.wav"
    ["destroywindow:Alacritty"]="paper_crumple.wav"
    ["destroywindow:foot"]="paper_crumple.wav"
    # Navegador: sonido de puerta
    ["windowopenev:firefox"]="door_open.wav"
    ["destroywindow:firefox"]="door_close.wav"
    # Cambio de workspace: pasar página
    ["workspace:*"]="page_turn.wav"
)

# --- Función para reproducir sonido ---
play_sound() {
    local sound_file="$1"
    local full_path="${SOUNDS_DIR}/${sound_file}"

    # Verificar que el archivo de sonido existe
    if [[ ! -f "$full_path" ]]; then
        return 0
    fi

    # Reproducir en background para no bloquear el procesamiento de eventos
    # -q: modo silencioso (sin output en terminal)
    # -v: volumen relativo
    play -q -v "$VOLUME" "$full_path" &
}

# --- Procesamiento de eventos ---
# socat conecta al socket Unix de Hyprland en modo lectura (-U)
# Cada línea es un evento con formato: tipo>>datos
socat -U - UNIX-CONNECT:"$EVENT_SOCKET" | while IFS= read -r line; do
    # Separar tipo de evento y datos
    event_type="${line%%>>*}"
    event_data="${line#*>>}"

    case "$event_type" in
        windowopenev)
            # Datos: clase_ventana,título_ventana
            window_class="${event_data%%,*}"
            key="windowopenev:${window_class}"
            sound="${SOUND_MAP[$key]:-}"
            [[ -n "$sound" ]] && play_sound "$sound"
            ;;
        destroywindow)
            # Datos: dirección_ventana (hex)
            # Para mapear a clase necesitaríamos hyprctl clients
            # Simplificación: usar sonido genérico
            play_sound "paper_crumple.wav"
            ;;
        workspace)
            # Datos: nombre_del_workspace
            sound="${SOUND_MAP["workspace:*"]:-}"
            [[ -n "$sound" ]] && play_sound "$sound"
            ;;
    esac
done
