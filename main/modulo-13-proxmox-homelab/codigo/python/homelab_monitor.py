"""
Monitor de recursos del Homelab — Módulo 13.
Muestra CPU, RAM y estado de VMs/LXC de forma periódica.
"""

import time
import argparse
from proxmox_client import ProxmoxClient


def monitor(client: ProxmoxClient, node: str, interval: int = 5, iterations: int = 0) -> None:
    """
    Muestra un resumen de recursos del nodo cada `interval` segundos.

    Args:
        client: ProxmoxClient autenticado.
        node: Nombre del nodo a monitorear.
        interval: Segundos entre actualizaciones.
        iterations: Número de iteraciones (0 = infinito).
    """
    count = 0
    try:
        while True:
            print(f"\n[{time.strftime('%H:%M:%S')}] Actualizando...")
            client.print_summary(node)
            count += 1
            if iterations and count >= iterations:
                break
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\n[INFO] Monitor detenido.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Monitor de Homelab Proxmox")
    parser.add_argument("--host",     required=True)
    parser.add_argument("--user",     default="root@pam")
    parser.add_argument("--password", required=True)
    parser.add_argument("--node",     required=True, help="Nombre del nodo (ej. pve)")
    parser.add_argument("--interval", type=int, default=5)
    args = parser.parse_args()

    client = ProxmoxClient(args.host, args.user, args.password)
    client.login()
    monitor(client, args.node, args.interval)


if __name__ == "__main__":
    main()
