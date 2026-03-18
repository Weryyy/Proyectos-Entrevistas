"""
Módulo 13 — Proxmox Homelab
Cliente Python para la API REST de Proxmox VE.

Uso:
    python proxmox_client.py --host 192.168.1.10 --user root@pam --password secret

Nota: para tests unitarios se usan mocks, no se necesita un Proxmox real.
"""

import json
import urllib.request
import urllib.parse
import ssl
import argparse
from typing import Any


class ProxmoxClient:
    """Cliente ligero para la API REST de Proxmox VE (sin dependencias externas)."""

    def __init__(self, host: str, user: str, password: str, port: int = 8006, verify_ssl: bool = False):
        self.base_url = f"https://{host}:{port}/api2/json"
        self.user = user
        self.password = password
        self.verify_ssl = verify_ssl
        self._ticket: str | None = None
        self._csrf_token: str | None = None
        # Contexto SSL: desactivar verificación en entornos de prueba
        self._ssl_ctx = ssl.create_default_context()
        if not verify_ssl:
            self._ssl_ctx.check_hostname = False
            self._ssl_ctx.verify_mode = ssl.CERT_NONE

    # ------------------------------------------------------------------
    # Autenticación
    # ------------------------------------------------------------------

    def login(self) -> dict[str, Any]:
        """Obtiene ticket de autenticación y token CSRF."""
        data = urllib.parse.urlencode({
            "username": self.user,
            "password": self.password,
        }).encode()
        req = urllib.request.Request(f"{self.base_url}/access/ticket", data=data, method="POST")
        with urllib.request.urlopen(req, context=self._ssl_ctx) as resp:
            result = json.loads(resp.read())["data"]
        self._ticket = result["ticket"]
        self._csrf_token = result["CSRFPreventionToken"]
        return result

    # ------------------------------------------------------------------
    # Métodos GET
    # ------------------------------------------------------------------

    def _get(self, path: str) -> Any:
        if not self._ticket:
            raise RuntimeError("No autenticado. Llama a login() primero.")
        url = f"{self.base_url}/{path.lstrip('/')}"
        req = urllib.request.Request(url)
        req.add_header("Cookie", f"PVEAuthCookie={self._ticket}")
        with urllib.request.urlopen(req, context=self._ssl_ctx) as resp:
            return json.loads(resp.read())["data"]

    def get_nodes(self) -> list[dict]:
        """Lista los nodos del cluster."""
        return self._get("/nodes")

    def get_vms(self, node: str) -> list[dict]:
        """Lista las VMs (KVM) de un nodo."""
        return self._get(f"/nodes/{node}/qemu")

    def get_containers(self, node: str) -> list[dict]:
        """Lista los contenedores LXC de un nodo."""
        return self._get(f"/nodes/{node}/lxc")

    def get_node_status(self, node: str) -> dict:
        """Devuelve el estado de recursos de un nodo (CPU, RAM, disco)."""
        return self._get(f"/nodes/{node}/status")

    def get_storage(self, node: str) -> list[dict]:
        """Lista los pools de almacenamiento de un nodo."""
        return self._get(f"/nodes/{node}/storage")

    # ------------------------------------------------------------------
    # Formateo de salida
    # ------------------------------------------------------------------

    @staticmethod
    def format_bytes(b: int) -> str:
        """Convierte bytes a formato legible."""
        for unit in ("B", "KB", "MB", "GB", "TB"):
            if b < 1024:
                return f"{b:.1f} {unit}"
            b /= 1024
        return f"{b:.1f} PB"

    def print_summary(self, node: str) -> None:
        """Imprime un resumen del nodo en la consola."""
        status = self.get_node_status(node)
        vms = self.get_vms(node)
        containers = self.get_containers(node)

        cpu_pct = status.get("cpu", 0) * 100
        mem_used = status.get("memory", {}).get("used", 0)
        mem_total = status.get("memory", {}).get("total", 1)
        mem_pct = mem_used / mem_total * 100

        print(f"\n{'='*50}")
        print(f"  Nodo: {node}")
        print(f"{'='*50}")
        print(f"  CPU:    {cpu_pct:.1f}%")
        print(f"  RAM:    {self.format_bytes(mem_used)} / {self.format_bytes(mem_total)} ({mem_pct:.1f}%)")
        print(f"  VMs:    {len(vms)}")
        print(f"  LXC:    {len(containers)}")
        print(f"{'='*50}\n")


# ------------------------------------------------------------------
# CLI
# ------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Cliente CLI para Proxmox VE")
    parser.add_argument("--host", required=True, help="IP/hostname del servidor Proxmox")
    parser.add_argument("--user", default="root@pam", help="Usuario (default: root@pam)")
    parser.add_argument("--password", required=True, help="Contraseña")
    parser.add_argument("--port", type=int, default=8006)
    args = parser.parse_args()

    client = ProxmoxClient(args.host, args.user, args.password, args.port)
    print("[INFO] Autenticando...")
    client.login()

    nodes = client.get_nodes()
    print(f"[OK] Conectado. Nodos detectados: {[n['node'] for n in nodes]}")

    for n in nodes:
        client.print_summary(n["node"])


if __name__ == "__main__":
    main()
