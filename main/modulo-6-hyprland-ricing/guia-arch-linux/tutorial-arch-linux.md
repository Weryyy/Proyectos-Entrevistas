# 🏔️ Guía Completa: De Cero a Arch Linux con Hyprland

> **Nivel**: Principiante absoluto → Intermedio
>
> **Tiempo estimado**: 2–4 horas (instalación) + 1–2 horas (configuración de Hyprland)
>
> **Objetivo**: Instalar Arch Linux desde cero y dejarlo listo con Hyprland para
> trabajar los sub-módulos del Módulo 6.

> ⚠️ **ADVERTENCIA IMPORTANTE**: La instalación de Arch Linux implica particionar
> discos y formatear particiones. Si no tienes cuidado, **puedes perder todos tus
> datos**. Lee cada paso completamente antes de ejecutarlo. Si tienes dudas, practica
> primero en una máquina virtual (VirtualBox, QEMU/KVM, VMware).

---

## Tabla de Contenidos

- [Parte 1: ¿Qué es Arch Linux?](#parte-1-qué-es-arch-linux)
- [Parte 2: Preparación](#parte-2-preparación)
- [Parte 3: Instalación de Arch Linux](#parte-3-instalación-de-arch-linux)
- [Parte 4: Post-instalación — Preparar el entorno](#parte-4-post-instalación--preparar-el-entorno)
- [Parte 5: Configurar Hyprland](#parte-5-configurar-hyprland)
- [Parte 6: Dotfiles — Gestión de configuración](#parte-6-dotfiles--gestión-de-configuración)
- [Parte 7: Compilar Plugins de Hyprland](#parte-7-compilar-plugins-de-hyprland)
- [Parte 8: El Ecosistema Rivendell](#parte-8-el-ecosistema-rivendell)

---

## Parte 1: ¿Qué es Arch Linux?

### Filosofía

Arch Linux se basa en tres principios fundamentales:

1. **Simplicidad**: Arch no esconde la complejidad detrás de herramientas gráficas.
   En lugar de eso, te da acceso directo al sistema. La "simplicidad" aquí significa
   *sin capas innecesarias de abstracción*, no "fácil de usar".

2. **Centrado en el usuario**: Arch asume que **tú** sabes (o quieres aprender) cómo
   funciona tu sistema. No toma decisiones por ti — tú eliges cada componente:
   el kernel, el bootloader, el entorno de escritorio, el gestor de paquetes AUR...

3. **Rolling release**: No hay "versiones" de Arch (como Ubuntu 22.04 o Fedora 39).
   Siempre tienes la última versión de todo. Un `sudo pacman -Syu` te actualiza
   todo el sistema a lo más reciente.

### ¿Por qué Arch Linux para ricing?

| Ventaja | Explicación |
|---------|-------------|
| **AUR** (Arch User Repository) | Miles de paquetes mantenidos por la comunidad. Si existe un programa para Linux, probablemente está en el AUR. Herramientas como `yay` o `paru` facilitan la instalación. |
| **Paquetes siempre actualizados** | Al ser rolling release, tienes las últimas versiones de Hyprland, Waybar, etc. sin esperar a que una distro las empaquete. |
| **Base mínima** | Arch se instala sin entorno de escritorio, sin bloatware, sin nada que no necesites. Tú construyes desde cero = control total. |
| **Arch Wiki** | La mejor documentación de cualquier distribución Linux. Si tienes un problema, la wiki probablemente tiene la respuesta. |
| **Comunidad activa** | Foros, Reddit (r/archlinux), Discord de Hyprland — comunidad enorme y activa. |

### Comparación con otras distribuciones

```
┌─────────────────┬───────────────┬────────────────┬──────────────────┐
│                 │  Ubuntu/Mint  │    Fedora      │   Arch Linux     │
├─────────────────┼───────────────┼────────────────┼──────────────────┤
│ Instalación     │ Gráfica,      │ Gráfica,       │ Manual, línea    │
│                 │ guiada        │ guiada         │ de comandos      │
├─────────────────┼───────────────┼────────────────┼──────────────────┤
│ Paquetes        │ apt (.deb)    │ dnf (.rpm)     │ pacman + AUR     │
├─────────────────┼───────────────┼────────────────┼──────────────────┤
│ Actualizaciones │ Cada 6 meses  │ Cada 6 meses   │ Rolling release  │
│                 │ (LTS: 2 años) │                │ (continuo)       │
├─────────────────┼───────────────┼────────────────┼──────────────────┤
│ Personalización │ Limitada por  │ Moderada       │ Total — tú       │
│                 │ GNOME/KDE     │                │ construyes todo  │
├─────────────────┼───────────────┼────────────────┼──────────────────┤
│ Hyprland        │ Versiones     │ Versiones      │ Última versión   │
│                 │ atrasadas     │ recientes      │ siempre (AUR)    │
├─────────────────┼───────────────┼────────────────┼──────────────────┤
│ Curva de        │ Baja          │ Media          │ Alta (pero       │
│ aprendizaje     │               │                │ muy educativa)   │
└─────────────────┴───────────────┴────────────────┴──────────────────┘
```

> 💡 **¿Es Arch difícil?** No es "difícil" — es *manual*. La instalación que en Ubuntu
> toma 10 clics, en Arch son 30 comandos. Pero al terminar, entiendes exactamente qué
> hay en tu sistema y por qué.

---

## Parte 2: Preparación

### 2.1 Descargar la ISO de Arch Linux

1. Ve a [archlinux.org/download](https://archlinux.org/download/)
2. Descarga la ISO más reciente (≈ 800 MB)
3. Verifica la firma (opcional pero recomendado):

```bash
# En Linux/macOS
gpg --keyserver-options auto-key-retrieve --verify archlinux-xxxx.xx.xx-x86_64.iso.sig
```

### 2.2 Crear USB booteable

#### Opción A: Desde Windows (Rufus)

1. Descarga [Rufus](https://rufus.ie/)
2. Inserta tu USB (mínimo 2 GB — **se borrarán todos los datos**)
3. En Rufus:
   - Dispositivo: tu USB
   - Selección de arranque: la ISO de Arch
   - Esquema de partición: **GPT** (para UEFI)
   - Sistema de archivos: FAT32
4. Clic en "Empezar"

#### Opción B: Desde Linux (dd)

```bash
# ⚠️ CUIDADO: verifica que /dev/sdX sea tu USB, NO tu disco duro
# Usa 'lsblk' para identificar los dispositivos

lsblk  # Identifica tu USB (ej: /dev/sdb)

sudo dd bs=4M if=archlinux-xxxx.xx.xx-x86_64.iso of=/dev/sdX status=progress oflag=sync
```

> ⚠️ **PELIGRO**: `dd` escribe directamente al dispositivo sin confirmación. Si pones
> el disco equivocado en `of=`, **perderás todos los datos de ese disco**. Verifica
> tres veces antes de ejecutar.

#### Opción C: Multiplataforma (Etcher)

1. Descarga [balenaEtcher](https://etcher.balena.io/)
2. Selecciona la ISO
3. Selecciona el USB
4. Clic en "Flash!"

### 2.3 Configurar BIOS/UEFI

Reinicia tu computadora y entra al BIOS/UEFI (normalmente presionando `F2`, `F12`,
`DEL` o `ESC` durante el arranque — depende del fabricante).

Configura lo siguiente:

| Opción | Valor | Razón |
|--------|-------|-------|
| **Secure Boot** | Deshabilitado | Arch Linux no viene firmado para Secure Boot por defecto |
| **Boot Order** | USB primero | Para arrancar desde el USB de instalación |
| **CSM/Legacy Boot** | Deshabilitado | Queremos arrancar en modo UEFI puro |
| **Fast Boot** | Deshabilitado | Puede interferir con la detección del USB |

### 2.4 Consideraciones para dual boot (Windows + Arch)

Si quieres mantener Windows en tu máquina:

1. **Desde Windows**, reduce la partición principal:
   - Abre "Administración de discos" (`diskmgmt.msc`)
   - Clic derecho en la partición C: → "Reducir volumen"
   - Libera al menos **50 GB** (recomendado: 100+ GB)
   - No formatees el espacio libre — lo haremos desde Arch

2. **Desactiva Fast Startup** en Windows:
   - Panel de Control → Opciones de energía → "Elegir el comportamiento del botón de inicio/apagado"
   - Desactiva "Activar inicio rápido"
   - Esto evita problemas con particiones NTFS montadas

3. **No toques la partición EFI** — Arch la compartirá con Windows

> 💡 **Recomendación**: Si es tu primera vez, usa una **máquina virtual** o un disco
> separado. El dual boot funciona bien, pero un error puede dejarte sin arranque de
> Windows.

---

## Parte 3: Instalación de Arch Linux

### 3.1 Arrancar desde el USB

1. Inserta el USB y reinicia
2. Selecciona el USB en el menú de arranque
3. En el menú de Arch, selecciona: **Arch Linux install medium (x86_64, UEFI)**
4. Llegarás a un prompt como: `root@archiso ~ #`

Verifica que estás en modo UEFI:

```bash
# Si este directorio existe, estás en modo UEFI
ls /sys/firmware/efi/efivars
```

Si no existe, reinicia y verifica la configuración de tu BIOS.

### 3.2 Configurar teclado (opcional)

El teclado viene en inglés US por defecto. Si necesitas español:

```bash
loadkeys es
# O para Latinoamérica:
loadkeys la-latin1
```

### 3.3 Conectar a internet

#### Ethernet (automático)

Si estás conectado por cable, debería funcionar automáticamente:

```bash
ping -c 3 archlinux.org
```

#### WiFi (iwctl)

```bash
# Entrar al prompt interactivo de iwd
iwctl

# Dentro de iwctl:
device list                          # Ver adaptadores WiFi
station wlan0 scan                   # Escanear redes
station wlan0 get-networks           # Listar redes disponibles
station wlan0 connect "Tu-Red-WiFi"  # Conectar (pedirá contraseña)
exit                                 # Salir de iwctl

# Verificar conexión
ping -c 3 archlinux.org
```

### 3.4 Sincronizar reloj

```bash
timedatectl set-ntp true
timedatectl status
```

### 3.5 Particionar el disco

> ⚠️ **PUNTO DE NO RETORNO**: Los siguientes pasos modifican tu disco. Asegúrate de
> estar trabajando en el disco correcto.

Primero, identifica tus discos:

```bash
lsblk
# Ejemplo de salida:
# NAME   SIZE TYPE MOUNTPOINT
# sda    500G disk
# ├─sda1 512M part           ← Partición EFI (si existe por Windows)
# ├─sda2 100G part           ← Windows (si tienes dual boot)
# └─sda3 399G part           ← Espacio libre / partición a usar
# nvme0n1 1T disk            ← Disco NVMe (si tienes)
```

Usaremos `cfdisk` (interfaz visual) para particionar. Si haces **instalación limpia**
(sin Windows):

```bash
cfdisk /dev/sda   # o /dev/nvme0n1 si es NVMe
```

Crea estas particiones:

| Partición | Tamaño | Tipo | Propósito |
|-----------|--------|------|-----------|
| `/dev/sda1` | 512 MB | EFI System | Bootloader |
| `/dev/sda2` | Tamaño de tu RAM | Linux swap | Memoria virtual + hibernación |
| `/dev/sda3` | Resto del disco | Linux filesystem | Sistema raíz (`/`) |

En `cfdisk`:
1. Selecciona `gpt` como tipo de tabla (si es disco nuevo)
2. Crea cada partición: `[New]` → tamaño → `[Type]` → tipo correcto
3. Al terminar: `[Write]` → escribe "yes" → `[Quit]`

> 💡 **Dual boot**: Si ya tienes una partición EFI de Windows, **NO** crees otra.
> Usa la existente. Solo crea swap y root en el espacio libre.

### 3.6 Formatear particiones

```bash
# Formatear partición EFI (SOLO si es nueva, NO si es compartida con Windows)
mkfs.fat -F 32 /dev/sda1

# Crear y activar swap
mkswap /dev/sda2
swapon /dev/sda2

# Formatear partición raíz
mkfs.ext4 /dev/sda3
```

> ⚠️ **Dual boot**: Si compartes la partición EFI con Windows, **NO ejecutes**
> `mkfs.fat` en ella — borraría el bootloader de Windows.

### 3.7 Montar particiones

```bash
# Montar raíz
mount /dev/sda3 /mnt

# Crear directorio para EFI y montar
mount --mkdir /dev/sda1 /mnt/boot

# Verificar
lsblk
```

### 3.8 Instalar el sistema base

```bash
# Instalar paquetes esenciales
pacstrap -K /mnt base linux linux-firmware

# Opcional pero recomendado: añadir editor y herramientas de red
pacstrap -K /mnt base-devel networkmanager vim nano sudo
```

¿Qué hace cada paquete?
- `base`: paquetes mínimos del sistema (glibc, bash, coreutils...)
- `linux`: el kernel de Linux
- `linux-firmware`: firmware para hardware (WiFi, GPU, etc.)
- `base-devel`: herramientas de compilación (gcc, make...) — necesarias para el AUR
- `networkmanager`: gestión de red (WiFi y Ethernet)
- `vim` / `nano`: editores de texto en terminal
- `sudo`: permite ejecutar comandos como root

### 3.9 Generar fstab

El archivo `fstab` le dice al sistema qué particiones montar al arrancar:

```bash
genfstab -U /mnt >> /mnt/etc/fstab

# Verificar que se generó correctamente
cat /mnt/etc/fstab
```

Deberías ver entradas para tu raíz (`/`), boot (`/boot`) y swap.

### 3.10 Entrar al nuevo sistema (chroot)

```bash
arch-chroot /mnt
```

Ahora estás "dentro" de tu nueva instalación de Arch.

### 3.11 Configurar zona horaria

```bash
# Ejemplo para España
ln -sf /usr/share/zoneinfo/Europe/Madrid /etc/localtime

# Ejemplo para México
ln -sf /usr/share/zoneinfo/America/Mexico_City /etc/localtime

# Ejemplo para Argentina
ln -sf /usr/share/zoneinfo/America/Argentina/Buenos_Aires /etc/localtime

# Sincronizar reloj del hardware
hwclock --systohc
```

> 💡 Lista todas las zonas disponibles con: `ls /usr/share/zoneinfo/`

### 3.12 Configurar idioma (locale)

```bash
# Editar el archivo de locales
vim /etc/locale.gen
# (o nano /etc/locale.gen)

# Descomenta (quita el #) las líneas:
#   en_US.UTF-8 UTF-8
#   es_ES.UTF-8 UTF-8
# (o el locale de tu país)

# Generar locales
locale-gen

# Establecer idioma del sistema
echo "LANG=es_ES.UTF-8" > /etc/locale.conf
```

### 3.13 Configurar teclado persistente

```bash
echo "KEYMAP=es" > /etc/vconsole.conf
# O para Latinoamérica:
echo "KEYMAP=la-latin1" > /etc/vconsole.conf
```

### 3.14 Configurar hostname (nombre del equipo)

```bash
# Elige un nombre para tu máquina
echo "rivendell" > /etc/hostname
```

### 3.15 Configurar contraseña de root

```bash
passwd
# Introduce tu contraseña (no se muestra al escribir)
```

### 3.16 Instalar bootloader

Usaremos **GRUB** (el más común y compatible):

```bash
# Instalar GRUB y herramientas EFI
pacman -S grub efibootmgr

# Instalar GRUB en la partición EFI
grub-install --target=x86_64-efi --efi-directory=/boot --bootloader-id=GRUB

# Generar configuración de GRUB
grub-mkconfig -o /boot/grub/grub.cfg
```

> 💡 **Dual boot**: Si tienes Windows, instala también `os-prober`:
> ```bash
> pacman -S os-prober
> # Edita /etc/default/grub y descomenta:
> #   GRUB_DISABLE_OS_PROBER=false
> grub-mkconfig -o /boot/grub/grub.cfg
> ```
> GRUB debería detectar Windows automáticamente.

**Alternativa: systemd-boot** (más simple, solo UEFI):

```bash
bootctl install

# Crear entrada de arranque
cat > /boot/loader/entries/arch.conf << 'EOF'
title   Arch Linux
linux   /vmlinuz-linux
initrd  /initramfs-linux.img
options root=/dev/sda3 rw
EOF

# Configurar loader
cat > /boot/loader/loader.conf << 'EOF'
default arch.conf
timeout 3
console-mode max
EOF
```

### 3.17 Crear usuario con sudo

```bash
# Crear usuario (reemplaza 'elfo' con tu nombre)
useradd -m -G wheel -s /bin/bash elfo

# Establecer contraseña
passwd elfo

# Habilitar sudo para el grupo wheel
EDITOR=vim visudo
# Descomenta la línea:
#   %wheel ALL=(ALL:ALL) ALL
```

### 3.18 Habilitar servicios esenciales

```bash
# Red (imprescindible para tener internet al reiniciar)
systemctl enable NetworkManager
```

### 3.19 Salir y reiniciar

```bash
# Salir del chroot
exit

# Desmontar particiones
umount -R /mnt

# Reiniciar
reboot
```

**Retira el USB** cuando la máquina se reinicie. Deberías ver GRUB y poder
arrancar en tu nuevo Arch Linux.

> 🎉 **¡Felicidades!** Si llegas a un prompt de login, tu instalación fue exitosa.
> Inicia sesión con el usuario que creaste.

---

## Parte 4: Post-instalación — Preparar el entorno

### 4.1 Conectar a internet

```bash
# Si usas Ethernet, debería conectarse automáticamente

# Para WiFi:
nmcli device wifi list                              # Listar redes
nmcli device wifi connect "Tu-Red" password "clave" # Conectar

# Verificar
ping -c 3 archlinux.org
```

### 4.2 Actualizar el sistema

```bash
sudo pacman -Syu
```

> 💡 Ejecuta esto frecuentemente. Al ser rolling release, las actualizaciones son
> incrementales y rara vez rompen cosas.

### 4.3 Instalar paquetes esenciales

```bash
# Herramientas básicas de desarrollo
sudo pacman -S git base-devel vim neovim

# Herramientas útiles
sudo pacman -S htop tree wget curl unzip
```

### 4.4 Instalar yay (AUR helper)

El **AUR** (Arch User Repository) es un repositorio mantenido por la comunidad con
miles de paquetes adicionales. `yay` es un helper que facilita instalar desde el AUR:

```bash
# Clonar el repositorio de yay
git clone https://aur.archlinux.org/yay.git
cd yay

# Compilar e instalar
makepkg -si

# Limpiar
cd .. && rm -rf yay

# Verificar
yay --version
```

Ahora puedes instalar paquetes del AUR igual que con pacman:

```bash
yay -S nombre-del-paquete
```

### 4.5 Instalar Hyprland

```bash
# Instalar la versión git (necesaria para plugins)
yay -S hyprland-git

# Alternativa: versión estable (sin soporte de plugins experimentales)
# sudo pacman -S hyprland
```

### 4.6 Instalar paquetes esenciales de Wayland

```bash
# Portales XDG (integración con apps)
yay -S xdg-desktop-portal-hyprland

# Soporte Qt para Wayland
sudo pacman -S qt5-wayland qt6-wayland

# Variables de entorno para Wayland
# Se configurarán en hyprland.conf más adelante
```

### 4.7 Instalar drivers de GPU

```bash
# AMD (recomendado para Wayland)
sudo pacman -S mesa vulkan-radeon libva-mesa-driver

# Intel
sudo pacman -S mesa vulkan-intel intel-media-driver

# NVIDIA (⚠️ requiere configuración adicional)
sudo pacman -S nvidia nvidia-utils
# Consulta: https://wiki.hyprland.org/Nvidia/
```

> ⚠️ **NVIDIA en Wayland**: Funciona, pero requiere configuración adicional.
> Consulta la [wiki de Hyprland sobre NVIDIA](https://wiki.hyprland.org/Nvidia/)
> para los pasos específicos.

---

## Parte 5: Configurar Hyprland

### 5.1 Primer arranque

Desde la TTY (la pantalla de texto donde haces login), simplemente ejecuta:

```bash
Hyprland
```

La primera vez, Hyprland creará un archivo de configuración por defecto en
`~/.config/hypr/hyprland.conf`. Verás un escritorio vacío con un fondo de pantalla
por defecto.

Keybinds por defecto:
- `SUPER + Q`: abrir terminal (si tienes kitty/alacritty instalado)
- `SUPER + C`: cerrar ventana activa
- `SUPER + M`: salir de Hyprland
- `SUPER + 1-9`: cambiar de workspace
- `SUPER + flechas`: mover foco entre ventanas

### 5.2 Conceptos clave de configuración

El archivo `~/.config/hypr/hyprland.conf` controla todo. Estos son los bloques
principales:

#### Monitores

```ini
# Formato: monitor = nombre, resolución@frecuencia, posición, escala
monitor = , preferred, auto, 1
# "," sin nombre = todos los monitores
# "preferred" = resolución nativa
# "auto" = posición automática
# "1" = sin escalado

# Ejemplo específico:
monitor = DP-1, 2560x1440@144, 0x0, 1
monitor = HDMI-A-1, 1920x1080@60, 2560x0, 1
```

#### Workspaces

```ini
# Asignar workspaces a monitores
workspace = 1, monitor:DP-1
workspace = 2, monitor:DP-1
workspace = 6, monitor:HDMI-A-1
```

#### Keybinds

```ini
# Formato: bind = MODS, key, dispatcher, params
bind = SUPER, Q, exec, kitty              # Abrir terminal
bind = SUPER, C, killactive               # Cerrar ventana
bind = SUPER, F, fullscreen               # Pantalla completa
bind = SUPER, V, togglefloating           # Flotar/tildar ventana
bind = SUPER, R, exec, wofi --show drun   # Lanzador de apps

# Mover entre ventanas
bind = SUPER, left, movefocus, l
bind = SUPER, right, movefocus, r
bind = SUPER, up, movefocus, u
bind = SUPER, down, movefocus, d

# Cambiar de workspace
bind = SUPER, 1, workspace, 1
bind = SUPER, 2, workspace, 2
# ... etc
```

#### Window Rules

```ini
# Formato: windowrulev2 = regla, filtro
windowrulev2 = float, class:^(pavucontrol)$
windowrulev2 = opacity 0.9, class:^(kitty)$
windowrulev2 = workspace 3 silent, class:^(firefox)$
```

#### Animaciones

```ini
animations {
    enabled = yes
    bezier = myBezier, 0.05, 0.9, 0.1, 1.05

    animation = windows, 1, 7, myBezier
    animation = windowsOut, 1, 7, default, popin 80%
    animation = border, 1, 10, default
    animation = fade, 1, 7, default
    animation = workspaces, 1, 6, default
}
```

### 5.3 Herramientas complementarias esenciales

Instala estas herramientas para un entorno funcional:

```bash
# Terminal
sudo pacman -S kitty
# Alternativa: alacritty

# Lanzador de aplicaciones
sudo pacman -S wofi
# Alternativa: yay -S rofi-wayland

# Barra de estado
sudo pacman -S waybar

# Notificaciones
sudo pacman -S mako
# Alternativa: sudo pacman -S dunst

# Gestor de archivos
sudo pacman -S thunar
# Alternativa: sudo pacman -S nautilus

# Capturas de pantalla
sudo pacman -S grim slurp
# Uso: grim -g "$(slurp)" screenshot.png

# Audio
sudo pacman -S pipewire pipewire-pulse wireplumber
systemctl --user enable --now pipewire pipewire-pulse wireplumber

# Control de volumen (GUI)
sudo pacman -S pavucontrol

# Gestión de inactividad y bloqueo
sudo pacman -S swayidle swaylock

# Fondo de pantalla
yay -S swww
# Alternativa: sudo pacman -S swaybg
```

Configura el autostart en `hyprland.conf`:

```ini
# Autostart
exec-once = waybar
exec-once = mako
exec-once = swww-daemon
exec-once = swww img ~/wallpapers/rivendell.jpg

# Idle management
exec-once = swayidle -w \
    timeout 300 'swaylock -f' \
    timeout 600 'hyprctl dispatch dpms off' \
    resume 'hyprctl dispatch dpms on'
```

---

## Parte 6: Dotfiles — Gestión de configuración

### 6.1 ¿Qué son los dotfiles?

En Linux, los archivos de configuración de la mayoría de aplicaciones se guardan en
el directorio `~/.config/`. Se llaman "dotfiles" porque tradicionalmente empezaban
con un punto (`.bashrc`, `.vimrc`), haciéndolos ocultos por defecto.

```
~/.config/
├── hypr/
│   └── hyprland.conf        ← Configuración de Hyprland
├── waybar/
│   ├── config               ← Configuración de Waybar
│   └── style.css            ← Estilos de Waybar
├── kitty/
│   └── kitty.conf           ← Configuración de Kitty
├── mako/
│   └── config               ← Configuración de notificaciones
├── wofi/
│   ├── config               ← Configuración de Wofi
│   └── style.css            ← Estilos de Wofi
└── ...
```

### 6.2 Gestión con GNU Stow

**GNU Stow** es una herramienta que crea symlinks (enlaces simbólicos) automáticamente.
Es perfecta para gestionar dotfiles:

```bash
# Instalar Stow
sudo pacman -S stow

# Crear estructura de dotfiles
mkdir -p ~/dotfiles
cd ~/dotfiles

# Crear estructura que refleje ~/.config/
mkdir -p hypr/.config/hypr
mkdir -p waybar/.config/waybar
mkdir -p kitty/.config/kitty

# Mover tus configs existentes
mv ~/.config/hypr/hyprland.conf hypr/.config/hypr/
mv ~/.config/waybar/config waybar/.config/waybar/
mv ~/.config/kitty/kitty.conf kitty/.config/kitty/

# Crear symlinks con Stow
cd ~/dotfiles
stow hypr      # Crea: ~/.config/hypr/hyprland.conf → dotfiles/hypr/.config/hypr/hyprland.conf
stow waybar    # Crea: ~/.config/waybar/config → dotfiles/waybar/.config/waybar/config
stow kitty     # Crea: ~/.config/kitty/kitty.conf → dotfiles/kitty/.config/kitty/kitty.conf
```

### 6.3 Control de versiones con Git

```bash
cd ~/dotfiles

# Inicializar repositorio
git init

# Crear .gitignore
cat > .gitignore << 'EOF'
# Ignorar archivos sensibles
*.secret
*.key
*password*
EOF

# Primer commit
git add -A
git commit -m "Initial dotfiles setup"

# Opcional: subir a GitHub
git remote add origin https://github.com/tu-usuario/dotfiles.git
git push -u origin main
```

### 6.4 Estructura del Rivendell

El proyecto Rivendell organiza sus dotfiles así:

```
rivendell-hyprdots/
├── hypr/
│   └── .config/hypr/
│       ├── hyprland.conf         ← Config principal
│       ├── keybinds.conf         ← Atajos de teclado
│       ├── rules.conf            ← Reglas de ventanas
│       └── autostart.conf        ← Programas al iniciar
├── waybar/
│   └── .config/waybar/
│       ├── config.jsonc          ← Módulos de la barra
│       └── style.css             ← Estilos CSS
├── quickshell/
│   └── .config/quickshell/
│       └── *.qml                 ← Widgets QML
├── sounds/
│   └── .local/share/sounds/
│       └── rivendell/            ← Efectos de sonido
└── scripts/
    └── .local/bin/
        ├── ipc-sounds.sh         ← Script de sonidos IPC
        └── rope-screenshot.py    ← Herramienta de captura
```

---

## Parte 7: Compilar Plugins de Hyprland

### 7.1 Preparar el entorno de desarrollo

Los plugins de Hyprland son bibliotecas compartidas (`.so`) escritas en C++ que
se cargan en tiempo de ejecución. Para compilarlos necesitas:

```bash
# Herramientas de compilación
sudo pacman -S cmake meson gcc

# Hyprland headers (se instalan automáticamente con hyprland-git)
# Verificar:
ls /usr/include/hyprland/
```

### 7.2 Clonar el código fuente de Hyprland

Algunos plugins necesitan los headers completos del código fuente:

```bash
# Clonar Hyprland
git clone --recursive https://github.com/hyprwm/Hyprland.git
cd Hyprland

# Checkout la misma versión que tienes instalada
hyprctl version  # Ver tu versión
git checkout <tag-o-commit>

# Preparar headers
make all
```

### 7.3 Usar hyprpm (Hyprland Plugin Manager)

`hyprpm` es el gestor oficial de plugins de Hyprland:

```bash
# Añadir un repositorio de plugins
hyprpm add https://github.com/usuario/plugin-repo

# Listar plugins disponibles
hyprpm list

# Habilitar un plugin
hyprpm enable plugin-name

# Deshabilitar
hyprpm disable plugin-name

# Actualizar plugins
hyprpm update
```

### 7.4 Compilar un plugin manualmente

```bash
# Estructura típica de un plugin
mi-plugin/
├── CMakeLists.txt
├── src/
│   └── main.cpp
└── README.md

# Compilar
cd mi-plugin
cmake -B build
cmake --build build

# El resultado será: build/libmi-plugin.so

# Cargar en Hyprland
hyprctl plugin load /ruta/completa/build/libmi-plugin.so
```

### 7.5 Depurar plugins

```bash
# Ver logs de Hyprland (incluye errores de plugins)
cat /tmp/hypr/$HYPRLAND_INSTANCE_SIGNATURE/hyprland.log

# Seguir logs en tiempo real
tail -f /tmp/hypr/$HYPRLAND_INSTANCE_SIGNATURE/hyprland.log

# Recargar un plugin después de cambios
hyprctl plugin unload /ruta/build/libmi-plugin.so
hyprctl plugin load /ruta/build/libmi-plugin.so
```

> 💡 **Consejo**: Los plugins que causan un crash reiniciarán Hyprland. Guarda tu
> trabajo antes de probar plugins nuevos.

---

## Parte 8: El Ecosistema Rivendell

### 8.1 Lista completa de dependencias

Aquí están todas las dependencias necesarias para replicar el setup completo de
Rivendell, con una explicación de qué hace cada una:

| Paquete | Fuente | Descripción |
|---------|--------|-------------|
| `hyprland-git` | AUR | Compositor Wayland (versión git para plugins) |
| `quickshell` | AUR | Framework QML para crear shells/widgets en Wayland |
| `kitty` | pacman | Emulador de terminal con soporte GPU |
| `waybar` | pacman | Barra de estado altamente configurable |
| `mako` | pacman | Demonio de notificaciones ligero |
| `wofi` | pacman | Lanzador de aplicaciones para Wayland |
| `grim` | pacman | Captura de pantalla para Wayland |
| `slurp` | pacman | Selector de región para capturas |
| `socat` | pacman | Herramienta de comunicación por sockets (para IPC) |
| `sox` | pacman | Reproductor/procesador de audio en línea de comandos |
| `pipewire` | pacman | Servidor multimedia moderno (reemplaza PulseAudio) |
| `wireplumber` | pacman | Session manager para PipeWire |
| `swayidle` | pacman | Gestión de inactividad (apagar pantalla, bloquear) |
| `swaylock` | pacman | Pantalla de bloqueo para Wayland |
| `swww` | AUR | Demonio de fondo de pantalla con transiciones |
| `python` | pacman | Para la herramienta de screenshot con física |
| `cmake` | pacman | Sistema de build para plugins C++ |
| `xdg-desktop-portal-hyprland` | AUR | Portal XDG para compartir pantalla, etc. |
| `qt5-wayland` | pacman | Soporte Wayland para aplicaciones Qt5 |
| `qt6-wayland` | pacman | Soporte Wayland para aplicaciones Qt6 |
| `nerd-fonts-complete` | AUR | Fuentes con iconos para Waybar y terminal |

### 8.2 Instalar todo de una vez

```bash
# Paso 1: Paquetes de los repositorios oficiales
sudo pacman -S --needed \
    kitty waybar mako wofi \
    grim slurp socat sox \
    pipewire pipewire-pulse wireplumber \
    swayidle swaylock \
    python cmake gcc meson \
    qt5-wayland qt6-wayland \
    git base-devel vim neovim \
    thunar pavucontrol htop tree wget curl unzip

# Paso 2: Paquetes del AUR
yay -S --needed \
    hyprland-git \
    quickshell \
    xdg-desktop-portal-hyprland \
    swww \
    nerd-fonts-complete

# Paso 3: Habilitar servicios de audio
systemctl --user enable --now pipewire pipewire-pulse wireplumber
```

### 8.3 Aplicar los dotfiles de Rivendell

```bash
# Clonar el repositorio original
git clone https://codeberg.org/zacoons/rivendell-hyprdots.git
cd rivendell-hyprdots

# ⚠️ IMPORTANTE: Haz backup de tus configs actuales primero
cp -r ~/.config/hypr ~/.config/hypr.backup

# Revisar la estructura del repositorio
ls -la

# Seguir las instrucciones del README del repositorio original
# para aplicar las configuraciones
cat README.md
```

> ⚠️ **Advertencia**: Aplicar dotfiles de otra persona sobrescribirá tus
> configuraciones. Siempre haz backup primero.

---

## Troubleshooting — Problemas comunes

### No arranca Hyprland

```bash
# Ver logs de la última sesión
cat /tmp/hypr/$(ls -t /tmp/hypr/ | head -1)/hyprland.log | tail -50

# Verificar que tienes drivers de GPU
lspci -k | grep -A 2 VGA
```

### No hay sonido

```bash
# Verificar que PipeWire está corriendo
systemctl --user status pipewire

# Reiniciar PipeWire
systemctl --user restart pipewire pipewire-pulse wireplumber

# Ver dispositivos de audio
wpctl status
```

### WiFi no funciona después de instalar

```bash
# Verificar que NetworkManager está activo
systemctl status NetworkManager

# Si no está activo:
sudo systemctl enable --now NetworkManager

# Listar redes
nmcli device wifi list
```

### GRUB no detecta Windows (dual boot)

```bash
# Instalar os-prober si no lo tienes
sudo pacman -S os-prober

# Habilitar os-prober en GRUB
sudo vim /etc/default/grub
# Descomenta: GRUB_DISABLE_OS_PROBER=false

# Montar la partición EFI de Windows si no está montada
sudo mount /dev/sda1 /boot

# Regenerar configuración de GRUB
sudo grub-mkconfig -o /boot/grub/grub.cfg
```

### Pantalla parpadeante con NVIDIA

```bash
# Agregar variables de entorno en hyprland.conf
env = LIBVA_DRIVER_NAME,nvidia
env = XDG_SESSION_TYPE,wayland
env = GBM_BACKEND,nvidia-drm
env = __GLX_VENDOR_LIBRARY_NAME,nvidia
env = WLR_NO_HARDWARE_CURSORS,1
```

### Aplicaciones Qt/GTK se ven mal

```bash
# Añadir a hyprland.conf:
env = QT_QPA_PLATFORM,wayland
env = QT_QPA_PLATFORMTHEME,qt5ct
env = GDK_BACKEND,wayland,x11
env = SDL_VIDEODRIVER,wayland
env = CLUTTER_BACKEND,wayland
env = XDG_CURRENT_DESKTOP,Hyprland
env = XDG_SESSION_TYPE,wayland
env = XDG_SESSION_DESKTOP,Hyprland

# Instalar herramientas de temas
sudo pacman -S qt5ct nwg-look
```

---

## Recursos adicionales

| Recurso | Enlace |
|---------|--------|
| Arch Wiki (español) | [wiki.archlinux.org/title/Main_page_(Español)](https://wiki.archlinux.org/title/Main_page_(Espa%C3%B1ol)) |
| Hyprland Wiki | [wiki.hyprland.org](https://wiki.hyprland.org/) |
| Hyprland GitHub | [github.com/hyprwm/Hyprland](https://github.com/hyprwm/Hyprland) |
| r/unixporn (ricing) | [reddit.com/r/unixporn](https://www.reddit.com/r/unixporn/) |
| r/hyprland | [reddit.com/r/hyprland](https://www.reddit.com/r/hyprland/) |
| Rivendell Hyprdots | [codeberg.org/zacoons/rivendell-hyprdots](https://codeberg.org/zacoons/rivendell-hyprdots) |

---

## Navegación

| ← Volver al módulo | Inicio |
|:-------------------:|:------:|
| [README del Módulo 6](../README.md) | [README principal](../../../README.md) |
