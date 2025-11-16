from django.contrib import messages
from django.contrib.auth.models import Group
from django.contrib.auth.mixins import AccessMixin
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect, JsonResponse
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.db.models import Q

class ValidatePermissionRequiredMixin(AccessMixin):
    permission_required = []

    def get_perms(self):
        """
        Convierte permission_required en una lista si es un string o un iterable.
        """
        if isinstance(self.permission_required, str):
            return [self.permission_required]
        return list(self.permission_required)

    def exception_redirect(self, request):
        """
        Redirige al usuario si no tiene permisos, mostrando un mensaje de error.
        """
        messages.error(request, 'No tiene permiso para ingresar a este módulo')
        return redirect(reverse_lazy('core:dashboard'))

    def has_permission(self, user):
        """
        Verifica si el usuario tiene los permisos requeridos, ya sea directamente o a través de sus grupos.
        """
        if user.is_superuser:
            return True

        user_perms = set(user.get_all_permissions())  # Obtiene todos los permisos del usuario y sus grupos
        required_perms = set(f"{perm}" for perm in self.get_perms())
        
        return required_perms.issubset(user_perms)

    def dispatch(self, request, *args, **kwargs):
        """
        Evalúa si el usuario tiene permisos y maneja la redirección en caso contrario.
        """
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        if not self.has_permission(request.user):
            return self.exception_redirect(request)
        
        return super().dispatch(request, *args, **kwargs)


class APIPermissionValidation(AccessMixin):
    permission_required = ''

    def get_perms(self):
        if isinstance(self.permission_required, str):
            return [self.permission_required]
        return list(self.permission_required)

    def has_permission(self, user):
        """
        Verifica si el usuario tiene los permisos requeridos, directamente o por grupos.
        """
        if user.is_superuser:
            return True

        user_perms = set(user.get_all_permissions())  # Incluye permisos por grupos y asignados directamente
        required_perms = set(self.get_perms())

        # Verifica que cada permiso esté en el formato 'app_label.codename'
        qualified_required_perms = set()
        for perm in required_perms:
            if '.' not in perm:
                raise ValueError(f"El permiso '{perm}' debe estar en formato 'app_label.codename'")
            qualified_required_perms.add(perm)

        return qualified_required_perms.issubset(user_perms)

    def dispatch(self, request, *args, **kwargs):
        user = request.user

        if not user.is_authenticated:
            return self.handle_no_permission()

        # Guardar grupo en sesión si hay solo uno (opcional, por si lo necesitas para otra lógica)
        if len(user.groups.all()) == 1:
            request.session['group'] = user.groups.first().id

        if not self.has_permission(user):
            return self.handle_permission_error('No tiene permiso para realizar esta acción')

        return super().dispatch(request, *args, **kwargs)

    def handle_permission_error(self, msg='No tiene permiso para realizar esta acción'):
        return JsonResponse({'type': 'error', 'msg': msg}, status=403)

    def handle_no_permission(self):
        return JsonResponse({'type': 'error', 'msg': 'Usuario no autenticado'}, status=401)


class ValidateAccessMixin(AccessMixin):
    """
    Mixin para validar si el usuario tiene acceso al recurso asociado con el parámetro 'pk'.
    """
    error_message = 'No tienes permiso para acceder a este recurso.'
    redirect_url = reverse_lazy('core:dashboard')
    param_name = None

    def has_access(self, param):
        raise NotImplementedError("Debes implementar el método 'has_access'.")

    def exception_redirect(self, request, custom_message=None):
        messages.error(request, self.error_message)
        return HttpResponseRedirect(self.redirect_url)

    def dispatch(self, request, *args, **kwargs):
        param = kwargs.get(self.param_name)

        if request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)
        
        try:
            if not self.has_access(request, param):
                return self.exception_redirect(request)
        except Exception as e:
            return self.exception_redirect(request, custom_message=str(e))
        
        return super().dispatch(request, *args, **kwargs)


class DataTablesMixin:
    """
    Mixin para manejar peticiones AJAX de DataTables. y Server Side Processing.
    """
    def get_datatables_response(self, request):

        queryset = self.get_initial_queryset(request)
        records_total = queryset.count()
        
        draw = int(request.POST.get('draw', 0))
        start = int(request.POST.get('start', 0))
        length = int(request.POST.get('length', 10))

        queryset, records_filtered = self.filter_queryset(request, queryset)

        queryset = self.order_queryset(request, queryset)

        paginated_queryset = queryset[start:start + length]

        data = [self.serialize_row(obj) for obj in paginated_queryset]

        return JsonResponse({
            'type': 'success',
            'msg': 'Consulta exitosa',
            'draw': draw,
            'recordsTotal': records_total,
            'recordsFiltered': records_filtered,
            'data': data,
        })
    
    def filter_queryset(self, request, queryset):
        search_value = request.POST.get('search[value]', '')
        if not search_value:
            return queryset, queryset.count()
        
        search_query = Q()
        for field in self.column_mapping.values():
            if field: 
                search_query |= Q(**{f'{field}__icontains': search_value})
        
        filtered_queryset = queryset.filter(search_query)
        return filtered_queryset, filtered_queryset.count()
    
    def order_queryset(self, request, queryset):
        order_column_index = int(request.POST.get('order[0][column]', 0))
        order_column_name_js = request.POST.get(f'columns[{order_column_index}][data]', 'id')
        order_dir = request.POST.get('order[0][dir]', 'asc')
        
        order_field = self.column_mapping.get(order_column_name_js, 'id')
        if order_dir == 'desc':
            order_field = f'-{order_field}'
            
        return queryset.order_by(order_field)   