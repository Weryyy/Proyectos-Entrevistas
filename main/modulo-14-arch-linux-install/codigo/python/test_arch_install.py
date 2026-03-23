"""
Tests para el Módulo 14 — Arch Linux Install

Pruebas unitarias para:
  - iso_downloader: parseo de checksums, verificación SHA256, URLs de mirrors
  - vbox_setup: generación de scripts VBoxManage y config archinstall
  - arch_install: funciones auxiliares del asistente interactivo
"""

import hashlib
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Asegurar que podemos importar los módulos del mismo directorio
sys.path.insert(0, str(Path(__file__).parent))

from iso_downloader import (
    MIRRORS_FALLBACK,
    obtener_checksums,
    obtener_mirrors_http,
    verificar_checksum,
)
from vbox_setup import (
    ConfigVM,
    generar_config_archinstall,
    generar_script_vbox,
)


# ─────────────────────────────────────────────────────────────────────────────
# Tests de iso_downloader
# ─────────────────────────────────────────────────────────────────────────────


class TestVerificarChecksum(unittest.TestCase):
    """Tests para la función verificar_checksum."""

    def test_checksum_correcto(self):
        """Verifica que un archivo con checksum correcto pasa la validación."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            contenido = b"arch linux iso test data"
            f.write(contenido)
            ruta = Path(f.name)

        sha256_esperado = hashlib.sha256(contenido).hexdigest()

        try:
            self.assertTrue(verificar_checksum(ruta, sha256_esperado))
        finally:
            ruta.unlink()

    def test_checksum_incorrecto(self):
        """Verifica que un archivo con checksum incorrecto falla la validación."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"datos incorrectos")
            ruta = Path(f.name)

        sha256_incorrecto = "a" * 64  # Hash falso

        try:
            self.assertFalse(verificar_checksum(ruta, sha256_incorrecto))
        finally:
            ruta.unlink()

    def test_checksum_mayusculas_minusculas(self):
        """El checksum debe ser insensible a mayúsculas/minúsculas."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            contenido = b"test data"
            f.write(contenido)
            ruta = Path(f.name)

        sha256 = hashlib.sha256(contenido).hexdigest()

        try:
            self.assertTrue(verificar_checksum(ruta, sha256.upper()))
            self.assertTrue(verificar_checksum(ruta, sha256.lower()))
        finally:
            ruta.unlink()

    def test_checksum_archivo_vacio(self):
        """Verifica el checksum de un archivo vacío."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            ruta = Path(f.name)

        sha256_vacio = hashlib.sha256(b"").hexdigest()

        try:
            self.assertTrue(verificar_checksum(ruta, sha256_vacio))
        finally:
            ruta.unlink()


class TestObtenerChecksums(unittest.TestCase):
    """Tests para la función obtener_checksums."""

    def test_parseo_formato_estandar(self):
        """Parsea correctamente el formato estándar 'sha256  archivo'."""
        contenido_fake = (
            "abc123def456  archlinux-2024.01.01-x86_64.iso\n"
            "789abcdef012  archlinux-2024.01.01-x86_64.iso.sig\n"
        )
        mock_resp = MagicMock()
        mock_resp.read.return_value = contenido_fake.encode()
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_resp.headers = {}

        with patch("urllib.request.urlopen", return_value=mock_resp):
            checksums = obtener_checksums()

        self.assertIn("archlinux-2024.01.01-x86_64.iso", checksums)
        self.assertEqual(checksums["archlinux-2024.01.01-x86_64.iso"], "abc123def456")

    def test_parseo_formato_bsd(self):
        """Parsea correctamente el formato BSD 'sha256 *archivo'."""
        contenido_fake = "abc123def456 *archlinux-2024.01.01-x86_64.iso\n"
        mock_resp = MagicMock()
        mock_resp.read.return_value = contenido_fake.encode()
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)

        with patch("urllib.request.urlopen", return_value=mock_resp):
            checksums = obtener_checksums()

        self.assertIn("archlinux-2024.01.01-x86_64.iso", checksums)
        self.assertEqual(checksums["archlinux-2024.01.01-x86_64.iso"], "abc123def456")

    def test_error_de_red_devuelve_dict_vacio(self):
        """Si hay error de red, debe devolver un diccionario vacío."""
        with patch("urllib.request.urlopen", side_effect=Exception("sin red")):
            checksums = obtener_checksums()
        self.assertIsInstance(checksums, dict)
        self.assertEqual(len(checksums), 0)


class TestObtenerMirrorsHttp(unittest.TestCase):
    """Tests para la función obtener_mirrors_http."""

    def test_usa_fallback_si_falla_red(self):
        """Si falla la red, debe devolver la lista de mirrors de fallback."""
        with patch("urllib.request.urlopen", side_effect=Exception("sin red")):
            mirrors = obtener_mirrors_http()
        self.assertEqual(mirrors, MIRRORS_FALLBACK)
        self.assertGreater(len(mirrors), 0)

    def test_extrae_mirrors_de_html(self):
        """Extrae correctamente URLs de mirrors desde HTML de descarga."""
        html_fake = """
        <a href="https://mirror.rackspace.com/archlinux/iso/latest/">Rackspace</a>
        <a href="https://mirrors.kernel.org/archlinux/iso/latest/">Kernel.org</a>
        <a href="https://otro-sitio.com/notamirror">Ignorar esto</a>
        """.encode()

        mock_resp = MagicMock()
        mock_resp.read.return_value = html_fake
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)

        with patch("urllib.request.urlopen", return_value=mock_resp):
            mirrors = obtener_mirrors_http()

        self.assertIn("https://mirror.rackspace.com/archlinux/iso/latest/", mirrors)
        self.assertIn("https://mirrors.kernel.org/archlinux/iso/latest/", mirrors)
        # URLs que no son mirrors de Arch no deben incluirse
        self.assertNotIn("https://otro-sitio.com/notamirror", mirrors)


# ─────────────────────────────────────────────────────────────────────────────
# Tests de vbox_setup
# ─────────────────────────────────────────────────────────────────────────────


class TestGenerarScriptVbox(unittest.TestCase):
    """Tests para la función generar_script_vbox."""

    def setUp(self):
        self.config = ConfigVM(
            nombre="TestArch",
            ram_mb=2048,
            vram_mb=128,
            cpus=2,
            disco_gb=20,
            tipo_firmware="EFI",
            iso_path=Path("/tmp/archlinux.iso"),
            directorio_vm=Path("/tmp/vms"),
            red="NAT",
        )

    def test_script_contiene_nombre_vm(self):
        """El script debe contener el nombre de la VM."""
        script = generar_script_vbox(self.config)
        self.assertIn("TestArch", script)

    def test_script_contiene_ram(self):
        """El script debe incluir la cantidad de RAM especificada."""
        script = generar_script_vbox(self.config)
        self.assertIn("2048", script)

    def test_script_contiene_cpus(self):
        """El script debe incluir el número de CPUs."""
        script = generar_script_vbox(self.config)
        self.assertIn("--cpus 2", script)

    def test_script_contiene_firmware_efi(self):
        """El script debe usar firmware EFI cuando corresponde."""
        script = generar_script_vbox(self.config)
        self.assertIn("--firmware efi", script)

    def test_script_contiene_firmware_bios(self):
        """El script debe usar firmware BIOS cuando se configura así."""
        self.config.tipo_firmware = "BIOS"
        script = generar_script_vbox(self.config)
        self.assertIn("--firmware bios", script)

    def test_script_contiene_tamaño_disco(self):
        """El script debe incluir el tamaño del disco (en MB = GB * 1024)."""
        script = generar_script_vbox(self.config)
        self.assertIn(str(20 * 1024), script)  # 20 GB = 20480 MB

    def test_script_contiene_iso(self):
        """El script debe referenciar la ruta del ISO."""
        script = generar_script_vbox(self.config)
        self.assertIn("archlinux.iso", script)

    def test_script_es_bash(self):
        """El script debe comenzar con el shebang de bash."""
        script = generar_script_vbox(self.config)
        self.assertTrue(script.startswith("#!/usr/bin/env bash"))

    def test_script_red_nat(self):
        """El script debe configurar la red NAT."""
        script = generar_script_vbox(self.config)
        self.assertIn("nat", script.lower())

    def test_script_carpeta_compartida(self):
        """El script debe incluir carpeta compartida si se configura."""
        self.config.carpeta_compartida = "/home/usuario/compartido"
        script = generar_script_vbox(self.config)
        self.assertIn("sharedfolder", script)
        self.assertIn("/home/usuario/compartido", script)

    def test_script_sin_carpeta_compartida(self):
        """Sin carpeta compartida, el script no debe incluir sharedfolder."""
        script = generar_script_vbox(self.config)
        self.assertNotIn("sharedfolder", script)


class TestGenerarConfigArchinstall(unittest.TestCase):
    """Tests para la función generar_config_archinstall."""

    def setUp(self):
        self.config_vm = ConfigVM(nombre="TestArch")
        self.config_arch = {
            "hostname": "mi-arch",
            "username": "usuario",
            "password": "password123",
            "timezone": "Europe/Madrid",
            "locale": "es_ES.UTF-8",
            "kernel": "linux",
            "perfil": "minimal",
        }

    def test_genera_json_valido(self):
        """La función debe generar JSON válido."""
        resultado = generar_config_archinstall(self.config_vm, self.config_arch)
        config = json.loads(resultado)  # No debe lanzar excepción
        self.assertIsInstance(config, dict)

    def test_contiene_hostname(self):
        """La config debe incluir el hostname especificado."""
        resultado = generar_config_archinstall(self.config_vm, self.config_arch)
        config = json.loads(resultado)
        self.assertEqual(config["hostname"], "mi-arch")

    def test_contiene_timezone(self):
        """La config debe incluir la zona horaria."""
        resultado = generar_config_archinstall(self.config_vm, self.config_arch)
        config = json.loads(resultado)
        self.assertEqual(config["timezone"], "Europe/Madrid")

    def test_contiene_kernel(self):
        """La config debe incluir el kernel seleccionado."""
        resultado = generar_config_archinstall(self.config_vm, self.config_arch)
        config = json.loads(resultado)
        self.assertIn("linux", config["kernels"])

    def test_contiene_usuario(self):
        """La config debe incluir el usuario configurado."""
        resultado = generar_config_archinstall(self.config_vm, self.config_arch)
        config = json.loads(resultado)
        usuarios = config["user_config"]["users"]
        self.assertEqual(len(usuarios), 1)
        self.assertEqual(usuarios[0]["username"], "usuario")

    def test_hostname_por_defecto_desde_vm(self):
        """Si no hay hostname en config_arch, debe usar el nombre de la VM."""
        config_sin_hostname = {k: v for k, v in self.config_arch.items() if k != "hostname"}
        resultado = generar_config_archinstall(self.config_vm, config_sin_hostname)
        config = json.loads(resultado)
        self.assertIn(self.config_vm.nombre.lower(), config["hostname"])


# ─────────────────────────────────────────────────────────────────────────────
# Tests de arch_install (funciones auxiliares)
# ─────────────────────────────────────────────────────────────────────────────


class TestFuncionesAuxiliares(unittest.TestCase):
    """Tests para las funciones auxiliares del asistente interactivo."""

    def test_config_vm_valores_por_defecto(self):
        """ConfigVM debe tener valores por defecto razonables."""
        config = ConfigVM()
        self.assertEqual(config.ram_mb, 2048)
        self.assertEqual(config.cpus, 2)
        self.assertEqual(config.disco_gb, 20)
        self.assertEqual(config.tipo_firmware, "EFI")
        self.assertEqual(config.red, "NAT")

    def test_config_vm_personalizada(self):
        """ConfigVM debe aceptar valores personalizados."""
        config = ConfigVM(
            nombre="MiVM",
            ram_mb=4096,
            cpus=4,
            disco_gb=50,
            tipo_firmware="BIOS",
        )
        self.assertEqual(config.nombre, "MiVM")
        self.assertEqual(config.ram_mb, 4096)
        self.assertEqual(config.cpus, 4)
        self.assertEqual(config.disco_gb, 50)
        self.assertEqual(config.tipo_firmware, "BIOS")

    def test_mirrors_fallback_son_https(self):
        """Los mirrors de fallback deben ser URLs HTTPS válidas."""
        for mirror in MIRRORS_FALLBACK:
            self.assertTrue(
                mirror.startswith("https://"),
                f"Mirror no es HTTPS: {mirror}",
            )

    def test_mirrors_fallback_terminan_en_barra(self):
        """Los mirrors de fallback deben terminar con '/'."""
        for mirror in MIRRORS_FALLBACK:
            self.assertTrue(
                mirror.endswith("/"),
                f"Mirror no termina en '/': {mirror}",
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
