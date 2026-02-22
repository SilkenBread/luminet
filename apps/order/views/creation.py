# standard library
import time

# Django
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.generic import View
from django.apps import apps

# local Django
from apps.mixins import APIPermissionValidation
from .tools import SetOrder
from apps.pqrs.views.tools import PqrStatusChangeHandler
from ..models import (
    OrderActive, InternalTypeDamage, Priority, TimingRepair,
    Activities, CauseRejectOrder
)

PqrActive = apps.get_model('pqrs', 'PqrActive')
Origin = apps.get_model('pqrs', 'Origin')


class GetOrderFieldsAPI(View):
    """Returns all the select/dropdown fields needed for order creation form."""

    def get(self, request, *args, **kwargs):
        try:
            start_time = time.time()
            data = {
                'type': 'success',
                'data': {
                    'listIntDamage': list(InternalTypeDamage.objects.all().values('id', 'name')),
                    'listPriority': list(Priority.objects.all().values('id', 'name')),
                    'listTiming': list(TimingRepair.objects.all().values('id', 'name')),
                    'listActivities': list(Activities.objects.all().values('id', 'code', 'name')),
                    'listRejectOt': list(CauseRejectOrder.objects.all().values('id', 'name')),
                    'origin': list(Origin.objects.all().values('id', 'name')),
                }
            }
        except Exception as e:
            data = {'type': 'error', 'msg': str(e)}
        data['time'] = str(time.time() - start_time)
        return JsonResponse(data, safe=False)


class ConfirmOrderCreationAPI(LoginRequiredMixin, View):
    """Returns existing orders for a given PQR to confirm before creating new ones."""

    def post(self, request, *args, **kwargs):
        try:
            start_time = time.time()
            pqr = get_object_or_404(PqrActive, pk=request.POST.get('pqr'))
            orders_created = OrderActive.objects.filter(fk_pqr=pqr)
            orders_count = orders_created.count()
            data = {
                'type': 'success',
                'msg': f"La PQR {pqr} tiene {orders_count} ordenes creadas.",
                'data': [order.toJSON() for order in orders_created]
            }
        except Exception as e:
            data = {'type': 'error', 'msg': str(e)}
        data['time'] = str(time.time() - start_time)
        return JsonResponse(data, safe=False)


class SetOrderActiveAPI(LoginRequiredMixin, APIPermissionValidation, View):
    """Creates a new OrderActive from a PQR."""
    permission_required = ['order.add_orderactive']

    def post(self, request, *args, **kwargs):
        start_time = time.time()
        try:
            params = request.POST.dict()
            pqr = get_object_or_404(PqrActive, id=params['id'])
            params['fk_type_order'] = 1
            base_fields = SetOrder.get_base_fields(params)
            extra_fields = {
                'fk_pqr': pqr,
                'user_creation': request.user,
                'fk_area': SetOrder.get_area(pqr),
            }
            create = SetOrder(base_fields).create(OrderActive, extra_fields)
            data = {'type': 'success', 'msg': f'Se creó correctamente la orden de trabajo {str(create)}'}
        except Exception as e:
            data = {'type': 'error', 'msg': str(e)}
        data['time'] = str(time.time() - start_time)
        return JsonResponse(data, safe=False)
