# Django
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.gis.geos import GEOSGeometry
from django.http import JsonResponse
from django.views import View

# local Django
from apps.infrastructure.models import Comuna

class ComunaSearchAllView(LoginRequiredMixin,View):
    def get(self, request, *args, **kwargs):
        comunas = Comuna.objects.all()
        data = []
        for comuna in comunas:
            poly = GEOSGeometry(comuna.poly)
            inverted_coords = [{"lat": lat, "lng": lon} for lon, lat in poly.coords[0]]

            items = {
                'pk': comuna.pk,
                'name': comuna.name,
                'type': comuna.type,
                'center': {"lat": comuna.centerPoint.y, "lng": comuna.centerPoint.x},
                'polygon': inverted_coords, 
            }
            data.append(items)
        return JsonResponse(data, safe=False)
    
class ComunaSearchView(View):
    def get(self, request,*args, **kwargs):
        params = request.GET.get("comunas")

        if params:
            comunaid_list = params.split(",")
            queryset = Comuna.objects.filter(id__in = [numero for numero in comunaid_list])
        else:
            queryset = Comuna.objects.all()

        data = []
        for comuna in queryset:
            poly = GEOSGeometry(comuna.poly)
            inverted_coords = [{"lat": lat, "lng": lon} for lon, lat in poly.coords[0]]

            items = {
                'pk': comuna.pk,
                'name': comuna.name,
                'type': comuna.type,
                'center': {"lat": comuna.centerPoint.y, "lng": comuna.centerPoint.x},
                'polygon': inverted_coords, 
            }
            data.append(items)
        return JsonResponse(data, safe=False)
