import re

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.gis.geos import Point
from django.db.models import ProtectedError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View

from apps.infrastructure.models import Node
from apps.mixins import APIPermissionValidation


PAINTING_CODE_REGEX = re.compile(r"^\d{7}$")


def _parse_node_payload(request):
    """Extrae y valida los campos del payload (POST) de creación/edición de nodo."""
    painting_code = request.POST.get("painting_code", "").strip()
    lng = request.POST.get("lng", "").strip()
    lat = request.POST.get("lat", "").strip()
    observation = request.POST.get("observation", "").strip() or None

    if not PAINTING_CODE_REGEX.match(painting_code):
        raise ValueError("El código pintado debe tener exactamente 7 dígitos numéricos.")

    try:
        lng_f = float(lng)
        lat_f = float(lat)
    except ValueError:
        raise ValueError("Las coordenadas deben ser valores numéricos válidos.")

    return {
        "painting_code": int(painting_code),
        "location": Point(lng_f, lat_f, srid=4326),
        "observation": observation,
    }


class NodeCreateAPI(LoginRequiredMixin, APIPermissionValidation, View):
    permission_required = ["infrastructure.add_node"]

    def post(self, request, *args, **kwargs):
        try:
            payload = _parse_node_payload(request)
            node = Node.objects.create(**payload)
            return JsonResponse({
                "type": "success",
                "msg": "Nodo creado correctamente.",
                "data": node.toJSON(),
            })
        except ValueError as e:
            return JsonResponse({"type": "error", "msg": str(e)}, status=400)
        except Exception as e:
            return JsonResponse({"type": "error", "msg": str(e)}, status=500)


class NodeUpdateAPI(LoginRequiredMixin, APIPermissionValidation, View):
    """
    GET  /api/node/<pk>/  -> devuelve el nodo serializado (para precargar el modal de edición).
    POST /api/node/<pk>/  -> actualiza painting_code, location y observation.
    """
    permission_required = ["infrastructure.change_node"]

    def get_perms(self):
        if self.request.method == "GET":
            return ["infrastructure.view_node"]
        return list(self.permission_required)

    def get(self, request, pk, *args, **kwargs):
        node = get_object_or_404(
            Node.objects.select_related("fk_district__fk_comuna"), pk=pk
        )
        return JsonResponse({"type": "success", "data": node.toJSON()})

    def post(self, request, pk, *args, **kwargs):
        node = get_object_or_404(Node, pk=pk)
        try:
            payload = _parse_node_payload(request)
            node.painting_code = payload["painting_code"]
            node.location = payload["location"]
            node.observation = payload["observation"]
            node.save()
            node.refresh_from_db()
            return JsonResponse({
                "type": "success",
                "msg": "Nodo actualizado correctamente.",
                "data": node.toJSON(),
            })
        except ValueError as e:
            return JsonResponse({"type": "error", "msg": str(e)}, status=400)
        except Exception as e:
            return JsonResponse({"type": "error", "msg": str(e)}, status=500)


class NodeDeleteAPI(LoginRequiredMixin, APIPermissionValidation, View):
    permission_required = ["infrastructure.delete_node"]

    def post(self, request, pk, *args, **kwargs):
        node = get_object_or_404(Node, pk=pk)
        try:
            node.delete()
            return JsonResponse({"type": "success", "msg": "Nodo eliminado correctamente."})
        except ProtectedError:
            return JsonResponse({
                "type": "error",
                "msg": "No se puede eliminar el nodo porque tiene infraestructura asociada (transformadores, luminarias, apoyos o cajas AP).",
            }, status=409)
        except Exception as e:
            return JsonResponse({"type": "error", "msg": str(e)}, status=500)
