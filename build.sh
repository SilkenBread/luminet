#!/usr/bin/env bash
# Build script para preparar la aplicación Django
# Se ejecuta durante la construcción de la imagen Docker

set -o errexit  # Exit on error
set -o pipefail # Exit on pipe failure
set -o nounset  # Exit on undefined variable

echo "🔧 Iniciando build script..."

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Recolectar archivos estáticos
echo -e "${YELLOW}📦 Recolectando archivos estáticos...${NC}"
python manage.py collectstatic --no-input --clear

# Aplicar migraciones (solo en build si es necesario)
# Comentado porque es mejor ejecutarlo en tiempo de ejecución
# echo -e "${YELLOW}🗄️  Aplicando migraciones de base de datos...${NC}"
# python manage.py migrate --noinput

echo -e "${GREEN}✅ Build completado exitosamente${NC}"

