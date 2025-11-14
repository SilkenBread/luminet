#!/bin/bash

# Script de inicio para Luminet Docker
# Facilita la configuración inicial del proyecto

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "╔═══════════════════════════════════════╗"
echo "║     🚀 Luminet Docker Setup 🚀       ║"
echo "╔═══════════════════════════════════════╝"
echo -e "${NC}"

# Verificar que Docker está corriendo
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Error: Docker no está corriendo${NC}"
    echo "Por favor, inicia Docker Desktop y vuelve a ejecutar este script."
    exit 1
fi

echo -e "${GREEN}✅ Docker está corriendo${NC}\n"

# Verificar si existe .env
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  No se encontró archivo .env${NC}"
    echo "Creando .env desde .env.example..."
    
    if [ -f .env.example ]; then
        cp .env.example .env
        echo -e "${GREEN}✅ Archivo .env creado${NC}"
        echo -e "${YELLOW}⚠️  IMPORTANTE: Edita el archivo .env con tus valores antes de continuar${NC}"
        echo "Presiona Enter para continuar o Ctrl+C para salir y editar .env..."
        read
    else
        echo -e "${RED}❌ Error: .env.example no existe${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✅ Archivo .env encontrado${NC}\n"
fi

# Preguntar si debe construir la imagen
echo -e "${BLUE}🏗️  ¿Deseas construir la imagen Docker?${NC}"
echo "1) Sí, construir imagen (recomendado para primera vez)"
echo "2) No, usar imagen existente"
read -p "Selecciona una opción (1/2): " build_option

if [ "$build_option" = "1" ]; then
    echo -e "\n${YELLOW}📦 Construyendo imagen Docker...${NC}"
    docker-compose build
    echo -e "${GREEN}✅ Imagen construida exitosamente${NC}\n"
fi

# Iniciar contenedores
echo -e "${YELLOW}🚀 Iniciando contenedores...${NC}"
docker-compose up -d

# Esperar a que el contenedor esté listo
echo -e "${YELLOW}⏳ Esperando que el contenedor esté listo...${NC}"
sleep 5

# Verificar que el contenedor está corriendo
if docker-compose ps | grep -q "luminet.*Up"; then
    echo -e "${GREEN}✅ Contenedor iniciado correctamente${NC}\n"
else
    echo -e "${RED}❌ Error: El contenedor no se inició correctamente${NC}"
    echo "Mostrando logs:"
    docker-compose logs
    exit 1
fi

# Preguntar si debe ejecutar migraciones
echo -e "${BLUE}🗄️  ¿Deseas ejecutar migraciones de la base de datos?${NC}"
read -p "(s/n): " run_migrations

if [ "$run_migrations" = "s" ] || [ "$run_migrations" = "S" ]; then
    echo -e "${YELLOW}Ejecutando migraciones...${NC}"
    docker-compose exec web python manage.py migrate
    echo -e "${GREEN}✅ Migraciones completadas${NC}\n"
fi

# Preguntar si debe crear superusuario
echo -e "${BLUE}👤 ¿Deseas crear un superusuario?${NC}"
read -p "(s/n): " create_superuser

if [ "$create_superuser" = "s" ] || [ "$create_superuser" = "S" ]; then
    echo -e "${YELLOW}Creando superusuario...${NC}"
    docker-compose exec web python manage.py createsuperuser
fi

# Obtener el puerto
PORT=$(grep PORT .env 2>/dev/null | cut -d '=' -f2 || echo "8082")

# Mensaje final
echo -e "\n${GREEN}╔═══════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   ✅ Setup completado exitosamente    ║${NC}"
echo -e "${GREEN}╔═══════════════════════════════════════╝${NC}\n"

echo -e "${BLUE}📍 Información importante:${NC}"
echo -e "   - URL: ${GREEN}http://localhost:${PORT}${NC}"
echo -e "   - Admin: ${GREEN}http://localhost:${PORT}/admin${NC}"
echo -e "   - Contenedor: ${GREEN}luminet${NC}"
echo ""
echo -e "${BLUE}🛠️  Comandos útiles:${NC}"
echo -e "   - Ver logs:          ${YELLOW}make logs${NC} o ${YELLOW}docker-compose logs -f${NC}"
echo -e "   - Detener:           ${YELLOW}make down${NC} o ${YELLOW}docker-compose down${NC}"
echo -e "   - Reiniciar:         ${YELLOW}make restart${NC} o ${YELLOW}docker-compose restart${NC}"
echo -e "   - Shell:             ${YELLOW}make shell${NC} o ${YELLOW}docker-compose exec web bash${NC}"
echo -e "   - Ver todos:         ${YELLOW}make help${NC}"
echo ""
echo -e "${BLUE}📚 Documentación: ${YELLOW}DOCKER.md${NC}"
echo ""
echo -e "${GREEN}¡Feliz desarrollo! 🎉${NC}\n"
