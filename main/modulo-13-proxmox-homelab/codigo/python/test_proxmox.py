"""
Tests unitarios del Módulo 13 — Proxmox Homelab.
Usa mocks para simular la API REST de Proxmox sin necesitar un servidor real.
"""

import json
import sys
import os
from unittest.mock import patch, MagicMock

# Añadir directorio actual al path
sys.path.insert(0, os.path.dirname(__file__))

from proxmox_client import ProxmoxClient


# ------------------------------------------------------------------
# Helpers de mock
# ------------------------------------------------------------------

def _make_response(data: object) -> MagicMock:
    """Crea un mock de urllib.request.urlopen con datos JSON."""
    mock_resp = MagicMock()
    mock_resp.read.return_value = json.dumps({"data": data}).encode()
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    return mock_resp


# ------------------------------------------------------------------
# Tests
# ------------------------------------------------------------------

def test_login_almacena_ticket():
    """login() guarda el ticket y el token CSRF."""
    payload = {
        "ticket": "PVE:root@pam:AABBCC==",
        "CSRFPreventionToken": "csrf-token-123",
        "username": "root@pam",
    }
    client = ProxmoxClient("192.168.1.10", "root@pam", "secret")
    with patch("urllib.request.urlopen", return_value=_make_response(payload)):
        result = client.login()

    assert result["ticket"] == "PVE:root@pam:AABBCC=="
    assert client._ticket == "PVE:root@pam:AABBCC=="
    assert client._csrf_token == "csrf-token-123"


def test_get_nodes_devuelve_lista():
    """get_nodes() retorna la lista de nodos."""
    nodes_data = [
        {"node": "pve1", "status": "online", "cpu": 0.05},
        {"node": "pve2", "status": "online", "cpu": 0.10},
    ]
    client = ProxmoxClient("192.168.1.10", "root@pam", "secret")
    client._ticket = "fake-ticket"

    with patch("urllib.request.urlopen", return_value=_make_response(nodes_data)):
        nodes = client.get_nodes()

    assert len(nodes) == 2
    assert nodes[0]["node"] == "pve1"
    assert nodes[1]["node"] == "pve2"


def test_get_vms_devuelve_lista():
    """get_vms() retorna las VMs de un nodo."""
    vms_data = [
        {"vmid": 100, "name": "ubuntu-server", "status": "running"},
        {"vmid": 101, "name": "debian-dev",    "status": "stopped"},
    ]
    client = ProxmoxClient("192.168.1.10", "root@pam", "secret")
    client._ticket = "fake-ticket"

    with patch("urllib.request.urlopen", return_value=_make_response(vms_data)):
        vms = client.get_vms("pve1")

    assert len(vms) == 2
    assert vms[0]["vmid"] == 100
    assert vms[1]["status"] == "stopped"


def test_get_containers_devuelve_lista():
    """get_containers() retorna los LXC de un nodo."""
    lxc_data = [
        {"vmid": 200, "name": "nginx-proxy", "status": "running"},
    ]
    client = ProxmoxClient("192.168.1.10", "root@pam", "secret")
    client._ticket = "fake-ticket"

    with patch("urllib.request.urlopen", return_value=_make_response(lxc_data)):
        containers = client.get_containers("pve1")

    assert len(containers) == 1
    assert containers[0]["name"] == "nginx-proxy"


def test_get_node_status():
    """get_node_status() retorna datos de uso de recursos."""
    status_data = {
        "cpu": 0.15,
        "memory": {"used": 4294967296, "total": 17179869184},
        "uptime": 86400,
    }
    client = ProxmoxClient("192.168.1.10", "root@pam", "secret")
    client._ticket = "fake-ticket"

    with patch("urllib.request.urlopen", return_value=_make_response(status_data)):
        status = client.get_node_status("pve1")

    assert status["cpu"] == 0.15
    assert status["memory"]["used"] == 4294967296


def test_format_bytes_bytes():
    assert ProxmoxClient.format_bytes(512) == "512.0 B"


def test_format_bytes_kb():
    assert ProxmoxClient.format_bytes(1024) == "1.0 KB"


def test_format_bytes_gb():
    assert ProxmoxClient.format_bytes(1024 ** 3) == "1.0 GB"


def test_get_sin_autenticar_lanza_error():
    """_get() lanza RuntimeError si no se ha llamado login()."""
    client = ProxmoxClient("192.168.1.10", "root@pam", "secret")
    try:
        client._get("/nodes")
        assert False, "Debería haber lanzado RuntimeError"
    except RuntimeError as e:
        assert "autenticado" in str(e).lower()


def test_url_base_construida_correctamente():
    """El base_url se forma con host y puerto correctamente."""
    client = ProxmoxClient("10.0.0.1", "root@pam", "x", port=8006)
    assert client.base_url == "https://10.0.0.1:8006/api2/json"
