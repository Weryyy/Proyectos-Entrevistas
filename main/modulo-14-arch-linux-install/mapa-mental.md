# 🗺️ Mapa Mental — Módulo 14: El Instalador de Arch Linux

```
ARCH LINUX INSTALL (Automatización)
│
├── 🏗️ PREREQUISITOS
│   ├── Python 3.11+ (urllib, hashlib, dataclasses, json)
│   ├── Linux básico (particiones, sistemas de archivos, bootloaders)
│   ├── Virtualización (concepto de VM, VirtualBox, imágenes ISO)
│   └── Redes básicas (HTTP/HTTPS, mirrors, checksums SHA256)
│
├── 📐 CONCEPTOS CLAVE
│   ├── Arch Linux
│   │   ├── Rolling release — siempre en la última versión estable
│   │   ├── Filosofía KISS (Keep It Simple, Stupid)
│   │   ├── Pacman — gestor de paquetes de Arch
│   │   ├── AUR — Arch User Repository (paquetes de la comunidad)
│   │   └── archinstall — instalador oficial en Python (desde 2021)
│   │
│   ├── Proceso de Instalación (Guía Oficial)
│   │   ├── 1. Descargar y verificar la ISO
│   │   ├── 2. Crear medio de arranque (USB o VM)
│   │   ├── 3. Arrancar el entorno live
│   │   ├── 4. Configurar red, reloj, particiones
│   │   ├── 5. pacstrap — instalar sistema base
│   │   ├── 6. Configurar fstab, chroot, locale, hostname
│   │   ├── 7. Instalar bootloader (GRUB)
│   │   └── 8. Reiniciar en el sistema instalado
│   │
│   ├── VirtualBox / VBoxManage
│   │   ├── VBoxManage createvm — crear máquina virtual
│   │   ├── VBoxManage modifyvm — configurar hardware virtual
│   │   ├── VBoxManage createmedium — crear disco VDI
│   │   ├── VBoxManage storageattach — conectar disco e ISO
│   │   ├── Firmware EFI vs BIOS
│   │   └── Tipos de red: NAT, Bridged, Host-only
│   │
│   └── Descarga Segura de ISO
│       ├── SHA256 — checksum de integridad
│       ├── Mirrors HTTP — servidores de distribución
│       ├── urllib — HTTP sin dependencias externas
│       └── hashlib — criptografía estándar de Python
│
├── 🛤️ CAMINO DE APRENDIZAJE
│   ├── 1. Leer la Guía de Instalación oficial (wiki.archlinux.org)
│   ├── 2. Instalar VirtualBox y entender VBoxManage
│   ├── 3. Ejecutar el asistente: python arch_install.py
│   ├── 4. Analizar los archivos generados (script VBox, config archinstall)
│   ├── 5. Crear la VM con el script generado
│   ├── 6. Arrancar la VM con la ISO y seguir los pasos documentados
│   ├── 7. Instalar Arch usando archinstall (modo guiado)
│   └── 8. Explorar instalación manual para entender cada paso
│
├── 🔧 MÓDULOS PYTHON
│   ├── arch_install.py — Asistente interactivo (CLI wizard)
│   │   ├── preguntar() — input con valor por defecto
│   │   ├── preguntar_si_no() — prompt booleano
│   │   ├── seleccionar_opcion() — menú numerado
│   │   └── paso_*() — cada paso del asistente
│   │
│   ├── iso_downloader.py — Descarga de ISO
│   │   ├── obtener_mirrors_http() — scraping de archlinux.org
│   │   ├── obtener_nombre_iso() — detección de versión más reciente
│   │   ├── obtener_checksums() — descarga sha256sums.txt oficial
│   │   ├── verificar_checksum() — validación SHA256 local
│   │   └── descargar_iso_arch() — orquestador completo
│   │
│   └── vbox_setup.py — Configuración VirtualBox
│       ├── ConfigVM — dataclass con parámetros de la VM
│       ├── generar_script_vbox() — genera script Bash con VBoxManage
│       └── generar_config_archinstall() — genera JSON para archinstall
│
└── 🔭 SIGUIENTES PASOS
    ├── Personalizar el sistema instalado (dotfiles, rice)
    ├── Instalar entorno gráfico (Hyprland, GNOME, KDE) → ver Módulo 6
    ├── Crear snapshots de la VM en diferentes etapas
    ├── Automatizar con Ansible playbooks
    └── Explorar Proxmox para virtualización avanzada → ver Módulo 13
```
