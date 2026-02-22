# standard library
import time

# Django
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.generic import View

# local Django
from apps.mixins import APIPermissionValidation
from ..models import PqrActive, PqrClosed


class PqrDetailAPI(LoginRequiredMixin, APIPermissionValidation, View):
    permission_required = ['pqrs.view_pqractive']

    def get(self, request, *args, **kwargs):
        try:
            start_time = time.time()
            pk = kwargs.get('pk')

            # Intentar buscar en PqrActive primero, luego en PqrClosed
            pqr = PqrActive.objects.filter(pk=pk).select_related(
                'fk_type_damage', 'fk_origin',
                'fk_node_reported__fk_district__fk_comuna'
            ).first()

            is_closed = False
            if not pqr:
                pqr = get_object_or_404(
                    PqrClosed.objects.select_related(
                        'fk_type_damage', 'fk_origin',
                        'fk_node_reported__fk_district__fk_comuna'
                    ),
                    pk=pk
                )
                is_closed = True

            pqr_data = pqr.toJSON()

            # Agregar datos del nodo (coordenadas)
            node = pqr.fk_node_reported
            if node and node.location:
                pqr_data['node_location'] = {
                    'lat': node.location.y,
                    'lng': node.location.x,
                    'painting_code': node.painting_code,
                    'address': getattr(node, 'address', ''),
                }
            else:
                pqr_data['node_location'] = None

            # Agregar datos de distrito y comuna
            if node and node.fk_district:
                pqr_data['district'] = node.fk_district.name
                pqr_data['comuna'] = node.fk_district.fk_comuna.name if node.fk_district.fk_comuna else ''
            else:
                pqr_data['district'] = ''
                pqr_data['comuna'] = ''

            # Intentar cargar órdenes asociadas
            orders_data = []
            try:
                if not is_closed:
                    from apps.order.models import OrderActive
                    orders = OrderActive.objects.filter(fk_pqr=pqr).select_related(
                        'fk_internal_type_damage', 'fk_priority', 'fk_crew', 'fk_area'
                    )
                    orders_data = [order.toJSON() for order in orders]
                else:
                    from apps.order.models import OrderClosed
                    orders = OrderClosed.objects.filter(fk_pqr=pqr).select_related(
                        'fk_internal_type_damage', 'fk_priority', 'fk_crew', 'fk_area'
                    )
                    orders_data = [order.toJSON() for order in orders]
            except (ImportError, Exception):
                orders_data = []

            pqr_data['orders'] = orders_data
            pqr_data['is_closed'] = is_closed

            data = {'type': 'success', 'data': pqr_data}
        except Exception as e:
            data = {'type': 'error', 'msg': str(e)}
        data['time'] = str(time.time() - start_time)
        return JsonResponse(data, safe=False)
