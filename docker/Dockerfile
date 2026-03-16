# ============================================================
# Dockerfile — Entorno de desarrollo para The Anthropic Gauntlet
# Imagen base con Python, Node.js y GCC para todos los módulos
# ============================================================

FROM ubuntu:22.04

# Evitar prompts interactivos durante la instalación
ENV DEBIAN_FRONTEND=noninteractive

# --- Actualizar el sistema e instalar dependencias base ---
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Python 3 y herramientas relacionadas
    python3 \
    python3-pip \
    python3-venv \
    # Node.js 18 — usamos el repositorio de NodeSource
    curl \
    ca-certificates \
    # Compilador C y herramientas de construcción
    gcc \
    make \
    libc6-dev \
    # Utilidades generales
    git \
    && rm -rf /var/lib/apt/lists/*

# --- Instalar Node.js 18 desde NodeSource ---
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

# --- Instalar paquetes de Python (pytest para testing) ---
RUN pip3 install --no-cache-dir pytest

# --- Crear enlace simbólico para que 'python' apunte a 'python3' ---
RUN ln -sf /usr/bin/python3 /usr/bin/python

# --- Establecer el directorio de trabajo ---
WORKDIR /app

# --- Comando por defecto: shell interactivo ---
CMD ["bash"]
