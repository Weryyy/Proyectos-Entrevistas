#!/usr/bin/env bash
# ==============================================================
# setup_lxc.sh — Crea un contenedor LXC en Proxmox via API REST
# Módulo 13: Proxmox Homelab
#
# Uso:
#   chmod +x setup_lxc.sh
#   ./setup_lxc.sh --host 192.168.1.10 --node pve --vmid 200 \
#                  --hostname mi-contenedor --password secreto
# ==============================================================

set -euo pipefail

# --- Valores por defecto ---
HOST=""
NODE="pve"
VMID="200"
HOSTNAME_CT="homelab-lxc"
PASSWORD_CT="changeme"
TEMPLATE="local:vztmpl/debian-12-standard_12.0-1_amd64.tar.zst"
CORES=2
MEMORY=512   # MB
DISK="local-lvm:8"  # 8 GB

usage() {
    echo "Uso: $0 --host HOST [--node NODE] [--vmid VMID]"
    echo "         [--hostname HOSTNAME] [--password PASSWORD]"
    exit 1
}

# --- Parseo de argumentos ---
while [[ $# -gt 0 ]]; do
    case "$1" in
        --host)      HOST="$2";        shift 2 ;;
        --node)      NODE="$2";        shift 2 ;;
        --vmid)      VMID="$2";        shift 2 ;;
        --hostname)  HOSTNAME_CT="$2"; shift 2 ;;
        --password)  PASSWORD_CT="$2"; shift 2 ;;
        *) usage ;;
    esac
done

[[ -z "$HOST" ]] && usage

API="https://${HOST}:8006/api2/json"

echo "============================================================"
echo "  Proxmox LXC Setup — Módulo 13"
echo "============================================================"
echo "  Nodo:     $NODE"
echo "  VMID:     $VMID"
echo "  Hostname: $HOSTNAME_CT"
echo "============================================================"

# --- Obtener ticket de autenticación ---
echo "[1/3] Autenticando..."
read -rsp "Usuario root@pam — Contraseña Proxmox: " PVE_PASS
echo ""

AUTH=$(curl -s -k -X POST "$API/access/ticket" \
    --data-urlencode "username=root@pam" \
    --data-urlencode "password=$PVE_PASS")

TICKET=$(echo "$AUTH" | python3 -c "import sys,json; d=json.load(sys.stdin)['data']; print(d['ticket'])")
CSRF=$(echo "$AUTH"   | python3 -c "import sys,json; d=json.load(sys.stdin)['data']; print(d['CSRFPreventionToken'])")

echo "[OK] Ticket obtenido."

# --- Crear el contenedor LXC ---
echo "[2/3] Creando contenedor LXC $VMID ($HOSTNAME_CT)..."
curl -s -k -X POST "$API/nodes/$NODE/lxc" \
    -H "CSRFPreventionToken: $CSRF" \
    -b "PVEAuthCookie=$TICKET" \
    --data-urlencode "vmid=$VMID" \
    --data-urlencode "hostname=$HOSTNAME_CT" \
    --data-urlencode "ostemplate=$TEMPLATE" \
    --data-urlencode "password=$PASSWORD_CT" \
    --data-urlencode "cores=$CORES" \
    --data-urlencode "memory=$MEMORY" \
    --data-urlencode "rootfs=$DISK" \
    --data-urlencode "net0=name=eth0,bridge=vmbr0,ip=dhcp" \
    | python3 -c "import sys,json; r=json.load(sys.stdin); print('[OK]', r.get('data','creado'))"

# --- Iniciar el contenedor ---
echo "[3/3] Iniciando contenedor..."
curl -s -k -X POST "$API/nodes/$NODE/lxc/$VMID/status/start" \
    -H "CSRFPreventionToken: $CSRF" \
    -b "PVEAuthCookie=$TICKET" \
    | python3 -c "import sys,json; r=json.load(sys.stdin); print('[OK] Task:', r.get('data','iniciado'))"

echo ""
echo "✅ Contenedor LXC $VMID creado e iniciado en nodo $NODE."
echo "   Accede con: pct enter $VMID  (desde el nodo Proxmox)"
