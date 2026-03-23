#!/bin/bash
# -----------------------------------------------------------------------------
# ARCH LINUX AUTOMATED INSTALLATION SCRIPT (BIOS/IDE)
# Script de auto-instalación para el Módulo 14 - Arch Linux Project
# -----------------------------------------------------------------------------

set -e # Detener en caso de error

echo "#####################################################"
echo "# INICIANDO INSTALACIÓN AUTOMATIZADA DE ARCH LINUX #"
echo "#####################################################"

# 1. Configuración de Teclado
echo "[-] Configurando teclado en español..."
loadkeys es

# 2. Particionado de Disco (/dev/sda - 20GB sugerido)
# Borra la tabla de particiones y crea una primaria bootable (BIOS)
echo "[-] Particionando /dev/sda (BIOS/MBR)..."
sfdisk /dev/sda <<EOF
label: dos
device: /dev/sda
unit: sectors

/dev/sda1 : start= 2048, type=83, bootable
EOF

# 3. Formateo y Montaje
echo "[-] Formateando /dev/sda1 (ext4)..."
mkfs.ext4 /dev/sda1
mount /dev/sda1 /mnt

# 4. Instalación de paquetes base
echo "[-] Instalando paquetes base (esto tardará unos minutos)..."
pacstrap /mnt base linux linux-firmware base-devel nano networkmanager grub

# 5. Generar FSTAB
echo "[-] Generando fstab..."
genfstab -U /mnt >> /mnt/etc/fstab

# 6. Configuración dentro del CHROOT
echo "[-] Entrando en entorno chroot para configuración final..."
arch-chroot /mnt /bin/bash <<EOF
# Zona Horaria
ln -sf /usr/share/zoneinfo/Europe/Madrid /etc/localtime
hwclock --systohc

# Localización (Español)
sed -i 's/#es_ES.UTF-8 UTF-8/es_ES.UTF-8 UTF-8/' /etc/locale.gen
locale-gen
echo "LANG=es_ES.UTF-8" > /etc/locale.conf
echo "KEYMAP=es" > /etc/vconsole.conf

# Hostname
echo "arch-pro-vm" > /etc/hostname

# Red
systemctl enable NetworkManager

# Usuario Root (Password: arch123)
echo "root:arch123" | chpasswd

# Bootloader (GRUB)
echo "[-] Instalando GRUB..."
grub-install --target=i386-pc /dev/sda
grub-mkconfig -o /boot/grub/grub.cfg
EOF

echo "#####################################################"
echo "#   INSTALACIÓN COMPLETADA CON ÉXITO                #"
echo "#####################################################"
echo "Usuario: root"
echo "Password: arch123"
echo "El sistema se reiniciará automáticamente en 5 segundos..."
sleep 5
umount -R /mnt
reboot
