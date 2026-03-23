"""
Módulo 14 — Arch Linux Install
Generador de configuración y comandos para Oracle VirtualBox.

Produce el script de VBoxManage que crea y configura una VM lista
para instalar Arch Linux desde la ISO descargada.
"""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ConfigVM:
    """Parámetros de configuración para la máquina virtual de VirtualBox."""

    nombre: str = "ArchLinux"
    ram_mb: int = 2048            # Memoria RAM en MB
    vram_mb: int = 128            # Memoria de vídeo en MB
    cpus: int = 2                 # Número de CPUs virtuales
    disco_gb: int = 20            # Tamaño del disco duro virtual en GB
    tipo_firmware: str = "EFI"    # "BIOS" o "EFI"
    iso_path: Path = field(default_factory=Path)
    directorio_vm: Path = field(default_factory=Path)
    red: str = "NAT"              # "NAT", "Bridged" o "Host-only"
    audio: bool = False           # Habilitar audio
    carpeta_compartida: str = ""  # Carpeta compartida host→guest (opcional)


def generar_script_vbox(config: ConfigVM) -> str:
    """
    Genera el script de shell con comandos VBoxManage para crear la VM.

    El script crea:
      1. La VM con los parámetros dados.
      2. Un disco duro virtual (VDI).
      3. La unidad óptica con la ISO adjuntada.
      4. La configuración de red, vídeo y CPU.

    Args:
        config: Configuración de la máquina virtual.

    Returns:
        Contenido del script de shell (bash) como string.
    """
    iso_abs = str(config.iso_path.resolve()
                  ) if config.iso_path != Path() else "/ruta/al/archlinux.iso"
    vm_dir = str(config.directorio_vm.resolve()
                 ) if config.directorio_vm != Path() else "$HOME/VirtualBox VMs"
    disco_path = f"{vm_dir}/{config.nombre}/{config.nombre}.vdi"

    firmware_flag = "--firmware efi" if config.tipo_firmware == "EFI" else "--firmware bios"
    lineas_audio = (
        [f'VBoxManage modifyvm "{config.nombre}" --audio-driver default --audio-enabled on']
        if config.audio
        else [f'VBoxManage modifyvm "{config.nombre}" --audio-enabled off']
    )
    lineas_carpeta = []
    if config.carpeta_compartida:
        lineas_carpeta = [
            f'VBoxManage sharedfolder add "{config.nombre}" '
            f'--name "compartido" --hostpath "{config.carpeta_compartida}" --automount'
        ]

    lineas = [
        "#!/usr/bin/env bash",
        "# Script generado automáticamente por arch_install.py",
        "# Crea una VM de Arch Linux en Oracle VirtualBox",
        "",
        "set -e",
        "",
        "# ── 1. Crear la máquina virtual ──────────────────────────────────",
        f'VBoxManage createvm \\',
        f'    --name "{config.nombre}" \\',
        f'    --ostype "ArchLinux_64" \\',
        f'    --basefolder "{vm_dir}" \\',
        f'    --register',
        "",
        "# ── 2. Configurar parámetros de hardware ─────────────────────────",
        f'VBoxManage modifyvm "{config.nombre}" \\',
        f'    --memory {config.ram_mb} \\',
        f'    --vram {config.vram_mb} \\',
        f'    --cpus {config.cpus} \\',
        f'    {firmware_flag} \\',
        f'    --graphicscontroller vmsvga \\',
        f'    --boot1 disk --boot2 dvd --boot3 none',
        "",
        "# ── 3. Crear disco duro virtual ──────────────────────────────────",
        f'VBoxManage createmedium disk \\',
        f'    --filename "{disco_path}" \\',
        f'    --size {config.disco_gb * 1024} \\',
        f'    --format VDI',
        "",
        "# ── 4. Agregar controladores de almacenamiento ───────────────────",
        f'VBoxManage storagectl "{config.nombre}" \\',
        f'    --name "SATA Controller" --add sata --controller IntelAhci',
        "",
        f'VBoxManage storageattach "{config.nombre}" \\',
        f'    --storagectl "SATA Controller" --port 0 --device 0 \\',
        f'    --type hdd --medium "{disco_path}"',
        "",
        "# Usamos IDE Controller para la ISO, máxima compatibilidad (PIIX4)",
        f'VBoxManage storagectl "{config.nombre}" \\',
        f'    --name "IDE Controller" --add ide --controller PIIX4',
        "",
        f'VBoxManage storageattach "{config.nombre}" \\',
        f'    --storagectl "IDE Controller" --port 0 --device 0 \\',
        f'    --type dvddrive --medium "{iso_abs}"',
        "",
        "# ── 5. Configurar red ────────────────────────────────────────────",
        f'VBoxManage modifyvm "{config.nombre}" --nic1 {config.red.lower()}',
        "",
        "# ── 6. Audio ─────────────────────────────────────────────────────",
        *lineas_audio,
        "",
    ]

    if lineas_carpeta:
        lineas += [
            "# ── 7. Carpeta compartida ────────────────────────────────────────",
            *lineas_carpeta,
            "",
        ]

    lineas += [
        "echo '=================================================='",
        f"echo '  VM \"{config.nombre}\" creada correctamente.'",
        "echo '  Inicia la VM con:'",
        f'echo \'  VBoxManage startvm "{config.nombre}" --type gui\'',
        "echo '=================================================='",
    ]

    return "\n".join(lineas) + "\n"


def generar_config_archinstall(config_vm: ConfigVM, config_arch: dict) -> str:
    """
    Genera un archivo JSON de configuración para archinstall
    (el instalador oficial de Arch Linux en Python).

    Args:
        config_vm: Configuración de la VM (se usa el nombre como hostname).
        config_arch: Diccionario con parámetros de instalación Arch:
            - hostname (str)
            - username (str)
            - password (str)
            - timezone (str)  ej. "Europe/Madrid"
            - locale (str)    ej. "es_ES.UTF-8"
            - kernel (str)    ej. "linux" o "linux-lts"
            - perfil (str)    ej. "minimal", "desktop"

    Returns:
        Contenido JSON del archivo de configuración para archinstall.
    """
    import json

    hostname = config_arch.get(
        "hostname", config_vm.nombre.lower().replace(" ", "-"))
    config = {
        "additional-repositories": [],
        "audio": "pipewire" if config_arch.get("perfil") == "desktop" else None,
        "bootloader": "grub",
        "config_version": "2.6.0",
        "debug": False,
        "disk_config": {
            "config_type": "default_layout",
            "device_modifications": []
        },
        "disk_encryption": None,
        "hostname": hostname,
        "kernels": [config_arch.get("kernel", "linux")],
        "locale_config": {
            "kb_layout": config_arch.get("locale", "es_ES.UTF-8").split(".")[0][-2:].lower(),
            "sys_enc": config_arch.get("locale", "es_ES.UTF-8").split(".")[-1],
            "sys_lang": config_arch.get("locale", "es_ES.UTF-8"),
        },
        "mirror_config": {
            "custom_mirrors": [],
            "mirror_regions": {"Spain": None}
        },
        "network_config": {
            "nics": [],
            "type": "nm"
        },
        "no_pkg_lookups": False,
        "ntp": True,
        "packages": [],
        # Clave con espacio: formato requerido por el esquema de archinstall
        "parallel downloads": 1,
        "profile_config": {
            "main_profile": config_arch.get("perfil", "minimal"),
            "sub_profiles": [],
        },
        "swap": True,
        "timezone": config_arch.get("timezone", "UTC"),
        "user_config": {
            "sudo": "sudo",
            "users": [
                {
                    "username": config_arch.get("username", "archuser"),
                    "!password": config_arch.get("password", ""),
                    "groups": ["wheel"],
                    "sudo": True,
                }
            ],
        },
    }
    # Eliminar claves con valor None
    config = {k: v for k, v in config.items() if v is not None}
    return json.dumps(config, indent=2, ensure_ascii=False)
