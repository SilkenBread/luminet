# standard library
import time

# Django
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views import View
from django.contrib.gis.geos import GEOSGeometry

# local Django
from apps.infrastructure.models import District, Comuna

class DistrictSearchView(View):
    def get(self, request, *args, **kwargs):
        start_time = time.time()
        districts = District.objects.all()

        data = []
        for district in districts:
            poly = GEOSGeometry(district.poly)
            polygons = []

            for polygon in poly:
                inverted_coords = [{"lat": lat, "lng": lon} for lon, lat in polygon[0].coords]
                polygons.append(inverted_coords)                

            items = {
                'pk': district.pk,
                'name': district.name,
                'estrato': district.estrato,
                'cod_unico': district.cod_unico,
                'polygon': polygons,  # Store the list of polygons
                'fk_comuna': district.fk_comuna_id
            }
            data.append(items)
        return JsonResponse(data, safe=False)

class DistrictSearchByComuna(View):
    def get(self, request, comuna, *args, **kwargs):
        comuna_obj = get_object_or_404(Comuna, pk=comuna)
        districts = District.objects.filter(fk_comuna=comuna_obj)

        data = []
        for district in districts:
            poly = GEOSGeometry(district.poly)
            polygons = []

            for polygon in poly:
                inverted_coords = [{"lat": lat, "lng": lon} for lon, lat in polygon[0].coords]
                polygons.append(inverted_coords)                

            items = {
                'pk': district.pk,
                'name': district.name,
                'estrato': district.estrato,
                'cod_unico': district.cod_unico,
                'polygon': polygons,  # Store the list of polygons
                'fk_comuna': district.fk_comuna_id
            }
            data.append(items)
        return JsonResponse(data, safe=False)