# standard library
import time
from datetime import datetime

# Django
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.generic import View

# local Django
from apps.mixins import APIPermissionValidation
from ..models import PqrActive, PqrActiveRoute, PqrClosed, PqrClosedRoute


class PqrStatusChangeHandler:
    """
    Manejador de cambio de estado de PQR activa.
    Sigue la misma lógica del old-project.
    """

    def __init__(self, instance):
        self.model_route = PqrActiveRoute
        self.instance = instance

    def validate_status(self, state, user=None):
        match state:
            case 0:
                self._validate_annulment(user)
            case 3:
                self._validate_attended()
            case _:
                pass

    def _validate_annulment(self, user):
        """Valida si es posible anular la PQR."""
        allowed_groups = ['Administrador', 'Supervisor']

        if not user.groups.filter(name__in=allowed_groups).exists():
            raise Exception("No tienes permiso para anular la PQR.")

        # Verificar órdenes asociadas - solo si el modelo OrderActive existe
        try:
            orders = self.instance.orderactive_set.all()
            # Solo se permite anular si las órdenes están en estado 1 (Asignación) o 3 (Validación)
            STATUS_ALLOWED = [1, 3]
            orders_denied = orders.filter(~Q(status__in=STATUS_ALLOWED)).values_list('id', flat=True)

            if orders_denied:
                orders_parsed = ', '.join([f"#{order}" for order in orders_denied])
                raise Exception(
                    f"No es posible anular la PQR. La(s) orden(es) {orders_parsed} deben estar en estado 'Por asignar' o 'Validación'"
                )
        except AttributeError:
            # Si no existe relación con OrderActive (módulo aún no registrado)
            pass

    def _validate_attended(self):
        """Valida si es posible marcar la PQR como atendida."""
        try:
            orders = self.instance.orderactive_set.all()
            if orders.exclude(status=4).exists():
                raise Exception(
                    f"No es posible marcar la PQR {str(self.instance)} como atendida, tiene ordenes sin cerrar"
                )
        except AttributeError:
            pass

    def change_status(self, state):
        self.instance.status = state
        self.instance.save()

    @transaction.atomic
    def create_route(self, init_state, causal=None):
        last_route_instance = self.model_route.objects \
            .filter(fk_pqr=self.instance, state=init_state) \
            .order_by('-id').first()

        if last_route_instance:
            last_route_instance.output_date = datetime.now()
            last_route_instance.save()

        new_route = self.model_route(
            fk_pqr=self.instance,
            state=self.instance.status
        )

        if causal:
            new_route.cause = causal
        if self.instance.status == 3 or self.instance.status == 0:
            new_route.output_date = datetime.now()
        new_route.save()

    @transaction.atomic
    def move_to_close(self):
        """
        Copia un PqrActive con sus PqrActiveRoute a un PqrClosed con sus PqrClosedRoute.
        """
        pqr_closed = PqrClosed(id=self.instance.id)

        for field in self.instance._meta.fields:
            if field.name != 'id':
                setattr(pqr_closed, field.name, getattr(self.instance, field.name))
        pqr_closed.save()

        history_active = PqrActiveRoute.objects.filter(fk_pqr=self.instance)

        for route in history_active:
            history_closed = PqrClosedRoute(
                id=route.id,
                input_date=route.input_date,
                output_date=route.output_date if route.output_date is not None else None,
                fk_pqr=pqr_closed,
                state=route.state,
                cause=route.cause
            )
            history_closed.save()
        return pqr_closed


class PqrStatusChangeAPI(LoginRequiredMixin, APIPermissionValidation, View):
    permission_required = ['pqrs.change_pqractive']

    def post(self, request, *args, **kwargs):
        try:
            start_time = time.time()

            pqr_instance = get_object_or_404(PqrActive, id=int(request.POST['pqr']))
            init_state = pqr_instance.status
            requested_state = int(request.POST['state'])

            pqr_handler = PqrStatusChangeHandler(pqr_instance)
            pqr_handler.validate_status(requested_state, request.user)
            pqr_handler.change_status(requested_state)
            pqr_handler.create_route(init_state)

            data = {
                'type': 'success',
                'msg': f'Se cambió correctamente el estado de la PQR {str(pqr_instance)}'
            }
        except Exception as e:
            data = {'type': 'error', 'msg': str(e)}
        data['time'] = str(time.time() - start_time)
        return JsonResponse(data, safe=False)
