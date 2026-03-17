#!/usr/bin/env bash
# ==============================================================
# backup_vm.sh — Hace snapshot/backup de una VM en Proxmox
# Módulo 13: Proxmox Homelab
#
# Uso:
#   ./backup_vm.sh --host 192.168.1.10 --node pve --vmid 100
# ==============================================================

set -euo pipefail

HOST=""
NODE="pve"
VMID=""
STORAGE="local"
MODE="snapshot"   # snapshot | suspend | stop

usage() {
    echo "Uso: $0 --host HOST --vmid VMID [--node NODE] [--storage STORAGE] [--mode MODE]"
    exit 1
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --host)    HOST="$2";    shift 2 ;;
        --node)    NODE="$2";    shift 2 ;;
        --vmid)    VMID="$2";    shift 2 ;;
        --storage) STORAGE="$2"; shift 2 ;;
        --mode)    MODE="$2";    shift 2 ;;
        *) usage ;;
    esac
done

[[ -z "$HOST" || -z "$VMID" ]] && usage

API="https://${HOST}:8006/api2/json"

echo "============================================================"
echo "  Proxmox VM Backup — Módulo 13"
echo "============================================================"
echo "  Nodo:    $NODE  |  VMID: $VMID  |  Modo: $MODE"
echo "============================================================"

read -rsp "Contraseña root@pam: " PVE_PASS
echo ""

AUTH=$(curl -s -k -X POST "$API/access/ticket" \
    --data-urlencode "username=root@pam" \
    --data-urlencode "password=$PVE_PASS")
TICKET=$(echo "$AUTH" | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['ticket'])")
CSRF=$(echo "$AUTH"   | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['CSRFPreventionToken'])")

echo "[INFO] Iniciando backup de VM $VMID..."
TASK=$(curl -s -k -X POST "$API/nodes/$NODE/vzdump" \
    -H "CSRFPreventionToken: $CSRF" \
    -b "PVEAuthCookie=$TICKET" \
    --data-urlencode "vmid=$VMID" \
    --data-urlencode "storage=$STORAGE" \
    --data-urlencode "mode=$MODE" \
    --data-urlencode "compress=zstd" \
    | python3 -c "import sys,json; print(json.load(sys.stdin).get('data',''))")

echo "[OK] Task iniciado: $TASK"
echo "     Monitorea en: https://$HOST:8006 → Datacenter → Tasks"
