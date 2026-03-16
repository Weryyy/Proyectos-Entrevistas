# 🐧 Guía de Uso General de Arch Linux — Personalización y Día a Día

> **Nota:** Esta guía cubre el **uso diario** y personalización de Arch Linux. La guía de instalación se encuentra en el Módulo 6.

---

## 📦 1. Gestión de Paquetes con pacman

`pacman` es el gestor de paquetes oficial de Arch Linux. Es rápido, potente y directo — como todo en Arch.

### Comandos Esenciales

```bash
# Actualizar el sistema completo (sincronizar repos + actualizar paquetes)
sudo pacman -Syu

# Instalar un paquete
sudo pacman -S nombre-paquete

# Instalar múltiples paquetes a la vez
sudo pacman -S firefox vlc gimp

# Eliminar un paquete
sudo pacman -R nombre-paquete

# Eliminar paquete + dependencias huérfanas que ya no necesita nadie
sudo pacman -Rns nombre-paquete

# Buscar un paquete en los repositorios
pacman -Ss término-búsqueda

# Ver información detallada de un paquete
pacman -Si nombre-paquete

# Listar paquetes instalados explícitamente
pacman -Qe

# Buscar qué paquete contiene un archivo específico
pacman -F /usr/bin/nombre-archivo
```

### Limpieza de Paquetes Huérfanos

Con el tiempo, se acumulan dependencias que ya ningún paquete necesita:

```bash
# Listar paquetes huérfanos (dependencias sin padre)
pacman -Qdtq

# Eliminar todos los huérfanos de una vez
sudo pacman -Rns $(pacman -Qdtq)
```

### Limpieza de Caché

`pacman` guarda una copia de cada paquete descargado en `/var/cache/pacman/pkg/`. Esto puede ocupar varios GB con el tiempo.

```bash
# Instalar paccache (incluido en pacman-contrib)
sudo pacman -S pacman-contrib

# Mantener solo las 3 últimas versiones de cada paquete en caché
sudo paccache -r

# Mantener solo la última versión
sudo paccache -rk1

# Eliminar caché de paquetes que ya no están instalados
sudo paccache -ruk0
```

### Configuración de pacman (`/etc/pacman.conf`)

Abre el archivo con tu editor favorito y activa estas opciones útiles:

```bash
sudo nano /etc/pacman.conf
```

Busca y descomenta o añade estas líneas en la sección `[options]`:

```ini
# Descargas paralelas (mucho más rápido)
ParallelDownloads = 5

# Salida con colores (¿por qué no venía activado por defecto?)
Color

# Easter egg: la barra de progreso se convierte en un Pac-Man
ILoveCandy

# Mostrar detalles de los paquetes antes de instalar
VerbosePkgLists
```

Guarda y la próxima vez que uses `pacman`, verás la diferencia.

---

## 🏗️ 2. AUR (Arch User Repository)

### ¿Qué es el AUR?

El AUR es un repositorio **mantenido por la comunidad** donde los usuarios suben scripts de compilación (`PKGBUILD`) para software que no está en los repositorios oficiales de Arch. Aquí encuentras casi cualquier cosa: Spotify, Google Chrome, Discord, herramientas de nicho, etc.

### ⚠️ Riesgos

- Los paquetes del AUR **no** son verificados por los desarrolladores de Arch.
- Siempre revisa el `PKGBUILD` antes de instalar un paquete nuevo del AUR.
- Un paquete malicioso podría ejecutar código arbitrario en tu sistema.

### AUR Helpers: `yay` y `paru`

En lugar de compilar manualmente cada paquete del AUR, usamos helpers que automatizan el proceso:

```bash
# Instalar yay (desde el AUR, irónicamente hay que hacerlo manual la primera vez)
sudo pacman -S --needed git base-devel
git clone https://aur.archlinux.org/yay.git
cd yay
makepkg -si
cd .. && rm -rf yay

# Alternativa: instalar paru (escrito en Rust, más rápido)
git clone https://aur.archlinux.org/paru.git
cd paru
makepkg -si
cd .. && rm -rf paru
```

### Uso de yay / paru

```bash
# Instalar un paquete del AUR
yay -S google-chrome
yay -S spotify
yay -S visual-studio-code-bin

# Actualizar TODO (repos oficiales + AUR)
yay -Syu

# Buscar en repos oficiales + AUR simultáneamente
yay -Ss nombre-paquete

# Limpiar paquetes no necesarios
yay -Yc
```

> **Consejo:** `paru` y `yay` funcionan casi igual. Usa el que prefieras — ambos reemplazan a `pacman` para las operaciones diarias, ya que también manejan repos oficiales.

---

## 🐚 3. Personalización del Shell

### Zsh vs Bash

| Característica | Bash | Zsh |
|---|---|---|
| Shell por defecto en Arch | ✅ | ❌ (hay que instalar) |
| Autocompletado avanzado | Básico | Excelente |
| Temas y plugins | Manual | Oh My Zsh / Starship |
| Corrección de typos | ❌ | ✅ |
| Compatibilidad POSIX | Total | Casi total |

```bash
# Instalar Zsh
sudo pacman -S zsh

# Cambiar tu shell por defecto a Zsh
chsh -s /usr/bin/zsh

# Cerrar sesión y volver a entrar para que surta efecto
```

### Instalar Oh My Zsh

```bash
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
```

Edita `~/.zshrc` para cambiar el tema y añadir plugins:

```bash
# Tema (robbyrussell es el default, prueba "agnoster", "powerlevel10k", "fino")
ZSH_THEME="agnoster"

# Plugins útiles
plugins=(
    git
    zsh-autosuggestions
    zsh-syntax-highlighting
    sudo          # Presiona Esc dos veces para añadir sudo al comando anterior
    copypath      # Copiar ruta actual al clipboard
    web-search    # Buscar desde terminal: google "mi búsqueda"
)
```

### Alternativa: Starship Prompt

Un prompt minimalista, rápido y altamente configurable (escrito en Rust):

```bash
# Instalar Starship
sudo pacman -S starship

# Añadir al final de ~/.zshrc o ~/.bashrc
eval "$(starship init zsh)"
# o para Bash:
# eval "$(starship init bash)"
```

Configura en `~/.config/starship.toml`:

```toml
[character]
success_symbol = "[➜](bold green)"
error_symbol = "[✗](bold red)"

[directory]
truncation_length = 3
truncate_to_repo = true

[git_branch]
symbol = "🌱 "

[python]
symbol = "🐍 "

[nodejs]
symbol = "⬡ "
```

### Aliases y Funciones Útiles

Añade estos a tu `~/.zshrc` o `~/.bashrc`:

```bash
# ── Reemplazos modernos ──
alias ls='eza --icons --group-directories-first'
alias ll='eza -la --icons --group-directories-first'
alias lt='eza --tree --level=2 --icons'
alias cat='bat --style=auto'
alias grep='rg'
alias find='fd'

# ── Navegación rápida ──
alias ..='cd ..'
alias ...='cd ../..'
alias ....='cd ../../..'

# ── Git abreviado ──
alias gs='git status'
alias ga='git add'
alias gc='git commit -m'
alias gp='git push'
alias gl='git log --oneline --graph --decorate -20'
alias gd='git diff'

# ── Sistema ──
alias update='sudo pacman -Syu && yay -Syu'
alias cleanup='sudo pacman -Rns $(pacman -Qdtq) 2>/dev/null; sudo paccache -rk1'
alias ports='ss -tulanp'
alias myip='curl -s ifconfig.me'

# ── Funciones ──
# Crear directorio y entrar en él
mkcd() {
    mkdir -p "$1" && cd "$1"
}

# Extraer cualquier archivo comprimido
extract() {
    case "$1" in
        *.tar.bz2) tar xjf "$1" ;;
        *.tar.gz)  tar xzf "$1" ;;
        *.tar.xz)  tar xJf "$1" ;;
        *.bz2)     bunzip2 "$1" ;;
        *.gz)      gunzip "$1" ;;
        *.tar)     tar xf "$1" ;;
        *.zip)     unzip "$1" ;;
        *.7z)      7z x "$1" ;;
        *)         echo "'$1' no se puede extraer automáticamente" ;;
    esac
}
```

---

## 🛠️ 4. Herramientas Modernas de Terminal

Las herramientas clásicas de Unix funcionan bien, pero existen alternativas modernas que son más rápidas, más bonitas y más útiles.

### Instalación de todas de una vez

```bash
sudo pacman -S eza bat fd ripgrep btop htop tmux lazygit fzf zoxide
```

### Comparativa

| Herramienta Clásica | Alternativa Moderna | ¿Por qué cambiar? |
|---|---|---|
| `ls` | `eza` | Iconos, colores, vista de árbol, Git status integrado |
| `cat` | `bat` | Syntax highlighting, números de línea, integración con Git |
| `find` | `fd` | Más rápido, sintaxis intuitiva, respeta `.gitignore` |
| `grep` | `ripgrep` (`rg`) | Mucho más rápido, respeta `.gitignore`, colores por defecto |
| `top` | `btop` / `htop` | Interfaz visual, gráficos, mouse support |
| `cd` | `zoxide` | Recuerda directorios frecuentes: `z proyectos` |

### Ejemplos de Uso

```bash
# eza — listar con estilo
eza -la --icons --git --group-directories-first
eza --tree --level=3 --icons

# bat — ver archivos con syntax highlighting
bat archivo.py
bat --diff archivo.py  # Muestra cambios Git inline

# fd — buscar archivos fácilmente
fd "\.py$"                  # Buscar archivos Python
fd -e jpg -e png            # Buscar imágenes
fd -H ".env"                # Incluir archivos ocultos

# ripgrep — buscar texto a la velocidad de la luz
rg "TODO" --type py         # Buscar TODOs en archivos Python
rg "función" -i -C 2        # Case insensitive + 2 líneas de contexto

# fzf — buscador fuzzy interactivo
# Ctrl+R → buscar en historial de comandos con fuzzy search
# Ctrl+T → buscar archivos
vim $(fzf)                  # Abrir archivo seleccionado con fzf en vim

# zoxide — navegar por directorios con memoria
z proyectos                 # Salta al directorio más frecuente que contiene "proyectos"
zi                          # Modo interactivo con fzf
```

### tmux — Multiplexor de Terminal

`tmux` te permite tener múltiples terminales dentro de una sola ventana, dividir paneles y mantener sesiones persistentes.

```bash
# Iniciar nueva sesión
tmux new -s trabajo

# Atajos dentro de tmux (Ctrl+B es el prefijo por defecto):
# Ctrl+B c          → Nueva ventana
# Ctrl+B %          → Dividir panel verticalmente
# Ctrl+B "          → Dividir panel horizontalmente
# Ctrl+B ←/→        → Moverse entre paneles
# Ctrl+B d          → Desconectarse (la sesión sigue viva)

# Reconectarse a una sesión
tmux attach -t trabajo

# Listar sesiones activas
tmux ls
```

### lazygit — Git con Interfaz TUI

```bash
# Simplemente ejecutar dentro de un repo Git
lazygit

# Navegar con flechas, Enter para ver diffs,
# espacio para stage/unstage, c para commit, P para push
```

---

## ⚙️ 5. Gestión de Servicios con systemd

`systemd` es el sistema de inicio y gestor de servicios de Arch Linux (y la mayoría de distros modernas).

### Comandos Básicos

```bash
# Ver el estado de un servicio
sudo systemctl status nombre-servicio

# Iniciar un servicio
sudo systemctl start nombre-servicio

# Detener un servicio
sudo systemctl stop nombre-servicio

# Habilitar un servicio (que inicie automáticamente al arrancar)
sudo systemctl enable nombre-servicio

# Deshabilitar un servicio (que NO inicie al arrancar)
sudo systemctl disable nombre-servicio

# Reiniciar un servicio
sudo systemctl restart nombre-servicio

# Recargar la configuración sin reiniciar
sudo systemctl reload nombre-servicio

# Listar todos los servicios activos
systemctl list-units --type=service --state=running
```

### Ejemplos Comunes

```bash
# NetworkManager
sudo systemctl enable --now NetworkManager

# Bluetooth
sudo systemctl enable --now bluetooth

# Servidor SSH
sudo systemctl enable --now sshd

# Docker
sudo systemctl enable --now docker

# CUPS (impresoras)
sudo systemctl enable --now cups
```

### Crear un Servicio Personalizado

Crea un archivo en `/etc/systemd/system/mi-servicio.service`:

```ini
[Unit]
Description=Mi Servicio Personalizado
After=network.target

[Service]
Type=simple
User=tu-usuario
WorkingDirectory=/home/tu-usuario/mi-proyecto
ExecStart=/usr/bin/python3 /home/tu-usuario/mi-proyecto/servidor.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
# Recargar systemd para que reconozca el nuevo servicio
sudo systemctl daemon-reload

# Habilitar e iniciar
sudo systemctl enable --now mi-servicio

# Ver logs en tiempo real
journalctl -u mi-servicio -f
```

### Journalctl — Leer Logs del Sistema

```bash
# Ver todos los logs del sistema
journalctl

# Logs del boot actual
journalctl -b

# Logs de un servicio específico
journalctl -u NetworkManager

# Logs en tiempo real (como tail -f)
journalctl -f

# Logs de las últimas 2 horas
journalctl --since "2 hours ago"

# Logs con prioridad de error o superior
journalctl -p err

# Ver cuánto espacio ocupan los logs
journalctl --disk-usage

# Limpiar logs antiguos (mantener solo 500MB)
sudo journalctl --vacuum-size=500M
```

---

## 🎨 6. Personalización Visual

### Temas GTK

```bash
# Instalar herramienta de configuración de temas
sudo pacman -S lxappearance

# Instalar temas populares
sudo pacman -S arc-gtk-theme papirus-icon-theme

# Desde AUR
yay -S catppuccin-gtk-theme-macchiato

# Ejecutar la herramienta y seleccionar el tema
lxappearance
```

### Gestión de Fuentes

```bash
# Instalar fuentes esenciales
sudo pacman -S ttf-jetbrains-mono-nerd ttf-firacode-nerd noto-fonts noto-fonts-emoji

# Listar fuentes instaladas
fc-list | grep -i "JetBrains"

# Buscar una fuente específica
fc-list : family | sort | uniq | grep -i "nerd"

# Refrescar la caché de fuentes después de instalar nuevas
fc-cache -fv
```

### Configuración de Terminal — Kitty

Si usas Kitty como emulador de terminal, edita `~/.config/kitty/kitty.conf`:

```conf
# Fuente
font_family      JetBrainsMono Nerd Font
font_size        12.0
bold_font        auto
italic_font      auto

# Opacidad del fondo
background_opacity 0.92

# Tema de colores (Catppuccin Mocha)
foreground #cdd6f4
background #1e1e2e
cursor     #f5e0dc

# Colores normales
color0  #45475a
color1  #f38ba8
color2  #a6e3a1
color3  #f9e2af
color4  #89b4fa
color5  #f5c2e7
color6  #94e2d5
color7  #bac2de

# Colores brillantes
color8  #585b70
color9  #f38ba8
color10 #a6e3a1
color11 #f9e2af
color12 #89b4fa
color13 #f5c2e7
color14 #94e2d5
color15 #a6adc8
```

### Configuración de Terminal — Alacritty

Si prefieres Alacritty, edita `~/.config/alacritty/alacritty.toml`:

```toml
[font]
size = 12.0

[font.normal]
family = "JetBrainsMono Nerd Font"
style = "Regular"

[window]
opacity = 0.92
padding = { x = 8, y = 8 }

[colors.primary]
foreground = "#cdd6f4"
background = "#1e1e2e"

[colors.normal]
black   = "#45475a"
red     = "#f38ba8"
green   = "#a6e3a1"
yellow  = "#f9e2af"
blue    = "#89b4fa"
magenta = "#f5c2e7"
cyan    = "#94e2d5"
white   = "#bac2de"
```

---

## 🔧 7. Solución de Problemas Comunes

### Paquetes Rotos o Conflictos

```bash
# Forzar sincronización completa + actualización
sudo pacman -Syuu

# Si un paquete está corrupto, borrar caché y reinstalar
sudo pacman -S nombre-paquete --overwrite '*'
```

### Problemas con Keyring

Si ves errores de "firma inválida" o "clave desconocida":

```bash
# Reinicializar el keyring
sudo pacman-key --init
sudo pacman-key --populate archlinux

# Si el problema persiste
sudo pacman -S archlinux-keyring
sudo pacman -Syu
```

### Drivers de Nvidia en Arch

```bash
# Identificar tu tarjeta gráfica
lspci -k | grep -A 2 -E "(VGA|3D)"

# Instalar drivers propietarios de Nvidia (para GPUs modernas)
sudo pacman -S nvidia nvidia-utils nvidia-settings

# Para GPUs más antiguas (serie 700 o anterior)
# Consulta la wiki: https://wiki.archlinux.org/title/NVIDIA

# Regenerar initramfs después de instalar
sudo mkinitcpio -P

# Reiniciar
reboot

# Verificar que funciona
nvidia-smi
```

### Problemas con Audio

```bash
# Instalar PipeWire (reemplazo moderno de PulseAudio)
sudo pacman -S pipewire pipewire-alsa pipewire-pulse pipewire-jack wireplumber

# Habilitar
systemctl --user enable --now pipewire pipewire-pulse wireplumber

# Herramienta gráfica para controlar volumen
sudo pacman -S pavucontrol
```

### Problemas con WiFi

```bash
# Verificar que NetworkManager está corriendo
sudo systemctl status NetworkManager

# Listar redes disponibles
nmcli device wifi list

# Conectarse a una red
nmcli device wifi connect "NombreRedWiFi" password "TuContraseña"

# Ver conexiones activas
nmcli connection show --active
```

### 📖 La Regla de Oro: Leer la Arch Wiki

La [Arch Wiki](https://wiki.archlinux.org/) es **el mejor recurso de documentación en el mundo Linux**. No importa qué problema tengas, la wiki probablemente tiene la respuesta:

```
https://wiki.archlinux.org/title/NombreDelTema
```

> **Consejo:** Incluso usuarios de Ubuntu, Fedora y otras distros consultan la Arch Wiki. Es así de buena.

---

## 🚀 8. Flujo de Trabajo Productivo

### Tiling Window Managers vs Floating Window Managers

| Tipo | Ejemplos | ¿Para quién? |
|---|---|---|
| **Tiling WM** | Hyprland, Sway, i3, bspwm | Usuarios que quieren control total con teclado. Las ventanas se organizan automáticamente sin superponerse. |
| **Floating WM** | Openbox, Fluxbox | Estilo tradicional con ventanas flotantes, pero más ligero que un DE completo. |
| **Desktop Environments** | KDE, GNOME, XFCE | Experiencia completa "out of the box" con barra de tareas, menú, configuración gráfica. |

### Configuración de un Tiling WM (ejemplo con Hyprland)

```bash
# Instalar Hyprland (Wayland)
sudo pacman -S hyprland waybar wofi dunst

# La configuración vive en:
# ~/.config/hypr/hyprland.conf
```

Reglas de ventanas útiles en `hyprland.conf`:

```conf
# Asignar aplicaciones a workspaces específicos
windowrulev2 = workspace 1, class:^(firefox)$
windowrulev2 = workspace 2, class:^(code)$
windowrulev2 = workspace 3, class:^(discord)$
windowrulev2 = workspace 4, class:^(spotify)$

# Hacer que ciertos diálogos sean flotantes
windowrulev2 = float, class:^(pavucontrol)$
windowrulev2 = float, title:^(Archivo)$

# Atajos de teclado esenciales
bind = SUPER, Return, exec, kitty         # Abrir terminal
bind = SUPER, Q, killactive               # Cerrar ventana
bind = SUPER, D, exec, wofi --show drun   # Lanzador de apps
bind = SUPER, 1, workspace, 1             # Ir a workspace 1
bind = SUPER, 2, workspace, 2             # Ir a workspace 2
bind = SUPER SHIFT, 1, movetoworkspace, 1 # Mover ventana a workspace 1
```

### Herramientas de Productividad Esenciales

```bash
# Clipboard manager — historial del portapapeles
sudo pacman -S wl-clipboard cliphist
# Uso: Ctrl+Super+V para ver historial

# Capturas de pantalla
sudo pacman -S grim slurp
# Captura de área seleccionada:
grim -g "$(slurp)" ~/Capturas/captura.png

# Grabación de pantalla
sudo pacman -S wf-recorder
# Grabar:
wf-recorder -g "$(slurp)" -f grabacion.mp4
# Detener: Ctrl+C

# Notificaciones
sudo pacman -S dunst
# Probar: notify-send "Hola" "Esto es una notificación"

# Wallpapers
sudo pacman -S swww
swww init
swww img ~/Wallpapers/mi-fondo.jpg --transition-type wipe

# Barra de estado
sudo pacman -S waybar
# Configurar en ~/.config/waybar/config y ~/.config/waybar/style.css

# Lanzador de aplicaciones
sudo pacman -S wofi
# o rofi para X11:
sudo pacman -S rofi
```

### Flujo de Trabajo Diario Recomendado

```bash
# 1. Actualizar el sistema (hazlo al menos una vez por semana)
yay -Syu

# 2. Abrir tu entorno con un solo comando
# Puedes crear un script ~/.local/bin/workspace.sh
#!/bin/bash
tmux new-session -d -s dev
tmux send-keys -t dev "cd ~/proyectos && nvim" Enter
tmux new-window -t dev -n "server"
tmux send-keys -t dev:server "cd ~/proyectos && npm run dev" Enter
tmux new-window -t dev -n "git"
tmux send-keys -t dev:git "cd ~/proyectos && lazygit" Enter
tmux attach -t dev

# 3. Backup periódico de tus dotfiles
# Usa GNU Stow o un repo Git para sincronizar configuraciones
mkdir -p ~/dotfiles/{kitty,hypr,zsh,nvim,waybar}
# Enlazar: stow -t ~ kitty
```

---

## 📚 Recursos

- [Arch Wiki — General Recommendations](https://wiki.archlinux.org/title/General_recommendations)
- [Arch Wiki — Pacman Tips and Tricks](https://wiki.archlinux.org/title/Pacman/Tips_and_tricks)
- [Arch Wiki — AUR](https://wiki.archlinux.org/title/Arch_User_Repository)
- [Arch Wiki — Hyprland](https://wiki.archlinux.org/title/Hyprland)
- [Catppuccin Theme](https://github.com/catppuccin/catppuccin) — Tema de colores pastel para todo
- [r/unixporn](https://www.reddit.com/r/unixporn/) — Inspiración visual para personalización Linux
