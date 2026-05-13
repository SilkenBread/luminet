from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_protect

from apps.infrastructure.models import Node
from apps.mixins import DataTablesMixin, ValidatePermissionRequiredMixin


MODULE_NAME = "Infraestructura"
ENTITY = "Nodos"


class NodeListView(LoginRequiredMixin, ValidatePermissionRequiredMixin, DataTablesMixin, View):
    """
    Vista principal para visualizar/gestionar Nodos.

    GET  -> Renderiza el template con mapa + tabla + filtros.
    POST -> Responde el protocolo Server-Side de DataTables.net.
    """

    template_name = "node/list.html"
    permission_required = ["infrastructure.view_node"]

    column_mapping = {
        "id": "id",
        "painting_code": "painting_code",
        "comuna": "fk_district__fk_comuna__name",
        "district": "fk_district__name",
    }

    def get_initial_queryset(self, request):
        qs = Node.objects.select_related("fk_district__fk_comuna")
        district_id = request.POST.get("district_id")
        comuna_id = request.POST.get("comuna_id")
        if district_id and district_id.isdigit():
            return qs.filter(fk_district_id=int(district_id))
        if comuna_id and comuna_id.isdigit():
            return qs.filter(fk_district__fk_comuna_id=int(comuna_id))
        # Sin filtro activo: no se devuelve nada para evitar escanear toda la tabla.
        return Node.objects.none()

    def serialize_row(self, node):
        return {
            "id": node.id,
            "painting_code": node.painting_code,
            "comuna": node.fk_district.fk_comuna.name if node.fk_district else None,
            "district": node.fk_district.name if node.fk_district else None,
            "lat": node.location.y if node.location else None,
            "lng": node.location.x if node.location else None,
        }

    def get_context_data(self):
        return {
            "title": "Visualizador de Nodos",
            "module": MODULE_NAME,
            "entity": ENTITY,
            "list_url": reverse_lazy("infrastructure:list_nodes"),
            "show_sidebar": True,
        }

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data())

    @method_decorator(csrf_protect)
    def post(self, request, *args, **kwargs):
        return self.get_datatables_response(request)
