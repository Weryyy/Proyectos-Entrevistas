# Módulo 13: El Laboratorio Virtual — Proxmox & Homelab

## 🧠 Concepto Técnico

Un **Homelab** es un entorno de servidores doméstico donde se aprende virtualización,
redes y automatización. **Proxmox VE** (Virtual Environment) es la plataforma de
virtualización de código abierto más popular para homelabs: permite crear máquinas
virtuales (KVM) y contenedores (LXC) desde una interfaz web o API REST.

Inspirado en el canal de **Ardens** y su serie de Homelab con Proxmox:
[Proxmox Homelab Series](https://www.youtube.com/@ardens_dev)

---

## 🎯 Objetivos

1. Entender la arquitectura de Proxmox VE (nodos, pools, VMs, LXC)
2. Interactuar con la API REST de Proxmox desde Python
3. Automatizar tareas de gestión (crear VM, listar nodos, snapshots)
4. Escribir scripts Bash para administración de Homelab
5. Monitorear recursos del homelab con Python

---

## 📁 Estructura

```
modulo-13-proxmox-homelab/
├── README.md
├── mapa-mental.md
├── notebook.ipynb          # Tutor interactivo
└── codigo/
    ├── python/
    │   ├── proxmox_client.py       # Cliente API Proxmox
    │   ├── homelab_monitor.py      # Monitor de recursos
    │   └── test_proxmox.py         # Tests unitarios (mock)
    └── bash/
        ├── setup_lxc.sh            # Script para crear contenedor LXC
        └── backup_vm.sh            # Script de backup de VMs
```

---

## 🚀 Ejecución

```bash
# Tests unitarios (sin Proxmox real, usando mocks)
cd codigo/python && pytest test_proxmox.py -v

# Cliente interactivo (requiere Proxmox real)
python codigo/python/proxmox_client.py --help
```

---

## 📚 Recursos

- [Documentación Proxmox VE](https://pve.proxmox.com/pve-docs/)
- [API REST Proxmox](https://pve.proxmox.com/pve-docs/api-viewer/)
- [proxmoxer — librería Python](https://github.com/proxmoxer/proxmoxer)
- [Ardens — Homelab Series](https://www.youtube.com/@ardens_dev)
