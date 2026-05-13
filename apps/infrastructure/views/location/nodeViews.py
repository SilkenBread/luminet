import json
import time

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.gis.geos import GEOSGeometry
from django.core.serializers import serialize
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View

from apps.infrastructure.models import District, Node
from apps.mixins import APIPermissionValidation


def _serialize_node(node):
    """Serialización canónica de un Nodo para respuestas AJAX (sin geometría binaria)."""
    return {
        "pk": node.pk,
        "id": node.pk,
        "painting_code": node.painting_code,
        "comuna": node.fk_district.fk_comuna.name if node.fk_district else None,
        "district": node.fk_district.name if node.fk_district else None,
        "fk_district": node.fk_district_id,
        "lng": node.location.x if node.location else None,
        "lat": node.location.y if node.location else None,
    }


class NodeInDistrictView(LoginRequiredMixin, APIPermissionValidation, View):
    """Buscar todos los nodos de un barrio."""
    permission_required = ["infrastructure.view_node"]

    def get(self, request, *args, **kwargs):
        start_time = time.time()
        try:
            # Aceptamos ambos nombres para no romper consumidores legacy
            district_id = request.GET.get("district") or request.GET.get("disrict")
            if not district_id:
                raise ValueError("Falta el parámetro 'district'.")

            nodes = (
                Node.objects
                .select_related("fk_district__fk_comuna")
                .filter(fk_district_id=int(district_id))
            )
            data = {"type": "success", "data": [_serialize_node(n) for n in nodes]}
        except Exception as e:
            data = {"type": "error", "msg": str(e)}
        data["time"] = str(time.time() - start_time)
        return JsonResponse(data, safe=False)


class NodeSearchPaintingCode(LoginRequiredMixin, APIPermissionValidation, View):
    """Buscar nodos por código de pintado."""
    permission_required = ["infrastructure.view_node"]

    def get(self, request, painting_code, *args, **kwargs):
        start_time = time.time()
        try:
            nodes = (
                Node.objects
                .select_related("fk_district__fk_comuna")
                .filter(painting_code=painting_code)
            )
            if not nodes.exists():
                raise Exception("No se encontraron nodos con el código pintado suministrado.")
            data = {"type": "success", "data": [_serialize_node(n) for n in nodes]}
        except Exception as e:
            data = {"type": "error", "msg": str(e)}
        data["time"] = str(time.time() - start_time)
        return JsonResponse(data, safe=False)


class NodeSearchId(LoginRequiredMixin, APIPermissionValidation, View):
    """Buscar nodo por ID."""
    permission_required = ["infrastructure.view_node"]

    def get(self, request, id, *args, **kwargs):
        start_time = time.time()
        node = get_object_or_404(
            Node.objects.select_related("fk_district__fk_comuna"), id=id
        )
        data = {"type": "success", "data": [_serialize_node(node)]}
        data["time"] = str(time.time() - start_time)
        return JsonResponse(data, safe=False)


class NodeSearchInArea(LoginRequiredMixin, APIPermissionValidation, View):
    """Buscar nodos en un área alrededor de un punto."""
    permission_required = ["infrastructure.view_node"]

    DEFAULT_DISTANCE = 0.0010  # ~110m en grados WGS84

    def get(self, request, *args, **kwargs):
        start_time = time.time()
        try:
            longitud = request.GET.get("lng")
            latitud = request.GET.get("lat")
            if not (latitud and longitud):
                raise ValueError("No ha ingresado coordenadas válidas para la consulta.")

            punto = GEOSGeometry(f"POINT({longitud} {latitud})", srid=4326)
            queryset = (
                Node.objects
                .select_related("fk_district__fk_comuna")
                .filter(location__distance_lte=(punto, self.DEFAULT_DISTANCE))
            )

            geojson_str = serialize(
                "geojson",
                queryset=queryset,
                fields=("pk", "location", "painting_code", "fk_district"),
                geometry_field="location",
            )
            geojson = json.loads(geojson_str)

            # Adjuntar nombre de barrio y comuna sin disparar más queries (ya hay select_related)
            node_by_pk = {n.pk: n for n in queryset}
            for feature in geojson.get("features", []):
                pk = feature.get("properties", {}).get("pk") or feature.get("id")
                node = node_by_pk.get(pk)
                if node and node.fk_district:
                    feature["properties"]["district"] = node.fk_district.name
                    feature["properties"]["comuna"] = node.fk_district.fk_comuna.name

            data = {"type": "success", "data": geojson}
        except Exception as e:
            data = {"type": "error", "msg": str(e)}
        data["time"] = str(time.time() - start_time)
        return JsonResponse(data, safe=False)


class SearchInfrastructureInNodeView(LoginRequiredMixin, APIPermissionValidation, View):
    """Buscar toda la infraestructura asociada a un nodo."""
    permission_required = ["infrastructure.view_node"]

    def get(self, request, pk, *args, **kwargs):
        try:
            node = (
                Node.objects
                .prefetch_related(
                    "apbox_set",
                    "trafo_set__power",
                    "luminaire_set__fk_setting",
                    "luminaire_set__fk_brand",
                    "support_set__fk_setting__fk_material",
                    "support_set__fk_setting__fk_supporttype",
                )
                .get(pk=pk)
            )

            data = {
                "type": "success",
                "data": {
                    "apbox": [obj.toJSON() for obj in node.apbox_set.all()],
                    "trafo": [obj.toJSON() for obj in node.trafo_set.all()],
                    "luminaire": [obj.toJSON() for obj in node.luminaire_set.all()],
                    "support": [obj.toJSON() for obj in node.support_set.all()],
                },
            }
        except Node.DoesNotExist:
            data = {"type": "error", "msg": "El nodo solicitado no existe."}
        except Exception as e:
            data = {"type": "error", "msg": str(e)}
        return JsonResponse(data, safe=False)


# Alias para compatibilidad retro (el nombre legacy estaba mal escrito)
SearchInfratructureInNodeView = SearchInfrastructureInNodeView


class NodeSearchComunaView(LoginRequiredMixin, APIPermissionValidation, View):
    """Buscar nodos por comuna."""
    permission_required = ["infrastructure.view_node"]

    def get(self, request, *args, **kwargs):
        start_time = time.time()
        try:
            comuna = request.GET.get("comuna")
            if not comuna:
                raise ValueError("Falta el parámetro 'comuna'.")
            nodes = (
                Node.objects
                .select_related("fk_district__fk_comuna")
                .filter(fk_district__fk_comuna_id=int(comuna))
            )
            data = {"type": "success", "data": [_serialize_node(n) for n in nodes]}
        except Exception as e:
            data = {"type": "error", "msg": str(e)}
        data["time"] = str(time.time() - start_time)
        return JsonResponse(data, safe=False)
