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
    """
    DEPRECATED. Buscar todos los nodos de un barrio.

    El flujo actual del mapa pinta marcadores vía NodeSearchInArea (bbox del
    viewport) y la tabla los lista paginada vía NodeListView. Este endpoint
    serializa la totalidad del barrio en un único response y no es usado por la
    UI; se conserva por compat. Eliminar en una limpieza posterior.
    """
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
    """
    Buscar nodos en un área del mapa.

    Modos soportados:
    - bbox: ?west=&south=&east=&north=  → todos los nodos dentro del viewport.
    - punto+radio: ?lat=&lng=            → nodos cercanos al punto (compat. legacy).
    """
    permission_required = ["infrastructure.view_node"]

    DEFAULT_DISTANCE = 0.0010  # ~110m en grados WGS84
    MAX_BBOX_RESULTS = 5000

    def _bbox_response(self, request):
        try:
            west = float(request.GET["west"])
            south = float(request.GET["south"])
            east = float(request.GET["east"])
            north = float(request.GET["north"])
        except (KeyError, ValueError):
            raise ValueError("Parámetros bbox inválidos (west/south/east/north).")

        bbox_wkt = (
            f"POLYGON(({west} {south}, {east} {south}, "
            f"{east} {north}, {west} {north}, {west} {south}))"
        )
        bbox = GEOSGeometry(bbox_wkt, srid=4326)

        # Payload mínimo para render de marcadores: id, painting_code, lng, lat.
        # Evitamos construir instancias Node y joinear a District/Comuna: los nombres
        # se piden on-demand al hacer click (endpoint detail).
        rows = list(
            Node.objects
            .filter(location__within=bbox)
            .values_list("id", "painting_code", "location")[: self.MAX_BBOX_RESULTS + 1]
        )
        truncated = len(rows) > self.MAX_BBOX_RESULTS
        data = [
            {"id": pk, "pk": pk, "painting_code": code, "lng": loc.x, "lat": loc.y}
            for pk, code, loc in rows[: self.MAX_BBOX_RESULTS]
            if loc is not None
        ]
        return {"type": "success", "data": data, "truncated": truncated}

    def _point_radius_response(self, request):
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

        node_by_pk = {n.pk: n for n in queryset}
        for feature in geojson.get("features", []):
            pk = feature.get("properties", {}).get("pk") or feature.get("id")
            node = node_by_pk.get(pk)
            if node and node.fk_district:
                feature["properties"]["district"] = node.fk_district.name
                feature["properties"]["comuna"] = node.fk_district.fk_comuna.name

        return {"type": "success", "data": geojson}

    def get(self, request, *args, **kwargs):
        start_time = time.time()
        try:
            if "west" in request.GET:
                data = self._bbox_response(request)
            else:
                data = self._point_radius_response(request)
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
    """
    DEPRECATED. Buscar nodos por comuna.

    El flujo actual del mapa pinta marcadores vía NodeSearchInArea (bbox del
    viewport) y la tabla los lista paginada vía NodeListView. Este endpoint
    serializa la totalidad de la comuna en un único response y no es usado por
    la UI; se conserva por compat. Eliminar en una limpieza posterior.
    """
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
