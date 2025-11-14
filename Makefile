# Makefile para simplificar comandos de Docker y Django

.PHONY: help build up down restart logs shell migrate collectstatic createsuperuser test clean

help: ## Mostrar esta ayuda
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

build: ## Construir la imagen Docker
	docker-compose build

up: ## Iniciar contenedores en modo desarrollo
	docker-compose up -d

down: ## Detener y eliminar contenedores
	docker-compose down

restart: ## Reiniciar contenedores
	docker-compose restart

logs: ## Ver logs de los contenedores
	docker-compose logs -f

shell: ## Abrir shell en el contenedor
	docker-compose exec web bash

django-shell: ## Abrir Django shell
	docker-compose exec web python manage.py shell

startapp: ## Crear nueva app Django (uso: make startapp name=nombre_app)
	@if [ -z "$(name)" ]; then \
		echo "Error: Debes especificar el nombre de la app"; \
		echo "Uso: make startapp name=nombre_app"; \
		exit 1; \
	fi
	docker-compose exec web python manage.py startapp $(name)
	@echo "✅ App '$(name)' creada en el directorio actual"
	@echo "📝 No olvides agregar 'apps.$(name)' a INSTALLED_APPS en settings.py"

migrate: ## Ejecutar migraciones
	docker-compose exec web python manage.py migrate

makemigrations: ## Crear migraciones
	docker-compose exec web python manage.py makemigrations

collectstatic: ## Recolectar archivos estáticos
	docker-compose exec web python manage.py collectstatic --noinput

createsuperuser: ## Crear superusuario
	docker-compose exec web python manage.py createsuperuser

test: ## Ejecutar tests
	docker-compose exec web python manage.py test

clean: ## Limpiar contenedores, volúmenes e imágenes no usadas
	docker-compose down -v
	docker system prune -f

rebuild: ## Reconstruir y reiniciar contenedores
	docker-compose down
	docker-compose build --no-cache
	docker-compose up -d

prod-up: ## Iniciar en modo producción
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

prod-build: ## Construir para producción
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

prod-logs: ## Ver logs de producción
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml logs -f

size: ## Mostrar tamaño de la imagen
	docker images luminet:latest --format "{{.Repository}}:{{.Tag}}\t{{.Size}}"
