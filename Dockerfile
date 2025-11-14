# ========================================
# Stage 1: Builder - Instalar dependencias
# ========================================
FROM python:3.12-slim as builder

# Variables de entorno para optimización
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /luminet

# Instalar dependencias del sistema necesarias para compilación
# Incluye GDAL para GeoDjango
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libgdal-dev \
    gdal-bin \
    binutils \
    libproj-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar solo requirements para aprovechar cache de Docker
COPY requirements.txt .

# Instalar dependencias de Python en un directorio virtual
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt

# ========================================
# Stage 2: Runtime - Imagen final optimizada
# ========================================
FROM python:3.12-slim

# Variables de entorno
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH" \
    DJANGO_SETTINGS_MODULE=config.settings

WORKDIR /luminet

# Instalar dependencias runtime necesarias para GeoDjango
# Nota: Los nombres de paquetes pueden variar según la versión de Debian
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libpq5 \
    gdal-bin \
    libgeos-c1t64 \
    libproj25 \
    binutils \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copiar el entorno virtual desde el builder
COPY --from=builder /opt/venv /opt/venv

# Crear usuario no-root para mayor seguridad
RUN groupadd -r django && \
    useradd -r -g django -d /luminet -s /sbin/nologin django && \
    chown -R django:django /luminet

# Copiar el proyecto
COPY --chown=django:django . .

# Preparar el script build.sh
RUN chmod +x build.sh

# Crear directorios necesarios con permisos correctos
RUN mkdir -p /luminet/staticfiles /luminet/media && \
    chown -R django:django /luminet/staticfiles /luminet/media

# Cambiar a usuario no-root
USER django

# Exponer puerto
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000').read()" || exit 1

# Comando por defecto
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-"]
