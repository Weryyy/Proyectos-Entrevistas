#!/bin/bash
# -----------------------------------------------------------------------------
# Script de auto-instalación para Arch Linux + Hyprland (Totalmente automático)
# -----------------------------------------------------------------------------

set -e

echo "=========================================================="
echo " Iniciando instalación de Arch Linux con Hyprland "
echo "=========================================================="

echo "[1/6] Configurando teclado en español..."
loadkeys es

echo "[2/6] Borrando y particionando el disco /dev/sda..."
sfdisk /dev/sda <<EOF
label: dos
device: /dev/sda
unit: sectors

/dev/sda1 : start= 2048, type=83, bootable
EOF

echo "[3/6] Formateando y montando..."
mkfs.ext4 /dev/sda1
mount /dev/sda1 /mnt

echo "[4/6] Instalando el sistema base y el entorno gráfico..."
# Añadimos paquetes de red, sonido, gráficos, y por supuesto Hyprland, SDDM y extras para máquinas virtuales (VirtualBox)
pacstrap /mnt base linux linux-firmware base-devel nano networkmanager sudo grub \
    hyprland kitty sddm waybar rofi \
    virtualbox-guest-utils mesa \
    xorg-xwayland qt5-wayland qt6-wayland polkit-kde-agent

echo "[5/6] Generando fstab..."
genfstab -U /mnt >> /mnt/etc/fstab

echo "[6/6] Configurando el sistema interno..."
arch-chroot /mnt /bin/bash <<EOF
# Reloj e idioma
ln -sf /usr/share/zoneinfo/Europe/Madrid /etc/localtime
hwclock --systohc
sed -i 's/#es_ES.UTF-8 UTF-8/es_ES.UTF-8 UTF-8/' /etc/locale.gen
locale-gen
echo "LANG=es_ES.UTF-8" > /etc/locale.conf
echo "KEYMAP=es" > /etc/vconsole.conf
echo "arch-hyprland" > /etc/hostname

# Red local
echo "127.0.0.1 localhost" >> /etc/hosts
echo "::1       localhost" >> /etc/hosts
echo "127.0.1.1 arch-hyprland.localdomain arch-hyprland" >> /etc/hosts

# Gestor de arranque (GRUB para BIOS)
grub-install --target=i386-pc /dev/sda
grub-mkconfig -o /boot/grub/grub.cfg

# Usuarios y contraseñas
echo "root:1234" | chpasswd
# Hyprland se niega a arrancar como root, así que creamos un usuario normal
useradd -m -G wheel,video,audio,vboxsf -s /bin/bash usuario
echo "usuario:1234" | chpasswd

# Dar permisos de sudo al nuevo usuario sin pedir contraseña (útil para pruebas)
echo "%wheel ALL=(ALL:ALL) NOPASSWD: ALL" >> /etc/sudoers

# Trucos para que Hyprland funcione bien en máquinas virtuales
echo "WLR_NO_HARDWARE_CURSORS=1" >> /mnt/etc/environment
echo "WLR_RENDERER_ALLOW_SOFTWARE=1" >> /mnt/etc/environment
echo "XDG_RUNTIME_DIR=/run/user/1000" >> /mnt/etc/environment

# Configurar el perfil del usuario para asegurar el entorno de sesión
cat <<EOF_USER > /mnt/home/usuario/.bash_profile
[[ -f ~/.bashrc ]] && . ~/.bashrc
export XDG_RUNTIME_DIR=/run/user/\$(id -u)
export WLR_NO_HARDWARE_CURSORS=1
export WLR_RENDERER_ALLOW_SOFTWARE=1

# Si estamos en el TTY1, arrancar Hyprland automáticamente
if [ -z "\$DISPLAY" ] && [ "\$(tty)" = "/dev/tty1" ]; then
  exec Hyprland
fi
EOF_USER
chown 1000:1000 /mnt/home/usuario/.bash_profile

# Activación de servicios al arrancar
systemctl enable NetworkManager
systemctl enable sddm
systemctl enable vboxservice
EOF

echo "=========================================================="
echo "          INSTALACIÓN DE HYPRLAND TERMINADA               "
echo "=========================================================="
echo "El sistema se reiniciará en 5 segundos."
echo "Login: usuario / Pass: 1234"
sleep 5
umount -R /mnt
reboot
