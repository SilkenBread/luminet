# Django
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views import View

# local Django
from apps.infrastructure.models import District, Comuna


def _serialize_district(district):
    if not district.poly:
        return None
    polygons = []
    for polygon in district.poly:
        inverted_coords = [{"lat": lat, "lng": lon} for lon, lat in polygon[0].coords]
        polygons.append(inverted_coords)
    return {
        "pk": district.pk,
        "name": district.name,
        "estrato": district.estrato,
        "cod_unico": district.cod_unico,
        "polygon": polygons,
        "fk_comuna": district.fk_comuna_id,
    }


class DistrictSearchView(View):
    def get(self, request, *args, **kwargs):
        districts = District.objects.only(
            "id", "name", "estrato", "cod_unico", "poly", "fk_comuna_id"
        )
        data = [d for d in (_serialize_district(d) for d in districts) if d]
        return JsonResponse(data, safe=False)


class DistrictSearchByComuna(View):
    def get(self, request, comuna, *args, **kwargs):
        comuna_obj = get_object_or_404(Comuna, pk=comuna)
        districts = District.objects.filter(fk_comuna=comuna_obj).only(
            "id", "name", "estrato", "cod_unico", "poly", "fk_comuna_id"
        )
        data = [d for d in (_serialize_district(d) for d in districts) if d]
        return JsonResponse(data, safe=False)