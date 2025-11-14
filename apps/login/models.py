from datetime import datetime

# Django
from django.db import models
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in, user_logged_out 

# django-user-agents
from django_user_agents.utils import get_user_agent

# local Django
from apps.users.models import User

class LoginHistory(models.Model):
    fk_user = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=False, verbose_name='Usuario')
    login_date = models.DateTimeField(verbose_name='Inicio de seción', auto_now_add=True, null=True, blank=True)
    ip_address = models.GenericIPAddressField(verbose_name='Dirección IP')
    connection = models.CharField(max_length=255, unique=False, null=True, blank=False, verbose_name='Información conexión')

    class Meta:
        db_table = 'LOGIN_HISTORY'
        verbose_name = 'Historial inicio sesión'
        verbose_name_plural = 'Historial inicios de sesión'
        ordering = ['-id']


@receiver(user_logged_in)
def loginSignal(sender, request, user, **kwargs):
    """
    Manejador de señales para el evento de inicio de sesión de un usuario.

    Parámetros:
        - sender: El remitente de la señal.
        - request: La solicitud de inicio de sesión.
        - user: El usuario que ha iniciado sesión.
        - kwargs: Argumentos adicionales de la señal (pueden variar según la implementación).

    Este manejador registra el historial de inicio de sesión del usuario, almacenando la dirección IP
    y conexión en un modelo LoginHistory.
    """
    req_headers = request.META
    user_agent = get_user_agent(request)
    x_forwarded_for_value = req_headers.get('HTTP_X_FORWARDED_FOR')

    # Determinar la dirección IP del usuario
    if x_forwarded_for_value:
        ip_addr = x_forwarded_for_value.split(',')[-1].strip()
    else:
        ip_addr = req_headers.get('REMOTE_ADDR')

    # Crear una instancia de LoginHistory y guardarla en la base de datos
    login_instance = LoginHistory(
        fk_user=user,        # Asignar el usuario que ha iniciado sesión
        ip_address=ip_addr,  # Asignar la dirección IP del usuario
        connection=user_agent  # Asignar el agente de conexión (User-Agent)
    )
    login_instance.save()
