#!/usr/bin/env python3
"""
Módulo 14 — Arch Linux Install
Script interactivo para guiar la instalación de Arch Linux paso a paso,
siguiendo la guía oficial: https://wiki.archlinux.org/title/Installation_guide

Funcionalidades:
  1. Descarga la ISO más reciente desde los mirrors oficiales.
  2. Genera un script de VirtualBox listo para crear la VM.
  3. Genera una configuración para archinstall (instalador oficial).
  4. Documenta todos los pasos del proceso de instalación.

Uso:
    python arch_install.py
    python arch_install.py --no-descarga    # Omite la descarga real de la ISO
    python arch_install.py --ayuda
"""

import argparse
import os
import sys
from pathlib import Path

from iso_downloader import obtener_mirrors_http, descargar_iso_arch
from vbox_setup import ConfigVM, generar_script_vbox, generar_config_archinstall


# ─────────────────────────────────────────────────────────────────────────────
# Utilidades de consola
# ─────────────────────────────────────────────────────────────────────────────

SEPARADOR = "=" * 60


def titular(texto: str) -> None:
    """Imprime un título formateado."""
    print(f"\n{SEPARADOR}")
    print(f"  {texto}")
    print(SEPARADOR)


def paso(numero: int, texto: str) -> None:
    """Imprime un paso numerado."""
    print(f"\n[Paso {numero}] {texto}")
    print("-" * 40)


def preguntar(mensaje: str, por_defecto: str = "") -> str:
    """
    Solicita input al usuario con un valor por defecto.

    Args:
        mensaje: Texto del prompt.
        por_defecto: Valor si el usuario pulsa Enter sin escribir nada.

    Returns:
        Respuesta del usuario (nunca vacía: usa por_defecto si es necesario).
    """
    sufijo = f" [{por_defecto}]" if por_defecto else ""
    respuesta = input(f"  {mensaje}{sufijo}: ").strip()
    return respuesta if respuesta else por_defecto


def preguntar_si_no(mensaje: str, por_defecto: bool = True) -> bool:
    """Pregunta Sí/No al usuario."""
    opciones = "S/n" if por_defecto else "s/N"
    while True:
        respuesta = input(f"  {mensaje} [{opciones}]: ").strip().lower()
        if not respuesta:
            return por_defecto
        if respuesta in ("s", "si", "sí", "y", "yes"):
            return True
        if respuesta in ("n", "no"):
            return False
        print("  Por favor responde 's' o 'n'.")


def preguntar_numero(mensaje: str, por_defecto: int, minimo: int = 1, maximo: int = 999_999) -> int:
    """Solicita un número entero dentro de un rango."""
    while True:
        entrada = preguntar(mensaje, str(por_defecto))
        try:
            valor = int(entrada)
            if minimo <= valor <= maximo:
                return valor
            print(f"  El valor debe estar entre {minimo} y {maximo}.")
        except ValueError:
            print("  Por favor introduce un número entero.")


def seleccionar_opcion(titulo: str, opciones: list[str], por_defecto: int = 0) -> int:
    """
    Muestra un menú numerado y devuelve el índice seleccionado.

    Args:
        titulo: Encabezado del menú.
        opciones: Lista de opciones a mostrar.
        por_defecto: Índice de la opción por defecto (base 0).

    Returns:
        Índice seleccionado (base 0).
    """
    print(f"\n  {titulo}")
    for i, opcion in enumerate(opciones):
        marca = " (por defecto)" if i == por_defecto else ""
        print(f"    {i + 1}) {opcion}{marca}")
    while True:
        entrada = preguntar("Selecciona una opción", str(por_defecto + 1))
        try:
            idx = int(entrada) - 1
            if 0 <= idx < len(opciones):
                return idx
            print(f"  Introduce un número entre 1 y {len(opciones)}.")
        except ValueError:
            print("  Por favor introduce un número.")


# ─────────────────────────────────────────────────────────────────────────────
# Pasos del asistente
# ─────────────────────────────────────────────────────────────────────────────

def paso_proposito() -> dict:
    """Paso 1: Preguntar el propósito de la instalación."""
    paso(1, "¿Para qué quieres instalar Arch Linux?")
    print(
        "  Este script sigue la Guía de Instalación oficial:\n"
        "  https://wiki.archlinux.org/title/Installation_guide\n"
        "  y descarga la ISO desde:\n"
        "  https://archlinux.org/download/#http-downloads"
    )

    propositos = [
        "Máquina Virtual con Oracle VirtualBox (recomendado para empezar)",
        "Máquina Virtual con QEMU/KVM",
        "Instalación en hardware real (bare-metal)",
        "Solo quiero la ISO para más adelante",
    ]
    idx = seleccionar_opcion("Selecciona el propósito:", propositos)
    return {"proposito_idx": idx, "proposito": propositos[idx]}


def paso_directorio() -> Path:
    """Paso 2: Preguntar dónde guardar los archivos generados."""
    paso(2, "¿Dónde quieres guardar los archivos? (ISO, scripts, configs)")
    directorio_por_defecto = str(Path.home() / "arch-install")
    entrada = preguntar("Directorio de destino", directorio_por_defecto)
    ruta = Path(entrada).expanduser().resolve()
    ruta.mkdir(parents=True, exist_ok=True)
    print(f"  [OK] Directorio: {ruta}")
    return ruta


def paso_config_arch() -> dict:
    """Paso 3: Recopilar configuración del sistema Arch Linux a instalar."""
    paso(3, "Configuración del sistema Arch Linux")

    print("  Estos valores se usarán para el sistema instalado dentro de la VM.\n")

    hostname = preguntar("Nombre del equipo (hostname)", "archvm")
    username = preguntar("Nombre de usuario", "arch")

    while True:
        password = input("  Contraseña (no se muestra): ")
        if len(password) >= 6:
            break
        print("  La contraseña debe tener al menos 6 caracteres.")

    # Zona horaria
    zonas = [
        "Europe/Madrid",
        "America/New_York",
        "America/Mexico_City",
        "America/Argentina/Buenos_Aires",
        "America/Santiago",
        "America/Bogota",
        "UTC",
    ]
    idx_zona = seleccionar_opcion("Zona horaria:", zonas)
    timezone = zonas[idx_zona]
    if timezone == "UTC":
        timezone = preguntar("Escribe tu zona horaria (ej. Europe/Madrid)", "UTC")

    # Locale / idioma
    locales = [
        "es_ES.UTF-8",
        "es_MX.UTF-8",
        "es_AR.UTF-8",
        "es_CL.UTF-8",
        "en_US.UTF-8",
    ]
    idx_locale = seleccionar_opcion("Idioma del sistema:", locales)
    locale = locales[idx_locale]

    # Kernel
    kernels = ["linux (estable)", "linux-lts (soporte extendido)", "linux-zen (rendimiento)"]
    idx_kernel = seleccionar_opcion("Kernel de Linux:", kernels)
    kernel = kernels[idx_kernel].split(" ")[0]

    # Perfil de instalación
    perfiles = [
        "minimal (sin entorno gráfico, solo terminal)",
        "desktop (entorno gráfico completo)",
    ]
    idx_perfil = seleccionar_opcion("Perfil de instalación:", perfiles)
    perfil = perfiles[idx_perfil].split(" ")[0]

    return {
        "hostname": hostname,
        "username": username,
        "password": password,
        "timezone": timezone,
        "locale": locale,
        "kernel": kernel,
        "perfil": perfil,
    }


def paso_config_vm(directorio: Path) -> ConfigVM:
    """Paso 4: Configurar la máquina virtual de VirtualBox."""
    paso(4, "Configuración de la Máquina Virtual (VirtualBox)")

    nombre = preguntar("Nombre de la VM", "ArchLinux")
    ram = preguntar_numero("RAM en MB (mínimo recomendado: 1024)", 2048, minimo=512, maximo=65536)
    cpus = preguntar_numero("Número de CPUs virtuales", 2, minimo=1, maximo=32)
    disco = preguntar_numero("Tamaño del disco duro virtual en GB (mínimo: 15)", 20, minimo=15, maximo=2048)

    firmwares = ["EFI (recomendado para sistemas modernos)", "BIOS (compatibilidad con sistemas antiguos)"]
    idx_fw = seleccionar_opcion("Tipo de firmware:", firmwares)
    firmware = "EFI" if idx_fw == 0 else "BIOS"

    redes = ["NAT (acceso a internet, sin acceso desde la red local)", "Bridged (como un equipo más en la red)", "Host-only (solo comunicación con el host)"]
    idx_red = seleccionar_opcion("Tipo de red:", redes)
    red = ["NAT", "Bridged", "Host-only"][idx_red]

    return ConfigVM(
        nombre=nombre,
        ram_mb=ram,
        vram_mb=128,
        cpus=cpus,
        disco_gb=disco,
        tipo_firmware=firmware,
        directorio_vm=directorio / "VMs",
        red=red,
    )


def paso_seleccionar_mirror() -> str | None:
    """Paso 5: Seleccionar mirror de descarga."""
    paso(5, "Selección de mirror para descargar la ISO")
    print("  Obteniendo lista de mirrors disponibles...")

    mirrors = obtener_mirrors_http()
    if not mirrors:
        print("  [AVISO] No se pudieron obtener mirrors automáticamente.")
        return None

    # Mostrar solo los primeros 10 mirrors para no saturar la pantalla
    mirrors_mostrados = mirrors[:10]
    idx = seleccionar_opcion(
        "Selecciona el mirror de descarga:",
        mirrors_mostrados,
        por_defecto=0,
    )
    return mirrors_mostrados[idx]


def paso_descargar_iso(directorio: Path, mirror_url: str | None, descargar: bool) -> Path | None:
    """Paso 6: Descargar la ISO de Arch Linux."""
    paso(6, "Descarga de la ISO de Arch Linux")
    dir_iso = directorio / "iso"

    if not descargar:
        print("  [OMITIDO] Descarga desactivada con --no-descarga.")
        print(f"  Para descargar manualmente visita: https://archlinux.org/download/")
        return None

    confirmacion = preguntar_si_no(
        f"¿Descargar la ISO en '{dir_iso}'?",
        por_defecto=True,
    )
    if not confirmacion:
        print("  [OMITIDO] Descarga cancelada por el usuario.")
        return None

    return descargar_iso_arch(dir_iso, mirror_url=mirror_url)


def paso_generar_archivos(
    directorio: Path,
    config_vm: ConfigVM,
    config_arch: dict,
    iso_path: Path | None,
) -> None:
    """Paso 7: Generar los archivos de configuración y scripts."""
    paso(7, "Generando archivos de configuración")

    # Actualizar la ruta del ISO en la configuración de la VM
    if iso_path:
        config_vm.iso_path = iso_path

    # Script de VirtualBox
    ruta_script_vbox = directorio / "crear_vm_vbox.sh"
    contenido_vbox = generar_script_vbox(config_vm)
    ruta_script_vbox.write_text(contenido_vbox, encoding="utf-8")
    try:
        ruta_script_vbox.chmod(0o755)
    except OSError:
        pass
    print(f"  [OK] Script VirtualBox:    {ruta_script_vbox}")

    # Configuración de archinstall
    ruta_config_arch = directorio / "archinstall_config.json"
    contenido_arch = generar_config_archinstall(config_vm, config_arch)
    ruta_config_arch.write_text(contenido_arch, encoding="utf-8")
    print(f"  [OK] Config archinstall:   {ruta_config_arch}")


def mostrar_pasos_instalacion(config_arch: dict, firmware: str) -> None:
    """Paso 8: Mostrar los pasos de instalación de la guía oficial."""
    paso(8, "Pasos de instalación (Guía Oficial Arch Linux)")

    pasos = [
        ("Arrancar desde la ISO",
         "Inicia la VM con la ISO montada. Verás el prompt de root."),
        ("Verificar modo de arranque",
         f"Ejecuta: ls /sys/firmware/efi/efivars\n"
         f"    {'Si muestra archivos → modo EFI ✓ (coincide con la configuración de la VM)' if firmware == 'EFI' else 'Si NO muestra archivos → modo BIOS ✓ (coincide con la configuración de la VM)'}"),
        ("Conectar a internet",
         "En VirtualBox con NAT ya tienes conexión automática.\n"
         "    Verifica con: ping -c 3 archlinux.org"),
        ("Sincronizar el reloj",
         "Ejecuta: timedatectl set-ntp true"),
        ("Particionar el disco",
         "Usa archinstall (recomendado) o fdisk/cfdisk manualmente.\n"
         "    archinstall detecta automáticamente el disco."),
        ("Instalación con archinstall (recomendado)",
         f"Ejecuta: archinstall\n"
         f"    O usa la config generada: archinstall --config archinstall_config.json\n"
         f"    Kernel seleccionado: {config_arch.get('kernel', 'linux')}\n"
         f"    Hostname: {config_arch.get('hostname', 'archvm')}\n"
         f"    Usuario: {config_arch.get('username', 'arch')}\n"
         f"    Timezone: {config_arch.get('timezone', 'UTC')}\n"
         f"    Locale: {config_arch.get('locale', 'es_ES.UTF-8')}"),
        ("Instalación manual (alternativa)",
         "1. Formatear: mkfs.ext4 /dev/sda2\n"
         "    2. Montar: mount /dev/sda2 /mnt\n"
         "    3. Instalar base: pacstrap /mnt base linux linux-firmware\n"
         "    4. fstab: genfstab -U /mnt >> /mnt/etc/fstab\n"
         "    5. Chroot: arch-chroot /mnt\n"
         "    6. Configurar timezone, locale, hostname, contraseña\n"
         "    7. Instalar GRUB: pacman -S grub && grub-install && grub-mkconfig"),
        ("Reiniciar",
         "Desmonta: umount -R /mnt\n"
         "    Reinicia: reboot\n"
         "    Retira la ISO del lector virtual en VirtualBox."),
    ]

    for i, (titulo_paso, descripcion) in enumerate(pasos, 1):
        print(f"\n  {i}. {titulo_paso}")
        for linea in descripcion.splitlines():
            print(f"     {linea}")


def mostrar_resumen(directorio: Path, iso_path: Path | None, config_arch: dict) -> None:
    """Muestra el resumen final del proceso."""
    titular("✅ Proceso completado — Resumen")

    print(f"\n  Directorio de trabajo: {directorio}")

    if iso_path:
        tamaño_mb = iso_path.stat().st_size / 1_048_576
        print(f"  ISO descargada:        {iso_path} ({tamaño_mb:.0f} MB)")
    else:
        print("  ISO:                   No descargada (hazlo desde https://archlinux.org/download/)")

    print(f"  Script VirtualBox:     {directorio / 'crear_vm_vbox.sh'}")
    print(f"  Config archinstall:    {directorio / 'archinstall_config.json'}")

    print(f"\n  Próximos pasos:")
    print(f"    1. Ejecuta el script de VirtualBox para crear la VM:")
    print(f"       bash {directorio / 'crear_vm_vbox.sh'}")
    print(f"    2. Inicia la VM en VirtualBox.")
    print(f"    3. Sigue los pasos de instalación mostrados arriba.")
    print(f"    4. Lee la guía completa en: https://wiki.archlinux.org/title/Installation_guide")


# ─────────────────────────────────────────────────────────────────────────────
# Punto de entrada
# ─────────────────────────────────────────────────────────────────────────────

def parsear_argumentos() -> argparse.Namespace:
    """Parsea los argumentos de línea de comandos."""
    parser = argparse.ArgumentParser(
        description="Asistente interactivo de instalación de Arch Linux",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Ejemplos:\n"
            "  python arch_install.py                 # Asistente completo\n"
            "  python arch_install.py --no-descarga   # Sin descargar la ISO\n"
        ),
    )
    parser.add_argument(
        "--no-descarga",
        action="store_true",
        help="Omitir la descarga de la ISO (solo generar scripts y configs)",
    )
    return parser.parse_args()


def main() -> int:
    """Función principal del asistente interactivo."""
    args = parsear_argumentos()

    titular("🐧 Asistente de Instalación de Arch Linux")
    print(
        "\n  Guía oficial: https://wiki.archlinux.org/title/Installation_guide\n"
        "  Descargas:    https://archlinux.org/download/#http-downloads\n"
        "\n  Este asistente te guiará por todos los pasos necesarios para\n"
        "  instalar Arch Linux, especialmente para una VM con VirtualBox."
    )

    try:
        # Paso 1: Propósito
        info_proposito = paso_proposito()

        # Paso 2: Directorio destino
        directorio = paso_directorio()

        # Paso 3: Configuración del sistema Arch
        config_arch = paso_config_arch()

        # Paso 4: Configuración de la VM (solo si es VirtualBox)
        config_vm: ConfigVM | None = None
        if info_proposito["proposito_idx"] == 0:
            config_vm = paso_config_vm(directorio)
        else:
            # Para otros propósitos, usar configuración por defecto
            config_vm = ConfigVM(
                nombre=config_arch["hostname"],
                directorio_vm=directorio / "VMs",
            )

        # Paso 5: Seleccionar mirror
        mirror_url = paso_seleccionar_mirror()

        # Paso 6: Descargar ISO
        iso_path = paso_descargar_iso(
            directorio,
            mirror_url=mirror_url,
            descargar=not args.no_descarga,
        )

        # Paso 7: Generar archivos de configuración
        paso_generar_archivos(directorio, config_vm, config_arch, iso_path)

        # Paso 8: Mostrar pasos de instalación
        mostrar_pasos_instalacion(config_arch, config_vm.tipo_firmware)

        # Resumen final
        mostrar_resumen(directorio, iso_path, config_arch)

    except KeyboardInterrupt:
        print("\n\n  [INFO] Asistente cancelado por el usuario.")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
