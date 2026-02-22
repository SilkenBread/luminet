# standard library
import os
import time
from datetime import datetime

# Django
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.apps import apps
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from django.views import View

# local Django
from ..models import (
    OrderActive, OrderClosed, OrderActiveRoute, OrderClosedRoute,
    CauseRejectOrder, TypeOrder, InternalTypeDamage, Priority, TimingRepair
)

PqrActive = apps.get_model('pqrs', 'PqrActive')
Zone = apps.get_model('users', 'Zone')


class SetOrder:
    def __init__(self, base_fields):
        self.base_fields = base_fields

    @staticmethod
    def get_base_fields(params):
        return {
            'fk_type_order': get_object_or_404(TypeOrder, id=params['fk_type_order']),
            'fk_internal_type_damage': get_object_or_404(InternalTypeDamage, id=params['fk_internal_type_damage']),
            'internal_observation': params['internal_observation'],
            'fk_priority': get_object_or_404(Priority, id=params['fk_priority']),
            'fk_timingrepair': get_object_or_404(TimingRepair, id=params['fk_timingrepair'])
        }

    @staticmethod
    def get_area(pqr):
        """Intenta obtener el área a partir de la zona del nodo reportado."""
        try:
            model_name = pqr.__class__.__name__.lower()
            zone = Zone.objects.filter(**{f'comunas__district__node__{model_name}': pqr}).first()
            area = zone.fk_area if zone else None
            return area
        except Exception:
            return None

    def create(self, model, extra_fields):
        return model.objects.create(**self.base_fields, **extra_fields)


class OrderStatusChangeHandler:
    def __init__(self, instance):
        self.model_route = apps.get_model('order', f'{str(instance.__class__.__name__)}Route')
        self.instance = instance

    def validate_status(self, state, user=None):
        match state:
            case 0:  # Anulacion
                if user and not user.groups.filter(name__in=['Administrador', 'Supervisor']).exists():
                    raise ValueError("No tienes permiso para anular la orden.")
            case 1:  # Asignacion
                if user and not user.groups.filter(name__in=['Administrador', 'Supervisor']).exists():
                    raise ValueError("No tienes permiso para volver a asignación la orden.")
            case 2:  # Terreno
                if not self.instance.fk_crew:
                    raise ValueError(f"No es posible pasar la orden {str(self.instance)} a terreno, no tiene una cuadrilla asignada")
            case 3:  # Validacion
                if not all([self.instance.image1, self.instance.image2, self.instance.site_observation]):
                    raise ValueError("Debes tener todos los campos para cambiar la orden a validación")
            case 4:
                history = self.model_route.objects.filter(fk_ot=self.instance, state=3).order_by('-id').first()
                if history and history.cause:
                    raise ValueError("No se puede cerrar la orden, tiene una reasignación pendiente.")
            case _:
                raise ValueError(f"No fue posible cambiar de estado la orden {str(self.instance)}, el estado no coincide.")

    def change_status(self, state):
        self.instance.status = state
        self.instance.save()
        match self.instance.status:
            case 1:
                self.instance.fk_crew = None
                self.instance.assigned_by = None
                self.instance.save()

    @transaction.atomic
    def create_route(self, user, init_state, causal=None):
        last_route_instance = self.model_route.objects.filter(fk_ot=self.instance, state=init_state).order_by('-id').first()
        if last_route_instance:
            last_route_instance.output_date = datetime.now()
            last_route_instance.save()
        new_route = self.model_route(fk_ot=self.instance, state=self.instance.status, user_creation=user)
        if causal:
            causal_instance = CauseRejectOrder.objects.get(pk=int(causal))
            new_route.cause = causal_instance
        if self.instance.status == 4 or self.instance.status == 0:
            new_route.output_date = datetime.now()
        new_route.save()

    @transaction.atomic
    def move_to_close(self):
        """Move an OrderActive to OrderClosed."""
        from apps.pqrs.views.tools import PqrStatusChangeHandler

        PqrClosed = apps.get_model('pqrs', 'PqrClosed')
        active_pqr = self.instance.fk_pqr
        pqr_id_for_closed_order = None

        pqr_closed_instance = PqrClosed.objects.filter(id=active_pqr.id).first()
        if pqr_closed_instance:
            pqr_id_for_closed_order = pqr_closed_instance.id
        else:
            pqr_handler = PqrStatusChangeHandler(active_pqr)
            newly_closed_pqr = pqr_handler.move_to_close()
            pqr_id_for_closed_order = newly_closed_pqr.id

        order_closed = OrderClosed(id=self.instance.id, fk_pqr_id=pqr_id_for_closed_order)
        for field in self.instance._meta.fields:
            if field.name not in ('id', 'fk_pqr'):
                setattr(order_closed, field.name, getattr(self.instance, field.name))

        for field_name in ['image1', 'image2']:
            image_active = getattr(self.instance, field_name)
            if image_active:
                filename = os.path.basename(image_active.name)
                new_filename = f'ot_images/{now().strftime("%Y/%m/%d")}/{filename}'
                setattr(order_closed, field_name, new_filename)
                setattr(self.instance, field_name, None)

        activities = self.instance.activities.all()
        order_closed.save()
        order_closed.activities.add(*activities)

        history_active = OrderActiveRoute.objects.filter(fk_ot=self.instance)
        for history in history_active:
            order_closed_history = OrderClosedRoute(
                id=history.id, user_creation=history.user_creation,
                input_date=history.input_date,
                output_date=history.output_date if history.output_date is not None else None,
                fk_ot=order_closed, state=history.state, cause=history.cause
            )
            order_closed_history.save()
        history_active.delete()
        self.instance.delete()


class OrderStatusChangeAPI(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        start_time = time.time()
        try:
            model_name = kwargs.get('model')
            order_id = kwargs.get('id')
            state = int(kwargs.get('state'))

            model = apps.get_model('order', model_name)
            instance = get_object_or_404(model, id=order_id)

            handler = OrderStatusChangeHandler(instance)
            handler.validate_status(state, request.user)
            init_state = instance.status
            handler.change_status(state)
            handler.create_route(request.user, init_state)

            if state == 4:
                handler.move_to_close()

            data = {'type': 'success', 'msg': f'Se cambió el estado de la orden {str(instance)} correctamente'}
        except Exception as e:
            data = {'type': 'error', 'msg': str(e)}
        data['time'] = str(time.time() - start_time)
        return JsonResponse(data, safe=False)
