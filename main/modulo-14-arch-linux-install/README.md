# Módulo 14: El Instalador de Arch — Automatización de Arch Linux

## 🧠 Concepto Técnico

**Arch Linux** es una distribución Linux minimalista y de lanzamiento continuo (*rolling release*)
que sigue una filosofía de configuración manual total: el usuario construye su sistema desde cero
eligiendo cada componente. Este módulo automatiza ese proceso creando un **asistente interactivo**
en Python que:

1. Descarga la **ISO oficial** de Arch Linux verificando su integridad (SHA256).
2. Genera un **script de VirtualBox** (`VBoxManage`) listo para ejecutar.
3. Genera una **configuración JSON** para `archinstall` (el instalador oficial de Arch).
4. Documenta todos los **pasos de instalación** de la guía oficial.

Inspirado en:
- [Guía de Instalación Oficial](https://wiki.archlinux.org/title/Installation_guide)
- [Descargas HTTP de Arch Linux](https://archlinux.org/download/#http-downloads)

---

## 🎯 Objetivos

1. Entender el proceso completo de instalación de Arch Linux paso a paso.
2. Aprender a descargar y verificar imágenes ISO con Python (sin dependencias externas).
3. Automatizar la creación de VMs con `VBoxManage` desde línea de comandos.
4. Usar `archinstall` (el instalador oficial en Python) con configuración JSON.
5. Practicar diseño de CLIs interactivos en Python.

---

## 📁 Estructura

```
modulo-14-arch-linux-install/
├── README.md
├── mapa-mental.md
└── codigo/
    └── python/
        ├── arch_install.py         # Asistente interactivo principal
        ├── iso_downloader.py       # Módulo: descarga y verificación de ISO
        ├── vbox_setup.py           # Módulo: generación de scripts VirtualBox
        ├── test_arch_install.py    # Tests unitarios (30 tests, sin dependencias)
        └── auto_install.sh         # Script de autoinstalación para ejecutar en la VM
```

---

## 🚀 Ejecución

### Asistente interactivo completo

```bash
cd codigo/python
python arch_install.py
```

El asistente te guiará por estos pasos:
1. **¿Para qué?** — Selecciona el propósito (VirtualBox, QEMU, bare-metal, solo ISO).
2. **¿Dónde?** — Directorio donde guardar la ISO, scripts y configuraciones.
3. **Sistema Arch** — Hostname, usuario, contraseña, zona horaria, idioma, kernel.
4. **VM VirtualBox** — RAM, CPUs, disco, firmware EFI/BIOS, tipo de red.
5. **Mirror** — Selecciona un servidor de descarga.
6. **Descarga** — Descarga la ISO con barra de progreso y verifica SHA256.
7. **Archivos generados** — `crear_vm_vbox.sh` y `archinstall_config.json`.
8. **Pasos de instalación** — Guía detallada para la instalación dentro de la VM.

### Solo generar scripts (sin descargar ISO)

```bash
python arch_install.py --no-descarga
```

### Ejecutar los tests

```bash
# Con pytest (dentro del Docker)
cd codigo/python
pytest test_arch_install.py -v

# Con unittest estándar
python -m unittest test_arch_install -v
```

---

## 📦 Archivos Generados

Después de ejecutar el asistente encontrarás en tu directorio de destino:

| Archivo | Descripción |
|---|---|
| `iso/archlinux-YYYY.MM.DD-x86_64.iso` | ISO oficial de Arch Linux descargada y verificada |
| `crear_vm_vbox.sh` | Script Bash con comandos `VBoxManage` para crear la VM |
| `archinstall_config.json` | Configuración JSON para el instalador oficial de Arch |

### Usar el script de VirtualBox

```bash
# Ejecutar el script generado
bash ~/arch-install/crear_vm_vbox.sh

# Iniciar la VM
VBoxManage startvm "ArchLinux" --type gui
```

### Script de Autoinstalación (DENTRO de la VM)

Para automatizar la instalación real una vez arrancada la VM de Arch Linux (puedes descargarlo con `curl` tras hacer `push` de este repositorio):

```bash
# 1. Asegúrate de tener Internet en la VM (ping google.com)
# 2. Descarga el script (sustituye 'TuUsuario' por el tuyo en GitHub)
curl -L https://raw.githubusercontent.com/TuUsuario/Proyectos-Entrevistas/main/main/modulo-14-arch-linux-install/codigo/python/auto_install.sh > install.sh

# 3. Hazlo ejecutable y lánzalo
chmod +x install.sh
./install.sh
```

### Usar la configuración de archinstall

Una vez dentro de la VM arrancada con la ISO:

```bash
# Descarga la config desde el host (si tienes carpeta compartida) o escríbela
# Luego ejecuta:
archinstall --config /ruta/archinstall_config.json
```

---

## 📚 Pasos de Instalación (Resumen)

Siguiendo la [guía oficial](https://wiki.archlinux.org/title/Installation_guide):

1. **Arrancar desde la ISO** — Seleccionar en el menú de VirtualBox.
2. **Verificar modo EFI/BIOS** — `ls /sys/firmware/efi/efivars`
3. **Conectar a internet** — Con NAT en VirtualBox es automático; verificar con `ping archlinux.org`
4. **Sincronizar reloj** — `timedatectl set-ntp true`
5. **Particionar disco** — Con `archinstall` (automático) o `fdisk`/`cfdisk` (manual)
6. **Instalar con archinstall** — `archinstall` o `archinstall --config config.json`
7. **Instalación manual (alternativa)** — `pacstrap`, `genfstab`, `arch-chroot`, `grub-install`
8. **Reiniciar** — `umount -R /mnt && reboot`

---

## 🔒 Seguridad

- La ISO se descarga solo por HTTPS desde mirrors oficiales.
- El checksum SHA256 se verifica con el archivo `sha256sums.txt` oficial de `archlinux.org`.
- Si el checksum no coincide, el archivo descargado se elimina automáticamente.
- Las contraseñas no se almacenan en texto claro en ningún archivo del repositorio.

---

## 📚 Recursos

- [Arch Linux Wiki — Installation Guide](https://wiki.archlinux.org/title/Installation_guide)
- [Arch Linux Downloads (HTTP mirrors)](https://archlinux.org/download/#http-downloads)
- [archinstall — Instalador oficial en Python](https://github.com/archlinux/archinstall)
- [VBoxManage Reference](https://www.virtualbox.org/manual/ch08.html)
- [Arch Linux Beginners Guide](https://wiki.archlinux.org/title/Arch_Linux)
