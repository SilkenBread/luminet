# standard library
import time, json

# Django
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.db.models import Q
from django.views.generic import ListView, TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse_lazy
from django.core.exceptions import ValidationError

# local Django
from config.settings import *
from ..models import *
from apps.mixins import ValidatePermissionRequiredMixin


MODULE_NAME = 'PQRs'
ENTITY = 'PQRs'


class PqrStateBaseListView(LoginRequiredMixin, ValidatePermissionRequiredMixin, ListView):
    """
    Clase genérica para listar los estados de una PQR usando Server Side Rendering
    """
    model = PqrActive
    permission_required = ['pqrs.view_pqractive']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = {}

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    fields_to_select = [
        'id',
        'date_creation',
        'file_number',
        'fk_type_damage__name',
        'fk_node_reported',
        'fk_node_reported__painting_code',
        'fk_node_reported__fk_district__fk_comuna__name',
        'fk_node_reported__fk_district__name',
        'fk_origin__name',
        'name',
    ]
    
    def get_query(self, request, status):
        # Mapeo de columnas para permitir ordenamiento por campos relacionados
        column_map = {
            'fk_type_damage__name': 'fk_type_damage__name',
            'fk_origin__name': 'fk_origin__name',
            'fk_node_reported__painting_code': 'fk_node_reported__painting_code',
            'fk_node_reported__fk_district__fk_comuna__name': 'fk_node_reported__fk_district__fk_comuna__name',
            'fk_node_reported__fk_district__name': 'fk_node_reported__fk_district__name',
        }

        # Obtener el campo de ordenamiento y la dirección
        order_by = request.POST.get('order_by', 'id')
        order_dir = request.POST.get('order_dir', 'asc')
        
        # Validar y corregir el campo de ordenamiento
        if order_by not in column_map and order_by not in self.fields_to_select:
            order_by = 'id'
        
        # Preparar el ordenamiento
        if order_dir == 'desc':
            order_by = f'-{order_by}'

        # Filtro de búsqueda con validación
        search_term = request.POST.get('filtro', '').strip()
        
        queryset = self.model.objects.filter(
            Q(status=status) & (
                Q(id__icontains=search_term) |
                Q(date_creation__icontains=search_term) |
                Q(file_number__icontains=search_term) |
                Q(fk_type_damage__name__icontains=search_term) |
                Q(fk_node_reported__painting_code__icontains=search_term) |
                Q(fk_node_reported__fk_district__fk_comuna__name__icontains=search_term) |
                Q(fk_node_reported__fk_district__name__icontains=search_term) |
                Q(fk_origin__name__icontains=search_term) |
                Q(name__icontains=search_term)
            )
        ).values(*self.fields_to_select).order_by(order_by)
        return queryset
    
    def get_data(self, request, queryset):
        inicio = int(request.POST.get('inicio', 0))
        fin = int(request.POST.get('limite', 50))

        list_data = [
            {**valor, 'date_creation': valor['date_creation'].strftime('%Y-%m-%d %H:%M:%S')} 
            for valor in queryset[inicio:inicio+fin]
        ]

        self.data = {
            "type": 'success',
            "length": queryset.count(),
            "objects": list_data
        }
        return self.data
    
    def post(self, request, *args, **kwargs):
        try:
            start_time = time.time()
            action = request.POST.get('action')
            
            if action != 'searchdata':
                raise ValidationError('Acción no válida')

            queryset = self.get_query(request, self.status)
            data = self.get_data(request, queryset)
        except Exception as e:
            data = {'type': 'error', 'msg': str(e)}
        
        data['time'] = str(time.time() - start_time)
        return JsonResponse(data, safe=False)

class PqrReceiveListView(PqrStateBaseListView):
    template_name = 'list/state1.html'
    status= 1
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'PQRs EN REVISIÓN'
        context['module'] = MODULE_NAME
        context['entity'] = 'Revisión'
        context['create_url'] = reverse_lazy('pqrs:create_internal_pqr')
        context['externalcreate_url'] = reverse_lazy('pqrs:create_pqr')
        context['list_url'] = reverse_lazy('pqrs:list_reviewpqr')
        context['show_sidebar'] = True
        return context


class PqrReviewListView(PqrStateBaseListView):
    template_name = 'list/state2.html'
    status = 2

    def get_query(self, request, status):
        # Obtener el campo de ordenamiento y la dirección
        order_by = request.POST.get('order_by', 'id')
        order_dir = request.POST.get('order_dir', 'asc')
        
        # Filtro adicional para órdenes
        with_order = request.POST.get('with_orders') == 'true'
        
        # Validar y corregir el campo de ordenamiento
        column_map = {
            'fk_type_damage__name': 'fk_type_damage__name',
            'fk_origin__name': 'fk_origin__name',
            'fk_node_reported__painting_code': 'fk_node_reported__painting_code',
            'fk_node_reported__fk_district__fk_comuna__name': 'fk_node_reported__fk_district__fk_comuna__name',
            'fk_node_reported__fk_district__name': 'fk_node_reported__fk_district__name',
        }
        
        if order_by not in column_map and order_by not in self.fields_to_select:
            order_by = 'id'
        
        # Preparar el ordenamiento
        if order_dir == 'desc':
            order_by = f'-{order_by}'

        # Filtro de búsqueda
        search_term = request.POST.get('filtro', '').strip()
        
        # Consulta con filtros combinados
        queryset = self.model.objects.filter(
            Q(status=status) & 
            Q(orderactive__isnull=not with_order) & (
                Q(id__icontains=search_term) |
                Q(date_creation__icontains=search_term) |
                Q(file_number__icontains=search_term) |
                Q(fk_type_damage__name__icontains=search_term) |
                Q(fk_node_reported__painting_code__icontains=search_term) |
                Q(fk_node_reported__fk_district__fk_comuna__name__icontains=search_term) |
                Q(fk_node_reported__fk_district__name__icontains=search_term) |
                Q(fk_origin__name__icontains=search_term) |
                Q(name__icontains=search_term)
            )
        ).values(*self.fields_to_select).order_by(order_by).distinct()    
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'PQRs RECIBIDAS'
        context['module'] = MODULE_NAME
        context['entity'] = 'Recibidas'
        context['create_url'] = reverse_lazy('pqrs:create_internal_pqr')
        context['externalcreate_url'] = reverse_lazy('pqrs:create_pqr')
        context['list_url'] = reverse_lazy('pqrs:list_receivepqr')
        return context


class PqrAtendedListView(PqrStateBaseListView):
    model = PqrClosed
    template_name = 'list/state3.html'
    permission_required = ['pqrs.view_pqrclosed']
    status = None

    def get_query(self, request, status):
        # Determinar el estado basado en el parámetro 'canceled'
        canceled = request.POST.get('canceled') == 'true'
        status = 0 if canceled else 3

        # Mapeo de columnas para permitir ordenamiento por campos relacionados
        column_map = {
            'fk_type_damage__name': 'fk_type_damage__name',
            'fk_origin__name': 'fk_origin__name',
            'fk_node_reported__painting_code': 'fk_node_reported__painting_code',
            'fk_node_reported__fk_district__fk_comuna__name': 'fk_node_reported__fk_district__fk_comuna__name',
            'fk_node_reported__fk_district__name': 'fk_node_reported__fk_district__name',
        }

        # Obtener el campo de ordenamiento y la dirección
        order_by = request.POST.get('order_by', 'id')
        order_dir = request.POST.get('order_dir', 'asc')
        
        # Validar y corregir el campo de ordenamiento
        if order_by not in column_map and order_by not in self.fields_to_select:
            order_by = 'id'
        
        # Preparar el ordenamiento
        if order_dir == 'desc':
            order_by = f'-{order_by}'

        # Filtro de búsqueda con validación
        search_term = request.POST.get('filtro', '').strip()
        
        queryset = self.model.objects.filter(
            Q(status=status) & (
                Q(id__icontains=search_term) |
                Q(date_creation__icontains=search_term) |
                Q(file_number__icontains=search_term) |
                Q(fk_type_damage__name__icontains=search_term) |
                Q(fk_node_reported__painting_code__icontains=search_term) |
                Q(fk_node_reported__fk_district__fk_comuna__name__icontains=search_term) |
                Q(fk_node_reported__fk_district__name__icontains=search_term) |
                Q(fk_origin__name__icontains=search_term) |
                Q(name__icontains=search_term)
            )
        ).values(*self.fields_to_select).order_by(order_by)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'PQRs Atendidas'
        context['module'] = MODULE_NAME
        context['entity'] = 'Atendidas'
        context['list_url'] = reverse_lazy('pqrs:list_atendedpqr')
        return context
