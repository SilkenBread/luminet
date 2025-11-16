from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views import View
from apps.mixins import ValidatePermissionRequiredMixin
from apps.users.models import User


class UserDeleteAPIView(LoginRequiredMixin, ValidatePermissionRequiredMixin, View):
    """API para eliminar usuarios con validaciones"""
    permission_required = ['users.delete_user']

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, pk, *args, **kwargs):
        try:
            # Obtener el usuario a eliminar
            user_to_delete = User.objects.get(pk=pk)
            
            # Validación 1: No puede eliminarse a sí mismo
            if user_to_delete.id == request.user.id:
                return JsonResponse({
                    'success': False,
                    'message': 'No puedes eliminar tu propio usuario. Por favor, contacta a otro administrador.'
                }, status=400)
            
            # Validación 2: No eliminar superusuarios (opcional, por seguridad)
            if user_to_delete.is_superuser and not request.user.is_superuser:
                return JsonResponse({
                    'success': False,
                    'message': 'No tienes permisos para eliminar un superusuario.'
                }, status=403)
            
            # Validación 3: Verificar si el usuario tiene dependencias críticas
            # (Puedes agregar más validaciones según tus modelos)
            
            # Guardar información para el mensaje
            username = user_to_delete.username
            full_name = user_to_delete.get_full_name()
            
            # Eliminar el usuario
            user_to_delete.delete()
            
            return JsonResponse({
                'success': True,
                'message': f'Usuario "{username}" ({full_name}) eliminado exitosamente'
            })
            
        except User.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'El usuario no existe o ya fue eliminado'
            }, status=404)
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al eliminar el usuario: {str(e)}'
            }, status=500)
