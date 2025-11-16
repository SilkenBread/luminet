from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.core.paginator import Paginator
from django.contrib import messages
from django.shortcuts import get_object_or_404
from apps.mixins import ValidatePermissionRequiredMixin
from apps.users.models import User, Crew
from apps.users.forms import UserForm, UserUpdateForm
from django.views.generic import ListView, CreateView, UpdateView
from django.db.models import Q

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
                    Q(first_name__icontains=search) |
                    Q(last_name__icontains=search) |
                    Q(email__icontains=search) |
                    Q(username__icontains=search)
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
        context['create_url'] = reverse_lazy('users:user_create')
        context['list_url'] = reverse_lazy('users:user_list')
        context['show_sidebar'] = True
        return context


class UserCreateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, CreateView):
    model = User
    form_class = UserForm
    template_name = 'user/create.html'
    permission_required = ['users.add_user']
    success_url = reverse_lazy('users:user_list')

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        # Si es AJAX, devolver las cuadrillas filtradas por área
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            area_id = request.GET.get('area_id')
            if area_id:
                crews = Crew.objects.filter(fk_area_id=area_id, is_active=True).values('id', 'name')
                return JsonResponse(list(crews), safe=False)
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = None
        form = self.get_form()
        
        if form.is_valid():
            try:
                user = form.save(commit=False)
                user.save()
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'message': f'Usuario {user.username} creado exitosamente',
                        'redirect_url': str(self.success_url)
                    })
                else:
                    messages.success(request, f'Usuario {user.username} creado exitosamente')
                    return self.form_valid(form)
            except Exception as e:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': f'Error al crear el usuario: {str(e)}'
                    })
                else:
                    messages.error(request, f'Error al crear el usuario: {str(e)}')
                    return self.form_invalid(form)
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                errors = {}
                for field, error_list in form.errors.items():
                    errors[field] = [str(error) for error in error_list]
                return JsonResponse({
                    'success': False,
                    'errors': errors
                })
            else:
                return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Crear Usuario'
        context['module'] = MODULE
        context['entity'] = ENTITY
        context['list_url'] = reverse_lazy('users:user_list')
        context['show_sidebar'] = True
        context['form_title'] = 'Nuevo Usuario'
        context['submit_text'] = 'Crear Usuario'
        return context


class UserUpdateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'user/edit.html'
    permission_required = ['users.change_user']
    success_url = reverse_lazy('users:user_list')

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        # Si es AJAX, devolver las cuadrillas filtradas por área
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            area_id = request.GET.get('area_id')
            if area_id:
                crews = Crew.objects.filter(fk_area_id=area_id, is_active=True).values('id', 'name')
                return JsonResponse(list(crews), safe=False)
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        
        if form.is_valid():
            try:
                user = form.save()
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'message': f'Usuario {user.username} actualizado exitosamente',
                        'redirect_url': str(self.success_url)
                    })
                else:
                    messages.success(request, f'Usuario {user.username} actualizado exitosamente')
                    return self.form_valid(form)
            except Exception as e:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': f'Error al actualizar el usuario: {str(e)}'
                    })
                else:
                    messages.error(request, f'Error al actualizar el usuario: {str(e)}')
                    return self.form_invalid(form)
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                errors = {}
                for field, error_list in form.errors.items():
                    errors[field] = [str(error) for error in error_list]
                return JsonResponse({
                    'success': False,
                    'errors': errors
                })
            else:
                return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Editar Usuario'
        context['module'] = MODULE
        context['entity'] = ENTITY
        context['list_url'] = reverse_lazy('users:user_list')
        context['show_sidebar'] = True
        context['form_title'] = f'Editar Usuario: {self.object.username}'
        context['submit_text'] = 'Actualizar Usuario'
        context['user_gradient'] = self.object.get_gradient_colors()
        return context
