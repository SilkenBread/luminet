# Django
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.generic import TemplateView
from django.views import View
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.apps import apps
from django.urls import NoReverseMatch, reverse, reverse_lazy

# standard library
import time

from apps.pqrs.signals.sse import pqr_created

MODULE_NAME = 'PQRs'
ENTITY = 'PQRs'

class GenericPqrCreateView(TemplateView):
    """
    Vista base para la creación de PQRs; POST devuelve datos de dropdowns (tipo de daño, origen).

    Métodos HTTP: GET, POST (action=getTypeDamage)
    Respuesta: HTML | JSON
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
    """Formulario público de creación de PQR; exento de CSRF."""
    template_name = 'creation/external.html'


@method_decorator(csrf_exempt, name='dispatch')
class PqrIntenalCreateView(LoginRequiredMixin, GenericPqrCreateView):
    """Formulario interno de creación de PQR; filtra origen por el grupo del usuario autenticado."""
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


class ValidateNodeInPqrView(View):
    """
    API para validar si un nodo ya esta reportado en una PQR
    """

    def check_node(self, node_id):
        PqrActive = apps.get_model('pqrs', 'PqrActive')
        return PqrActive.objects.filter(Q(fk_node_reported=int(node_id)), Q(status=1) | Q(status=2))

    def post(self, request, *args, **kwargs):
        start_time = time.time()
        data = dict()

        try:
            check_node = self.check_node(request.POST['value'])

            if not check_node:
                Node = apps.get_model('infrastructure', 'Node')
                node_instance = get_object_or_404(Node, pk=request.POST['value'])

                data = {
                    'type': 'success',
                    'msg': f"Has seleccionado el poste {node_instance.painting_code}",
                    'data': {
                        'id': str(node_instance.pk),
                        'painting_code': str(node_instance.painting_code),
                    }
                }
            else:
                file_number = check_node.first().file_number

                try:
                    url_ext_search = reverse('pqr:externalsearch_pqr')
                    raise ValueError(
                        f"Este poste ya tiene una PQR activa con el radicado #{file_number}. "
                        f"<a href='{url_ext_search}' target='_blank' class='text-danger'>Consulta su estado aquí</a>"
                    )
                except NoReverseMatch:
                    raise ValueError(f"Este poste ya tiene una PQR activa con el radicado #{file_number}.")
        except Exception as e:
            data = {'type': 'error', 'msg': str(e)}

        data['time'] = str(time.time() - start_time)
        return JsonResponse(data, safe=False)


class PqrCreationAPI(View):
    """
    API para crear un PQR
    """

    @transaction.atomic
    def create_pqr(self, params, node):
        PqrActive = apps.get_model('pqrs', 'PqrActive')
        GeneralTypeDamage = apps.get_model('pqrs', 'GeneralTypeDamage')
        Origin = apps.get_model('pqrs', 'Origin')

        return PqrActive.objects.create(
            fk_type_damage=GeneralTypeDamage.objects.get(id=params['typeDamage']),
            fk_node_reported=node,
            fk_origin=Origin.objects.get(id=params['origin']),
            name=params['name'],
            dni=params['identification'] or None,
            phone_number=params['contact_phoneNumber'],
            email=params['email'],
            observation=f"{params['observations']}",
        )

    def post(self, request, *args, **kwargs):
        start_time = time.time()

        try:
            params = request.POST.dict()

            Node = apps.get_model('infrastructure', 'Node')
            node = get_object_or_404(Node, pk=params['idNode'])

            if node:
                create = self.create_pqr(params, node)

                pqr_created.send(sender=apps.get_model('pqrs', 'PqrActive'), instance=create)
            else:
                raise ValueError('No es posible crear la PQR, el nodo no fue encontrado.')

            data = {
                'type': 'success',
                'msg': f"Se ha reportado correctamente el daño con el radicado #{create.file_number}",
            }
        except Exception as e:
            data = {'type': 'error', 'msg': str(e)}

        data['time'] = str(time.time() - start_time)
        return JsonResponse(data, safe=False)
