# 🌍 GeoDjango Setup para Luminet

## 📋 Dependencias Instaladas

Tu contenedor Docker ya incluye todas las dependencias necesarias para GeoDjango:

### Bibliotecas Geoespaciales
- ✅ **GDAL** (Geospatial Data Abstraction Library) - versión automática según Debian
- ✅ **GEOS** (Geometry Engine Open Source) - `libgeos-c1t64`
- ✅ **PROJ** (Cartographic Projections Library) - `libproj25`
- ✅ **binutils** - Para operaciones de bajo nivel

### Herramientas CLI
- ✅ **gdal-bin** - Comandos `ogr2ogr`, `gdalinfo`, etc.

## 🚀 Configurar GeoDjango en tu Proyecto

### 1. Instalar Django GIS

Agrega a `requirements.txt`:
```txt
# GeoDjango (ya tienes Django y leaflet)
psycopg2-binary==2.9.10  # Si vas a usar PostgreSQL con PostGIS
```

### 2. Actualizar settings.py

```python
# config/settings.py

# Agregar django.contrib.gis
INSTALLED_APPS = [
    # ... apps existentes ...
    'django.contrib.gis',  # ✅ Agregar esto
]

# Si usas SQLite con SpatiaLite (desarrollo)
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.spatialite',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Si usas PostgreSQL con PostGIS (producción recomendada)
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.contrib.gis.db.backends.postgis',
#         'NAME': env('DB_NAME', default='luminet'),
#         'USER': env('DB_USER', default='postgres'),
#         'PASSWORD': env('DB_PASSWORD', default='postgres'),
#         'HOST': env('DB_HOST', default='db'),
#         'PORT': env('DB_PORT', default='5432'),
#     }
# }

# Configuración de Leaflet (ya lo tienes instalado)
LEAFLET_CONFIG = {
    'DEFAULT_CENTER': (4.6097, -74.0817),  # Bogotá
    'DEFAULT_ZOOM': 12,
    'MIN_ZOOM': 3,
    'MAX_ZOOM': 18,
    'TILES': [
        ('OpenStreetMap', 
         'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
         {'attribution': '© OpenStreetMap contributors'}),
    ],
}
```

### 3. Crear Modelos con Geometría

```python
# apps/core/models.py o crear apps/locations/models.py

from django.contrib.gis.db import models as gis_models
from django.db import models

class Location(models.Model):
    """Modelo para almacenar ubicaciones geoespaciales"""
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Campos geoespaciales
    point = gis_models.PointField(
        help_text="Coordenadas de punto (lat, lon)",
        null=True,
        blank=True
    )
    
    polygon = gis_models.PolygonField(
        help_text="Área o polígono",
        null=True,
        blank=True
    )
    
    # Metadatos
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Ubicación"
        verbose_name_plural = "Ubicaciones"
    
    def __str__(self):
        return self.name
```

### 4. Admin con Mapa Interactivo

```python
# apps/core/admin.py

from django.contrib.gis import admin as gis_admin
from django.contrib import admin
from .models import Location

@admin.register(Location)
class LocationAdmin(gis_admin.GISModelAdmin):
    """Admin con mapa interactivo de Leaflet"""
    
    list_display = ('name', 'created_at')
    search_fields = ('name', 'description')
    
    # Configuración del mapa en admin
    default_lon = -74.0817  # Bogotá
    default_lat = 4.6097
    default_zoom = 12
    
    # Usar widget de OpenLayers (por defecto) o Leaflet
    # gis_widget = gis_admin.OSMGeoAdmin.default_widget
```

### 5. Ejecutar Migraciones

```bash
# Dentro del contenedor
make migrate

# O directamente
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
```

## 🗺️ Usar con Leaflet en Templates

### Template de Mapa

```html
<!-- templates/location_map.html -->
{% load leaflet_tags %}

<!DOCTYPE html>
<html>
<head>
    <title>Mapa de Ubicaciones</title>
    {% leaflet_js %}
    {% leaflet_css %}
</head>
<body>
    <h1>Ubicaciones</h1>
    
    <!-- Contenedor del mapa -->
    {% leaflet_map "main-map" %}
    
    <script>
        // Personalizar mapa después de carga
        window.addEventListener('map:init', function (e) {
            const map = e.detail.map;
            
            // Agregar marcador
            const marker = L.marker([4.6097, -74.0817]).addTo(map);
            marker.bindPopup("<b>Bogotá</b><br>Colombia").openPopup();
            
            // Agregar polígono
            const polygon = L.polygon([
                [4.61, -74.08],
                [4.61, -74.07],
                [4.60, -74.07],
                [4.60, -74.08]
            ]).addTo(map);
            polygon.bindPopup("Área de ejemplo");
        });
    </script>
</body>
</html>
```

### View para Mapa

```python
# apps/core/views/maps.py

from django.views.generic import TemplateView
from apps.core.models import Location

class LocationMapView(TemplateView):
    template_name = 'location_map.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['locations'] = Location.objects.filter(point__isnull=False)
        return context
```

## 🐘 Usar PostgreSQL + PostGIS (Producción)

### 1. Actualizar docker-compose.yml

Descomentar la sección de PostgreSQL en `docker-compose.prod.yml`:

```yaml
services:
  db:
    image: postgis/postgis:16-3.5-alpine
    container_name: luminet_db
    restart: always
    environment:
      - POSTGRES_DB=luminet
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=${DB_PASSWORD:-postgres}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - luminet-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  web:
    depends_on:
      db:
        condition: service_healthy

volumes:
  postgres_data:
    name: luminet_postgres_data
```

### 2. Actualizar .env

```bash
DB_ENGINE=django.contrib.gis.db.backends.postgis
DB_NAME=luminet
DB_USER=postgres
DB_PASSWORD=tu-password-seguro
DB_HOST=db
DB_PORT=5432
```

### 3. Agregar psycopg2 a requirements.txt

```bash
# Dentro del contenedor
docker-compose exec web pip install psycopg2-binary==2.9.10

# Luego actualiza requirements.txt:
docker-compose exec web pip freeze > requirements.txt
```

### 4. Iniciar con PostgreSQL

```bash
# Reconstruir con nuevas dependencias
make rebuild

# Crear base de datos y extensiones
docker-compose exec db psql -U postgres -d luminet -c "CREATE EXTENSION postgis;"
docker-compose exec db psql -U postgres -d luminet -c "CREATE EXTENSION postgis_topology;"

# Migrar
make migrate
```

## 🧪 Verificar Instalación de GeoDjango

### Verificar en Django Shell

```python
# Acceder al shell
make django-shell

# Verificar GDAL
from django.contrib.gis.gdal import HAS_GDAL
print(f"GDAL disponible: {HAS_GDAL}")

# Verificar GEOS
from django.contrib.gis.geos import HAS_GEOS
print(f"GEOS disponible: {HAS_GEOS}")

# Verificar versiones
from django.contrib.gis import gdal, geos
print(f"GDAL versión: {gdal.gdal_version()}")
print(f"GEOS versión: {geos.geos_version()}")

# Crear un punto de prueba
from django.contrib.gis.geos import Point
bogota = Point(-74.0817, 4.6097, srid=4326)
print(f"Punto Bogotá: {bogota}")
print(f"Coordenadas: Lat {bogota.y}, Lon {bogota.x}")
```

### Script de Verificación

```python
# Crear archivo: scripts/check_geodjango.py

from django.contrib.gis import gdal, geos
from django.contrib.gis.geos import Point, Polygon

def check_geodjango():
    print("=" * 50)
    print("🌍 Verificación de GeoDjango")
    print("=" * 50)
    
    # GDAL
    try:
        print(f"✅ GDAL: {gdal.gdal_version()}")
    except Exception as e:
        print(f"❌ GDAL: {e}")
    
    # GEOS
    try:
        print(f"✅ GEOS: {geos.geos_version()}")
    except Exception as e:
        print(f"❌ GEOS: {e}")
    
    # Crear geometrías de prueba
    try:
        point = Point(-74.0817, 4.6097, srid=4326)
        print(f"✅ Punto creado: {point}")
        
        poly = Polygon((
            (-74.08, 4.60),
            (-74.08, 4.61),
            (-74.07, 4.61),
            (-74.07, 4.60),
            (-74.08, 4.60),
        ))
        print(f"✅ Polígono creado con área: {poly.area:.6f}")
        
    except Exception as e:
        print(f"❌ Error creando geometrías: {e}")
    
    print("=" * 50)

if __name__ == "__main__":
    check_geodjango()
```

Ejecutar:
```bash
docker-compose exec web python scripts/check_geodjango.py
```

## 📚 Consultas Geoespaciales Útiles

```python
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D  # Distance
from apps.core.models import Location

# Buscar ubicaciones cerca de un punto (dentro de 5km)
centro = Point(-74.0817, 4.6097, srid=4326)
cercanas = Location.objects.filter(
    point__distance_lte=(centro, D(km=5))
)

# Ordenar por distancia
ordenadas = Location.objects.filter(
    point__isnull=False
).distance(centro).order_by('distance')

# Ubicaciones dentro de un polígono
from django.contrib.gis.geos import Polygon
area = Polygon(((
    (-74.08, 4.60),
    (-74.08, 4.61),
    (-74.07, 4.61),
    (-74.07, 4.60),
    (-74.08, 4.60),
)))
dentro = Location.objects.filter(point__within=area)

# Calcular área o longitud
for loc in Location.objects.filter(polygon__isnull=False):
    print(f"{loc.name}: {loc.polygon.area} unidades cuadradas")
```

## 🔧 Troubleshooting

### Error: "GDAL library not found"

```bash
# Verificar instalación en contenedor
docker-compose exec web which gdalinfo
docker-compose exec web gdalinfo --version

# Si falla, reconstruir:
make rebuild
```

### Error: "SpatiaLite not available"

Para SQLite con SpatiaLite:

```bash
# Instalar en stage runtime del Dockerfile
RUN apt-get install -y libsqlite3-mod-spatialite
```

### Error de permisos con archivos .shp

```bash
# Asegurar permisos en media/
docker-compose exec web chown -R django:django /luminet/media
```

## 📖 Recursos

- [GeoDjango Docs](https://docs.djangoproject.com/en/5.1/ref/contrib/gis/)
- [PostGIS Docs](https://postgis.net/documentation/)
- [Leaflet Docs](https://leafletjs.com/reference.html)
- [Django Leaflet](https://django-leaflet.readthedocs.io/)

---

**¡GeoDjango está listo para usar!** 🌍✨
