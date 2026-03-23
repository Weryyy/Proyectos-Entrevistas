# Módulo 14: El Instalador de Arch — Automatización de Arch Linux

## 🧠 Concepto Técnico

**Arch Linux** es una distribución Linux minimalista y de lanzamiento continuo (*rolling release*)
que sigue una filosofía de configuración manual total: el usuario construye su sistema desde cero
eligiendo cada componente. Este módulo automatiza ese proceso mediante **tres niveles de despliegue**:

1.  **Nivel Básico (Local)**: Instalación manual asistida por scripts locales.
2.  **Nivel Cloud (GitHub)**: Despliegue automático "Zero-Touch" usando la nube.
3.  **Nivel Dios (iPXE/Netboot)**: Arranque y despliegue directo desde red sin medios físicos (ISO/USB).

---

## 🎯 Niveles de Despliegue (Elite Dev)

Para impresionar en una entrevista técnica, este módulo ofrece tres formas de instalar el sistema:

### 🥉 Nivel 1: Despliegue Local (PC a VM)
Ideal para redes cerradas. Lanzas un servidor web en tu PC y la VM descarga el script directamente.
```powershell
# En tu PC (carpeta del script)
python -m http.server 8080

# En la VM Arch (Live)
curl 192.168.1.XX:8080/auto_install_hyprland.sh | bash
```

### 🥈 Nivel 2: Despliegue Cloud (GitHub Raw)
El estándar de la industria. El script reside en tu repositorio y se descarga en cualquier parte del mundo.
```bash
# En cualquier máquina con Arch Live
curl -L https://tinyurl.com/arch-weryyy-raw | bash
```
*Nota: Apunta a `raw.githubusercontent.com` para evitar descargar código HTML.*

### 🥇 Nivel 3: El Nivel "Dios" (iPXE / Netboot)
Despliegue de infraestructura a gran escala. El ordenador arranca por red (PXE), descarga el kernel de los servidores oficiales de Arch y ejecuta tu script de autoinstalación sin intervención humana.
- **Archivo**: `codigo/python/boot.ipxe`
- **Ventaja**: No necesitas quemar ISOs ni pendrives. Ideal para data centers.

---

## 📁 Estructura

```
modulo-14-arch-linux-install/
├── README.md
├── mapa-mental.md
└── codigo/
    └── python/
        ├── arch_install.py         # Asistente interactivo principal
        ├── auto_install_hyprland.sh # Script potente con entorno gráfico (Hyprland)
        ├── boot.ipxe               # Script de arranque por red (Nivel Dios)
        ├── vbox_setup.py           # Módulo: generación de scripts VirtualBox
        └── ...
```

---

## 🚀 Instalación Automática (Hyprland + Wayland)

El script `auto_install_hyprland.sh` realiza las siguientes tareas de forma autónoma:
1. **Particionado**: Borra `/dev/sda` y crea la estructura base.
2. **Entorno Gráfico**: Instala **Hyprland** (Tiling Window Manager moderno) y **Wayland**.
3. **VM Ready**: Configura drivers de VirtualBox y corrige errores críticos de `XDG_RUNTIME_DIR`.
4. **Login automático**: Configura **SDDM** para arrancar la sesión visual.

**Credenciales por defecto:**
- **Usuario**: `usuario`
- **Contraseña**: `1234`
- **Comandos**: `SUPER + Q` (Terminal Kitty), `SUPER + M` (Salir).

---

## 🚀 Ejecución del Asistente Interactivo

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

### Automatización total para equipos reales (y máquinas virtuales)

Si vas a instalar esto en un sistema y no quieres tener que teclear nada, Arch Linux permite pasarle instrucciones directas desde su menú de inicio usando el parámetro `script=`.

1. En la pantalla donde te pide instalar Arch (la pantalla negra inicial con letras blancas).
2. Justo antes de que acabe la cuenta atrás, pulsa **`Tab`** (si estás en BIOS) o **`e`** (si estás en UEFI).
3. Escribe al final de la línea lo siguiente (dependiendo de si quieres modo terminal o con interfaz Hyprland):

**Para el servidor básico:**
`script=https://raw.githubusercontent.com/Weryyy/Proyectos-Entrevistas/main/main/modulo-14-arch-linux-install/codigo/python/auto_install.sh`

**Para escritorio interactivo (Hyprland):**
`script=https://raw.githubusercontent.com/Weryyy/Proyectos-Entrevistas/main/main/modulo-14-arch-linux-install/codigo/python/auto_install_hyprland.sh`

4. Pulsa **Enter**. El sistema arrancará, se conectará a internet, bajará el archivo y te instalará absolutamente todo hasta dejarte en la pantalla de inicio (login). No necesitas interactuar con él en ningún momento.

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
