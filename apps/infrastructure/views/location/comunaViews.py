# Django
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views import View

# local Django
from apps.infrastructure.models import Comuna


def _serialize_comuna(comuna):
    if not comuna.poly:
        return None
    inverted_coords = [{"lat": lat, "lng": lon} for lon, lat in comuna.poly.coords[0]]
    center = comuna.centerPoint
    return {
        "pk": comuna.pk,
        "name": comuna.name,
        "type": comuna.type,
        "center": {"lat": center.y, "lng": center.x} if center else None,
        "polygon": inverted_coords,
    }


class ComunaSearchAllView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        comunas = Comuna.objects.only("id", "name", "type", "centerPoint", "poly")
        data = [c for c in (_serialize_comuna(c) for c in comunas) if c]
        return JsonResponse(data, safe=False)


class ComunaSearchView(View):
    def get(self, request, *args, **kwargs):
        params = request.GET.get("comunas")
        queryset = Comuna.objects.only("id", "name", "type", "centerPoint", "poly")
        if params:
            comunaid_list = [int(n) for n in params.split(",") if n.strip().isdigit()]
            queryset = queryset.filter(id__in=comunaid_list)

        data = [c for c in (_serialize_comuna(c) for c in queryset) if c]
        return JsonResponse(data, safe=False)
