# standard library
import time
from datetime import datetime

# Django
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.db.models import Q
from django.views.generic import ListView
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404

# local Django
from apps.mixins import ValidatePermissionRequiredMixin
from ..models import OrderActive, OrderClosed, OrderActiveRoute
from ..choices import OT_STATUS
from apps.users.models import Area

MODULE_NAME = 'Ordenes de Trabajo'


class OrderActiveBase(LoginRequiredMixin, ValidatePermissionRequiredMixin, ListView):
    model = OrderActive
    permission_required = ['order.view_orderactive']

    @staticmethod
    def calculate_remaining_time(date_limit):
        now_dt = datetime.now()
        if now_dt > date_limit:
            return "Tiempo Expirado"
        diff = date_limit - now_dt
        days = diff.days
        hours, remainder = divmod(diff.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        return f"{days} días, {hours} horas, {minutes} minutos"

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    fields_to_select = [
        'id',
        'date_creation',
        'fk_pqr__id',
        'fk_pqr__fk_node_reported__fk_district__name',
        'fk_pqr__fk_node_reported__fk_district__fk_comuna__name',
        'fk_pqr__fk_node_reported',
        'fk_pqr__file_number',
        'fk_priority__name',
        'fk_internal_type_damage__name',
        'fk_timingrepair__name',
        'date_limit',
        'fk_crew__name',
    ]

    def area(self, **kwargs):
        return get_object_or_404(Area, name=kwargs.get('area'))

    def get_query(self, request, status, area):
        column_map = {
            'fk_pqr__id': 'fk_pqr__id',
            'fk_pqr__fk_node_reported__fk_district__name': 'fk_pqr__fk_node_reported__fk_district__name',
            'fk_pqr__fk_node_reported__fk_district__fk_comuna__name': 'fk_pqr__fk_node_reported__fk_district__fk_comuna__name',
            'fk_pqr__file_number': 'fk_pqr__file_number',
            'fk_priority__name': 'fk_priority__name',
            'fk_internal_type_damage__name': 'fk_internal_type_damage__name',
            'fk_timingrepair__name': 'fk_timingrepair__name',
            'fk_crew__name': 'fk_crew__name',
        }

        order_by = request.POST.get('order_by', 'id')
        order_dir = request.POST.get('order_dir', 'desc')

        if order_by not in column_map and order_by not in self.fields_to_select:
            order_by = 'id'

        if order_dir == 'desc':
            order_by = f'-{order_by}'

        search_term = request.POST.get('filtro', '').strip()

        queryset = self.model.objects.filter(
            Q(status=status) &
            Q(fk_area=area) & (
                Q(id__icontains=search_term) |
                Q(date_creation__icontains=search_term) |
                Q(fk_pqr__fk_node_reported__fk_district__name__icontains=search_term) |
                Q(fk_pqr__fk_node_reported__fk_district__fk_comuna__name__icontains=search_term) |
                Q(fk_pqr__file_number__icontains=search_term) |
                Q(fk_priority__name__icontains=search_term) |
                Q(fk_internal_type_damage__name__icontains=search_term) |
                Q(date_limit__icontains=search_term) |
                Q(fk_crew__name__icontains=search_term)
            )
        ).values(*self.fields_to_select).order_by(order_by)

        # Filtrar por grupo de usuario
        group = request.user.groups.first()
        if not (group and group.name in ('Administrador', 'Supervisor')):
            queryset = queryset.filter(fk_crew=request.user.fk_crew)

        return queryset

    def get_data(self, request, queryset):
        inicio = int(request.POST.get('inicio', 0))
        fin = int(request.POST.get('limite', 50))

        list_data = []
        for valor in queryset[inicio:inicio + fin]:
            valor['remaining_time'] = OrderActiveBase.calculate_remaining_time(valor['date_limit'])
            valor['date_creation'] = valor['date_creation'].strftime('%Y-%m-%d %H:%M:%S')
            valor['date_limit'] = valor['date_limit'].strftime('%Y-%m-%d %H:%M:%S') if valor['date_limit'] else ''
            list_data.append(valor)

        return {
            "type": 'success',
            "length": queryset.count(),
            "objects": list_data
        }

    def post(self, request, *args, **kwargs):
        try:
            start_time = time.time()
            queryset = self.get_query(request, self.status, self.area(**kwargs))
            data = self.get_data(request, queryset)
            data['time'] = str(time.time() - start_time)
        except Exception as e:
            data = {'type': 'error', 'msg': str(e)}
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['module'] = MODULE_NAME
        context['area'] = str(self.kwargs.get('area'))
        context['entity'] = OT_STATUS[self.status][1]
        context['title'] = f"ORDENES {context['entity']} {context['area']}".upper()
        context['show_sidebar'] = True
        return context


class OrderActiveListState1(OrderActiveBase):
    """Por Asignar"""
    template_name = 'list/active_state1.html'
    status = 1

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['list_url'] = reverse_lazy('order:list_ot_active_state1', kwargs={'area': context['area']})
        return context


class OrderActiveListState2(OrderActiveBase):
    """En Terreno"""
    template_name = 'list/active_state2.html'
    status = 2

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['list_url'] = reverse_lazy('order:list_ot_active_state2', kwargs={'area': context['area']})
        return context


class OrderActiveListState3(OrderActiveBase):
    """Validación"""
    template_name = 'list/active_state3.html'
    status = 3

    def get_data(self, request, queryset):
        inicio = int(request.POST.get('inicio', 0))
        fin = int(request.POST.get('limite', 50))

        list_data = []
        for valor in queryset[inicio:inicio + fin]:
            valor['remaining_time'] = OrderActiveBase.calculate_remaining_time(valor['date_limit'])
            valor['date_creation'] = valor['date_creation'].strftime('%Y-%m-%d %H:%M:%S')
            valor['date_limit'] = valor['date_limit'].strftime('%Y-%m-%d %H:%M:%S') if valor['date_limit'] else ''

            checkReassign = OrderActiveRoute.objects.filter(
                fk_ot__id=valor['id'], state=3
            ).order_by('-id').first()
            valor['reassign'] = checkReassign.cause.name if checkReassign and checkReassign.cause else None

            list_data.append(valor)

        return {
            "type": 'success',
            "length": queryset.count(),
            "objects": list_data
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['list_url'] = reverse_lazy('order:list_ot_active_state3', kwargs={'area': context['area']})
        return context


class OrderClosedListState4(LoginRequiredMixin, ValidatePermissionRequiredMixin, ListView):
    """Cerradas"""
    model = OrderClosed
    permission_required = ['order.view_orderclosed']
    template_name = 'list/closed_state4.html'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    fields_to_select = [
        'id',
        'date_creation',
        'fk_pqr__id',
        'fk_pqr__fk_node_reported__fk_district__name',
        'fk_pqr__fk_node_reported__fk_district__fk_comuna__name',
        'fk_pqr__file_number',
        'fk_priority__name',
        'fk_internal_type_damage__name',
        'fk_crew__name',
        'status',
    ]

    def area(self, **kwargs):
        return get_object_or_404(Area, name=kwargs.get('area'))

    def get_query(self, request, area):
        order_by = request.POST.get('order_by', 'id')
        order_dir = request.POST.get('order_dir', 'desc')
        search_term = request.POST.get('filtro', '').strip()
        canceled = request.POST.get('canceled') == 'true'
        status = 0 if canceled else 4

        if order_by not in self.fields_to_select:
            order_by = 'id'
        if order_dir == 'desc':
            order_by = f'-{order_by}'

        queryset = self.model.objects.filter(
            Q(status=status) &
            Q(fk_area=area) & (
                Q(id__icontains=search_term) |
                Q(fk_pqr__file_number__icontains=search_term) |
                Q(fk_priority__name__icontains=search_term) |
                Q(fk_internal_type_damage__name__icontains=search_term) |
                Q(fk_crew__name__icontains=search_term)
            )
        ).values(*self.fields_to_select).order_by(order_by)
        return queryset

    def get_data(self, request, queryset):
        inicio = int(request.POST.get('inicio', 0))
        fin = int(request.POST.get('limite', 50))

        list_data = []
        for valor in queryset[inicio:inicio + fin]:
            valor['date_creation'] = valor['date_creation'].strftime('%Y-%m-%d %H:%M:%S')
            list_data.append(valor)

        return {
            "type": 'success',
            "length": queryset.count(),
            "objects": list_data
        }

    def post(self, request, *args, **kwargs):
        try:
            start_time = time.time()
            queryset = self.get_query(request, self.area(**kwargs))
            data = self.get_data(request, queryset)
            data['time'] = str(time.time() - start_time)
        except Exception as e:
            data = {'type': 'error', 'msg': str(e)}
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['module'] = MODULE_NAME
        context['area'] = str(self.kwargs.get('area'))
        context['entity'] = 'Cerradas'
        context['title'] = f"ORDENES CERRADAS {context['area']}".upper()
        context['list_url'] = reverse_lazy('order:list_ot_closed_state4', kwargs={'area': context['area']})
        context['show_sidebar'] = True
        return context
