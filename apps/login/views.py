# standard library
import uuid, os, environ, json
from pathlib import Path

# Django
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout, authenticate
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import FormView, RedirectView
from django.http import HttpResponseRedirect, JsonResponse

# local Django
import config.settings as setting
# from config import settings
from apps.login.forms import ResetPasswordForm, ChangePasswordForm, LoginForm
from apps.users.models import User
from apps.utils.send_mails import GenericSendMail

from django.core.cache import cache
from django.utils.crypto import get_random_string


class LoginFormView(LoginView):
    """
    Vista basada en clase iniciar sesión
    """
    form_class = LoginForm
    template_name = 'login.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(setting.LOGIN_REDIRECT_URL)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Inicio de sesión'
        return context

class LogoutView(RedirectView):
    """
    Vista basada en clase para cerrar sesión
    """
    pattern_name = 'login:login'

    def dispatch(self, request, *args, **kwargs):
        logout(request)
        return super().dispatch(request, *args, **kwargs)
    
class CheckPasswordRecovery(FormView):
    """
    Vista basada en clase para validar el usuario que quiere cambiar la contraseña
    """
    form_class = ResetPasswordForm
    template_name = 'recovery_password.html'
    success_url = reverse_lazy(setting.LOGIN_REDIRECT_URL)

    def send_email_reset_pwd(self, user):
        URL = setting.DOMAIN if not setting.DEBUG else f"http://{self.request.META['HTTP_HOST']}"

        token = get_random_string(length=32)
        cache.set(token, user.pk, timeout=3600)  # Store token in cache for 1 hour

        # Generate the dynamic URL using reverse
        action_link = URL + reverse('login:change_password', kwargs={'token': token})

        params = {
            'email_to': user.email,
            'subject': 'Cambio de contraseña',
            'html': 'signup_email.html',
            'title_mail': 'Cambio de contraseña',
            'body_mail': f"Señor(a) {user.get_full_name()}, Para poder cambiar tu contraseña debes dar click en el botón cambiar y sigue los pasos para resetear tu contraseña",
            'action_link': action_link,
            'action_title': 'Cambiar'
        }
        GenericSendMail(params)
    
    def post(self, request, *args, **kwargs):
        try:
            params = json.loads(request.body)
            username = params['username']

            if not User.objects.filter(is_active=True, username=username).exists():
                raise ValueError(f"El usuario con nombre de usuario '{username}' no existe o se encuentra inactivo")
            
            user = User.objects.get(username=username)
            self.send_email_reset_pwd(user)

            data = {
                'type': 'success',
                'msg': f'Se ha enviado un correo a {user.email} para recuperar tu contraseña'
            }
        except Exception as e:
            data = {'type': 'error', 'msg': str(e)}
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Validación para recuperación de contraseña'
        return context

    
class ChangePasswordView(FormView):
    """
    Vista basada en clase para cambiar la contraseña
    """
    form_class = ChangePasswordForm
    template_name = 'change_password.html'
    success_url = reverse_lazy(setting.LOGIN_REDIRECT_URL)

    def get(self, request, *args, **kwargs):
        token = self.kwargs['token']
        user_id = cache.get(token)
        if user_id:
            return super().get(request, *args, **kwargs)
        return HttpResponseRedirect('/')

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            form = ChangePasswordForm(request.POST)
            if form.is_valid():
                token = self.kwargs['token']
                user_id = cache.get(token)

                if user_id:
                    user = User.objects.get(pk=user_id)
                    user.set_password(request.POST['password'])
                    user.save()

                    cache.delete(token)
            else:
                data['error'] = form.errors
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Cambio de Contraseña'
        context['login_url'] = setting.LOGIN_URL
        return context


@method_decorator(csrf_exempt, name='dispatch')
class LoginWebView(View):
    """
    Vista basada en clase para loguearse desde el web view
    """
    def post(self, request, *args, **kwargs):
        data = dict()
        try:
            username = request.POST.get('username', '')
            password = request.POST.get('password', '')
            user = authenticate(username=username,password=password)
            if user:
                data['type']='success'
                data['msg']='Has iniciado sesión correctamente.'
                data['data']= user.toJSON()
            else:
                raise ValueError('No se pudo iniciar sesión. Credenciales incorrectas')
        except Exception as e:
            data['type']='error'
            data['msg']= str(e)
        return JsonResponse(data, safe=False)
