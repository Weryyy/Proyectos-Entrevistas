#!/usr/bin/env python3
import http.server
import socketserver
import socket
import os

PORT = 8080
DIRECTORY = os.path.dirname(os.path.abspath(__file__))


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # no importa si la IP es alcanzable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


print(f"--- Servidor de Despliegue Local (Módulo 14) ---")
print(f"IP de este equipo: {get_ip()}")
print(f"Puerto: {PORT}")
print(f"Serviendo archivos desde: {DIRECTORY}")
print("-" * 45)
print(f"COMANDO PARA LA VM ARCH:")
print(f"curl -L {get_ip()}:{PORT}/auto_install_hyprland.sh | bash")
print("-" * 45)

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido.")
