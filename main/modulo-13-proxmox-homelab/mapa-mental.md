# 🗺️ Mapa Mental — Módulo 13: Proxmox & Homelab

```
PROXMOX & HOMELAB
│
├── 🏗️ PREREQUISITOS
│   ├── Redes básicas (TCP/IP, VLANs, subnets)
│   ├── Virtualización (KVM, LXC, diferencias VM vs contenedor)
│   ├── Linux CLI (ssh, systemctl, ip, lvs)
│   └── Python intermedio (requests, json, clases)
│
├── 📐 CONCEPTOS CLAVE
│   ├── Proxmox VE
│   │   ├── Nodo (node) — servidor físico con Proxmox
│   │   ├── VM (KVM) — máquina virtual completa
│   │   ├── LXC — contenedor Linux ligero
│   │   ├── Pool — agrupación lógica de recursos
│   │   └── Storage — discos, ZFS, NFS, CEPH
│   ├── API REST Proxmox
│   │   ├── Autenticación: ticket + CSRF token
│   │   ├── Endpoints: /nodes, /cluster, /access
│   │   └── proxmoxer — wrapper Python oficial
│   └── Automatización
│       ├── Infraestructura como Código (IaC)
│       ├── Terraform provider Proxmox
│       └── Ansible playbooks para VMs
│
├── 🛤️ CAMINO DE APRENDIZAJE
│   ├── 1. Instalar Proxmox en VM nested o bare-metal
│   ├── 2. Explorar interfaz web (puerto 8006)
│   ├── 3. Crear primera VM o LXC manualmente
│   ├── 4. Usar API REST con curl
│   ├── 5. Automatizar con Python (proxmoxer)
│   └── 6. Scripts Bash para tareas recurrentes
│
└── 🔭 SIGUIENTES PASOS
    ├── Cluster de alta disponibilidad (HA)
    ├── Ceph para almacenamiento distribuido
    ├── Terraform + Proxmox provider
    └── Monitoreo con Prometheus + Grafana
```
