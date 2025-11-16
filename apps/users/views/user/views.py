from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.core.paginator import Paginator
from apps.mixins import ValidatePermissionRequiredMixin
from apps.users.models import User
from django.views.generic import ListView

ENTITY = 'Usuarios'
MODULE = 'Gestión de Usuarios'

class UserListView(LoginRequiredMixin, ValidatePermissionRequiredMixin, ListView):
    model = User
    template_name = 'user/list.html'
    permission_required = ['users.view_user']

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return self.get_ajax_data(request)
        return super().get(request, *args, **kwargs)

    def get_ajax_data(self, request):
        data = {}
        try:
            # Parámetros de paginación de DataTables
            start = int(request.GET.get('start', 0))
            length = int(request.GET.get('length', 10))
            search = request.GET.get('search[value]', '')
            
            # Filtrar usuarios
            queryset = User.objects.all()
            
            if search:
                queryset = queryset.filter(
                    first_name__icontains=search
                ) | queryset.filter(
                    last_name__icontains=search
                ) | queryset.filter(
                    email__icontains=search
                ) | queryset.filter(
                    username__icontains=search
                )
            
            # Total de registros
            total_records = User.objects.count()
            filtered_records = queryset.count()
            
            # Paginación
            page_number = (start // length) + 1
            paginator = Paginator(queryset, length)
            page_obj = paginator.get_page(page_number)
            
            # Serializar datos
            users_data = []
            for user in page_obj:
                user_dict = user.toJSON()
                users_data.append(user_dict)
            
            # Formato de respuesta para DataTables
            data = {
                'draw': int(request.GET.get('draw', 1)),
                'recordsTotal': total_records,
                'recordsFiltered': filtered_records,
                'data': users_data
            }
        except Exception as e:
            data = {
                'error': str(e)
            }
        
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Listado de Usuarios'
        context['module'] = MODULE
        context['entity'] = ENTITY
        context['create_url'] = reverse_lazy('users:user_list')  # TODO: Cambiar a user_create cuando exista
        context['list_url'] = reverse_lazy('users:user_list')
        context['show_sidebar'] = True
        return context
