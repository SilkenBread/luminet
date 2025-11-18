# Django
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.apps import apps
from django.urls import reverse_lazy

MODULE_NAME = 'PQRs'
ENTITY = 'PQRs'

class GenericPqrCreateView(TemplateView):
    """
    VISTAS GENERICA PARA LA CREACION DE PQRs (EXTERNAS E INTERNAS)
    """    
    def get_post_data(self, action):
        try:
            if action == 'getTypeDamage':
                GeneralTypeDamage = apps.get_model('pqrs', 'GeneralTypeDamage')
                
                data ={'type': 'success',
                       'data': {
                           'typeDamage': list(GeneralTypeDamage.objects.all().values('id', 'name')),
                           'origin': self.get_origin_data()}}
            else:
                raise ValueError('Ha ocurrido un error')
        except Exception as e:
            data = {'type': 'error', 'msg': str(e)}
        return data
    
    def get_origin_data(self):
        Origin = apps.get_model('pqrs', 'Origin')
        return list(Origin.objects.all().values('id', 'name'))
    
    def post(self, request, *args, **kwargs):
        action = request.POST.get('action')
        data = self.get_post_data(action)
        return JsonResponse(data, safe=False)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Creación de PQR'
        context['module'] = MODULE_NAME
        context['entity'] = 'Creación PQR'
        return context


@method_decorator(csrf_exempt, name='dispatch') 
class PqrCreateView(GenericPqrCreateView):    
    template_name = 'creation/external.html'


@method_decorator(csrf_exempt, name='dispatch') 
class PqrIntenalCreateView(LoginRequiredMixin, GenericPqrCreateView):
    template_name = 'creation/internal.html'

    def get_origin_data(self):
        Origin = apps.get_model('pqrs', 'Origin')
        return list(Origin.objects.filter(fk_group=self.request.user.groups.first()).values('id', 'name'))
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Creación PQR Interna'
        context['module'] = MODULE_NAME
        context['entity'] = 'Creación PQR Interna'
        context['list_url'] = reverse_lazy('pqrs:list_receivepqr')
        context['show_sidebar'] = True
        return context
