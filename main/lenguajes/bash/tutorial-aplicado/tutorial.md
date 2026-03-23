# 🐚 Tutorial Aplicado: Bash en el Módulo 14

En el **Módulo 14 (Instalador de Arch)**, Bash deja de ser una utilidad para convertirse en la herramienta principal de **Infraestructura como Código (IaC)**.

---

## 🏗️ Patrones Avanzados Utilizados

### 1. El uso de Here-Docs (`EOF`)
En el instalador de Arch, nos permite enviar múltiples líneas a un comando interactivo, como `sfdisk` para particionar o `arch-chroot` para configurar el sistema:
```bash
arch-chroot /mnt /bin/bash <<EOF
# Comandos ejecutados dentro de la nueva instalación
passwd <<PASSWORD_EOF
1234
1234
PASSWORD_EOF
EOF
```

### 2. Gestión de Errores con `set -e`
En scripts críticos como una instalación de sistema operativo, queremos que todo se detenga si algo falla:
```bash
set -e
# Si un comando falla, el script muere aquí
```

### 3. Redirección y Pipes (`|`)
Esenciales para descargar y ejecutar scripts en un solo paso:
```bash
curl -L https://tinyurl.com/arch-weryyy-raw | bash
```
*Cuidado: Siempre revisa los scripts antes de hacer pipe a bash por seguridad.*

### 4. Automatización de Sistemas (`systemctl`)
Bash es el puente para hablar con `systemd`:
```bash
systemctl enable --now sddm
```

---

## 🚀 Ejercicios Sugeridos
1. Analiza el archivo `auto_install_hyprland.sh` y localiza cómo se crean las particiones con `sfdisk`.
2. Modifica el script para que pregunte por el nombre del usuario en lugar de usar "usuario" por defecto.
3. Intenta añadir una comprobación de red al principio del script usando `ping`.
