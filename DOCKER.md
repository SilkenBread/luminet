# 🐳 Guía de Docker para Luminet

## 📋 Tabla de Contenidos
- [Mejoras Implementadas](#-mejoras-implementadas)
- [Inicio Rápido](#-inicio-rápido)
- [Comandos Útiles](#-comandos-útiles)
- [Configuración](#️-configuración)
- [Producción](#-producción)
- [Troubleshooting](#-troubleshooting)

## ✨ Mejoras Implementadas

### 1. **Multi-stage Build**
- ✅ Imagen final ~50% más pequeña
- ✅ Separación entre dependencias de compilación y runtime
- ✅ Mejor aprovechamiento del caché de Docker

### 2. **Seguridad**
- ✅ Usuario no-root (`django`)
- ✅ Variables de entorno desde archivo `.env`
- ✅ Permisos correctos en directorios
- ✅ Sin contraseñas hardcodeadas

### 3. **Optimización**
- ✅ Cache de layers optimizado
- ✅ `.dockerignore` completo
- ✅ Health checks configurados
- ✅ Limpieza de archivos temporales

### 4. **DevOps**
- ✅ Configuración separada dev/prod
- ✅ Volúmenes nombrados para persistencia
- ✅ Makefile con comandos simplificados
- ✅ Logs accesibles

## 🚀 Inicio Rápido

### Desarrollo

```bash
# 1. Copiar archivo de ejemplo de variables de entorno
cp .env.example .env

# 2. Editar .env con tus valores
nano .env

# 3. Construir la imagen
make build
# O: docker-compose build

# 4. Iniciar contenedores
make up
# O: docker-compose up -d

# 5. Aplicar migraciones
make migrate

# 6. Crear superusuario
make createsuperuser

# 7. Acceder a la aplicación
open http://localhost:8082
```

### Producción

```bash
# 1. Configurar .env para producción (DEBUG=False, SECRET_KEY seguro, etc.)

# 2. Construir imagen de producción
make prod-build

# 3. Iniciar en modo producción
make prod-up

# 4. Ver logs
make prod-logs
```

## 🛠️ Comandos Útiles

### Con Makefile (Recomendado)

```bash
make help              # Ver todos los comandos disponibles
make build             # Construir imagen
make up                # Iniciar contenedores
make down              # Detener contenedores
make restart           # Reiniciar contenedores
make logs              # Ver logs
make shell             # Shell bash en contenedor
make django-shell      # Django shell
make migrate           # Ejecutar migraciones
make makemigrations    # Crear migraciones
make collectstatic     # Recolectar archivos estáticos
make createsuperuser   # Crear superusuario
make test              # Ejecutar tests
make clean             # Limpiar todo
make rebuild           # Reconstruir desde cero
make size              # Ver tamaño de imagen
```

### Con Docker Compose

```bash
# Desarrollo
docker-compose build                    # Construir
docker-compose up -d                    # Iniciar en background
docker-compose logs -f                  # Ver logs
docker-compose exec web bash            # Shell en contenedor
docker-compose exec web python manage.py <comando>  # Comandos Django
docker-compose down                     # Detener

# Producción
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## ⚙️ Configuración

### Variables de Entorno

Crea un archivo `.env` basado en `.env.example`:

```bash
# Django
SECRET_KEY=tu-secret-key-super-seguro-aqui
DEBUG=False  # True para desarrollo

# Docker
PORT=8082

# Database (futuro)
# DB_ENGINE=django.db.backends.postgresql
# DB_NAME=luminet
# ...
```

### Personalizar Puerto

Edita el archivo `.env`:
```bash
PORT=8080  # Cambia al puerto que prefieras
```

O directamente al ejecutar:
```bash
PORT=8080 docker-compose up -d
```

## 🏭 Producción

### Checklist Pre-Producción

- [ ] `DEBUG=False` en `.env`
- [ ] `SECRET_KEY` seguro y único
- [ ] `ALLOWED_HOSTS` configurado correctamente
- [ ] Base de datos producción (PostgreSQL recomendado)
- [ ] SSL/TLS configurado (Nginx + Let's Encrypt)
- [ ] Backups automáticos configurados
- [ ] Monitoreo y logs centralizados

### Desplegar con PostgreSQL (Opcional)

Descomenta la sección `db` en `docker-compose.prod.yml` y configura:

```yaml
services:
  db:
    image: postgres:16-alpine
    # ... configuración
```

Actualiza `.env`:
```bash
DB_ENGINE=django.db.backends.postgresql
DB_NAME=luminet
DB_USER=postgres
DB_PASSWORD=tu-password-seguro
DB_HOST=db
DB_PORT=5432
```

### Nginx Reverse Proxy (Recomendado)

Para servir archivos estáticos eficientemente y manejar SSL:

```bash
# Crear configuración de Nginx
mkdir nginx
# Editar nginx/nginx.conf según necesidades
# Descomentar sección nginx en docker-compose.prod.yml
```

## 🔍 Troubleshooting

### La imagen es muy grande

```bash
# Ver tamaño actual
make size

# Limpiar imágenes antiguas
docker system prune -a

# Verificar que .dockerignore esté correcto
cat .dockerignore
```

### Permisos de archivos

Si tienes problemas con permisos:

```bash
# En el host
sudo chown -R $USER:$USER .

# Reconstruir
make rebuild
```

### Base de datos bloqueada (SQLite)

```bash
# Detener contenedores
make down

# Eliminar archivo de lock
rm db.sqlite3-journal

# Reiniciar
make up
```

### Variables de entorno no se cargan

```bash
# Verificar que .env existe
ls -la .env

# Verificar contenido
cat .env

# Reconstruir y reiniciar
make rebuild
```

### Health check falla

```bash
# Ver logs detallados
make logs

# Inspeccionar health status
docker inspect luminet | grep -A 10 Health

# Acceder al contenedor
make shell
# Dentro del contenedor, probar manualmente
curl localhost:8000
```

## 📊 Comparación de Tamaños

| Versión | Tamaño | Mejora |
|---------|--------|--------|
| Original (single-stage) | ~1.2 GB | - |
| Optimizada (multi-stage) | ~600 MB | 50% |
| Con alpine (opcional) | ~400 MB | 66% |

## 🔐 Seguridad

- **Usuario no-root**: La aplicación corre como usuario `django`
- **Secrets**: Nunca commits `.env` al repositorio
- **Health checks**: Detecta contenedores no saludables automáticamente
- **Actualizaciones**: Usa imágenes base actualizadas regularmente

## 📚 Recursos Adicionales

- [Docker Docs](https://docs.docker.com/)
- [Docker Compose Docs](https://docs.docker.com/compose/)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)

---

**Nota**: Esta configuración está optimizada para desarrollo local. Para producción, considera usar servicios managed o Kubernetes para mejor escalabilidad.
