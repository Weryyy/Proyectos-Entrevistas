"""
Módulo 14 — Arch Linux Install
Descargador de ISO con verificación de checksum SHA256.

Obtiene la lista de mirrors de archlinux.org y descarga la ISO
oficial con barra de progreso, verificando la integridad del archivo.
"""

import hashlib
import os
import re
import urllib.request
import urllib.error
from pathlib import Path


# URL base de descargas de Arch Linux
ARCH_DOWNLOAD_PAGE = "https://archlinux.org/download/"
# URL del archivo de checksums SHA256 oficiales
ARCH_SHA256_URL = "https://archlinux.org/iso/latest/sha256sums.txt"

# Mirrors HTTP conocidos (fallback si no se puede acceder a la página de descargas)
MIRRORS_FALLBACK = [
    "https://mirror.rackspace.com/archlinux/iso/latest/",
    "https://mirrors.kernel.org/archlinux/iso/latest/",
    "https://mirror.leaseweb.net/archlinux/iso/latest/",
    "https://mirrors.ocf.berkeley.edu/archlinux/iso/latest/",
]


def obtener_mirrors_http(timeout: int = 10) -> list[str]:
    """
    Obtiene la lista de mirrors HTTP desde la página de descargas de Arch Linux.

    Returns:
        Lista de URLs de mirrors disponibles.
    """
    try:
        req = urllib.request.Request(
            ARCH_DOWNLOAD_PAGE,
            headers={"User-Agent": "Mozilla/5.0 (arch-install-script/1.0)"},
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            html = resp.read().decode("utf-8", errors="replace")

        # Extraer URLs de mirrors HTTP/HTTPS
        patron = r'href="(https?://[^"]+/archlinux/iso/latest/)"'
        mirrors = re.findall(patron, html)

        if not mirrors:
            # Intentar patrón alternativo
            patron2 = r'href="(https?://[^"]+iso/latest/)"'
            mirrors = re.findall(patron2, html)

        return mirrors if mirrors else MIRRORS_FALLBACK
    except Exception:
        return MIRRORS_FALLBACK


def obtener_nombre_iso(mirror_url: str, timeout: int = 10) -> str | None:
    """
    Busca el nombre del archivo ISO más reciente en un mirror.

    Args:
        mirror_url: URL base del mirror (ej. https://mirror.example.com/archlinux/iso/latest/).
        timeout: Tiempo límite de conexión en segundos.

    Returns:
        Nombre del archivo ISO (ej. archlinux-2024.01.01-x86_64.iso) o None.
    """
    try:
        req = urllib.request.Request(
            mirror_url,
            headers={"User-Agent": "Mozilla/5.0 (arch-install-script/1.0)"},
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            html = resp.read().decode("utf-8", errors="replace")

        patron = r'href="(archlinux-\d{4}\.\d{2}\.\d{2}-x86_64\.iso)"'
        match = re.search(patron, html)
        if match:
            return match.group(1)
    except Exception:
        pass
    return None


def obtener_checksums(timeout: int = 10) -> dict[str, str]:
    """
    Descarga y parsea el archivo SHA256SUMS oficial de Arch Linux.

    Returns:
        Diccionario {nombre_archivo: sha256_hex}.
    """
    checksums: dict[str, str] = {}
    try:
        req = urllib.request.Request(
            ARCH_SHA256_URL,
            headers={"User-Agent": "Mozilla/5.0 (arch-install-script/1.0)"},
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            contenido = resp.read().decode("utf-8", errors="replace")

        for linea in contenido.splitlines():
            partes = linea.strip().split(None, 1)
            if len(partes) == 2:
                sha256, nombre = partes
                # El nombre puede tener un asterisco al inicio (formato BSD sum)
                nombre = nombre.lstrip("*").strip()
                checksums[nombre] = sha256.lower()
    except Exception:
        pass
    return checksums


def verificar_checksum(ruta_archivo: Path, sha256_esperado: str) -> bool:
    """
    Verifica la integridad de un archivo usando SHA256.

    Args:
        ruta_archivo: Ruta al archivo a verificar.
        sha256_esperado: Hash SHA256 esperado (hexadecimal).

    Returns:
        True si el checksum coincide, False en caso contrario.
    """
    sha256 = hashlib.sha256()
    with open(ruta_archivo, "rb") as f:
        for bloque in iter(lambda: f.read(65536), b""):
            sha256.update(bloque)
    return sha256.hexdigest().lower() == sha256_esperado.lower()


def descargar_iso(
    url: str,
    destino: Path,
    mostrar_progreso: bool = True,
) -> None:
    """
    Descarga un archivo desde una URL con barra de progreso opcional.

    Args:
        url: URL del archivo a descargar.
        destino: Ruta completa donde guardar el archivo.
        mostrar_progreso: Si True, muestra el progreso de descarga.

    Raises:
        urllib.error.URLError: Si hay error de red.
        OSError: Si hay error de escritura en disco.
    """
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (arch-install-script/1.0)"},
    )

    with urllib.request.urlopen(req) as resp:
        tamaño_total = int(resp.headers.get("Content-Length", 0))
        descargado = 0
        tamaño_bloque = 65536  # 64 KB

        with open(destino, "wb") as f:
            while True:
                bloque = resp.read(tamaño_bloque)
                if not bloque:
                    break
                f.write(bloque)
                descargado += len(bloque)

                if mostrar_progreso and tamaño_total > 0:
                    porcentaje = descargado * 100 // tamaño_total
                    mb_descargado = descargado / 1_048_576
                    mb_total = tamaño_total / 1_048_576
                    barra = "█" * (porcentaje // 2) + "░" * (50 - porcentaje // 2)
                    print(
                        f"\r  [{barra}] {porcentaje:3d}% "
                        f"({mb_descargado:.1f}/{mb_total:.1f} MB)",
                        end="",
                        flush=True,
                    )

    if mostrar_progreso:
        print()  # Salto de línea al terminar


def descargar_iso_arch(
    directorio_destino: Path,
    mirror_url: str | None = None,
    mostrar_progreso: bool = True,
) -> Path | None:
    """
    Orquesta la descarga completa de la ISO de Arch Linux:
    1. Obtiene mirrors disponibles.
    2. Descubre el nombre del ISO más reciente.
    3. Descarga el ISO y verifica el checksum SHA256.

    Args:
        directorio_destino: Carpeta donde se guardará la ISO.
        mirror_url: URL de mirror específico. Si None, usa el primero disponible.
        mostrar_progreso: Si True, muestra barra de progreso.

    Returns:
        Ruta al archivo ISO descargado, o None si falló.
    """
    directorio_destino.mkdir(parents=True, exist_ok=True)

    # 1. Seleccionar mirror
    if mirror_url is None:
        mirrors = obtener_mirrors_http()
        mirror_url = mirrors[0] if mirrors else MIRRORS_FALLBACK[0]

    # 2. Obtener nombre del ISO
    nombre_iso = obtener_nombre_iso(mirror_url)
    if nombre_iso is None:
        print("[ERROR] No se pudo determinar el nombre del ISO. Revisa tu conexión a Internet.")
        return None

    ruta_iso = directorio_destino / nombre_iso

    # Comprobar si ya existe
    if ruta_iso.exists():
        print(f"[INFO] El archivo ISO ya existe: {ruta_iso}")
        return ruta_iso

    # 3. Obtener checksums oficiales
    print("[INFO] Descargando checksums oficiales...")
    checksums = obtener_checksums()
    sha256_esperado = checksums.get(nombre_iso)

    # 4. Descargar
    url_iso = mirror_url.rstrip("/") + "/" + nombre_iso
    print(f"[INFO] Descargando: {url_iso}")
    print(f"[INFO] Destino:     {ruta_iso}")

    try:
        descargar_iso(url_iso, ruta_iso, mostrar_progreso=mostrar_progreso)
    except Exception as e:
        print(f"\n[ERROR] Falló la descarga: {e}")
        if ruta_iso.exists():
            os.remove(ruta_iso)
        return None

    # 5. Verificar checksum
    if sha256_esperado:
        print("[INFO] Verificando integridad del archivo...")
        if verificar_checksum(ruta_iso, sha256_esperado):
            print("[OK] Checksum SHA256 verificado correctamente.")
        else:
            print("[ERROR] El checksum SHA256 no coincide. El archivo puede estar corrupto.")
            os.remove(ruta_iso)
            return None
    else:
        print("[AVISO] No se encontró el checksum para este archivo. Verifica manualmente.")

    return ruta_iso
