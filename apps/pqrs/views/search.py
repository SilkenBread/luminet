# standard library
import time

# Django
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from django.core.exceptions import ValidationError

# local Django
from ..models import PqrActive, PqrClosed, PqrActiveRoute, PqrClosedRoute


MODULE_NAME = 'PQRs'
ENTITY = 'Búsqueda PQR'


@method_decorator(csrf_exempt, name='dispatch')
class GenericPqrSearch(TemplateView):
    """
    Vista genérica para búsqueda de PQR por radicado.
    """

    template_name = 'search/external.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Consultar estado PQR'
        context['module'] = MODULE_NAME
        context['entity'] = ENTITY
        context['list_url'] = reverse_lazy('pqr:externalsearch_pqr')

        file_number = self.request.GET.get('file_number', '').strip()
        context['file_number'] = file_number

        if file_number:
            search_data = self.search_by_file_number(file_number)
            context.update(search_data)
        else:
            context['has_search'] = False
            context['has_result'] = False

        return context

    def search_by_file_number(self, file_number):
        if not file_number.isdigit():
            return {
                'has_search': True,
                'has_result': False,
                'error_message': 'El número de radicado debe contener solo dígitos.',
            }

        pqr_active = PqrActive.objects.filter(file_number=int(file_number)).select_related(
            'fk_type_damage',
            'fk_origin',
            'fk_node_reported__fk_district__fk_comuna',
        ).first()

        if pqr_active:
            route_history = PqrActiveRoute.objects.filter(fk_pqr=pqr_active).order_by('input_date')
            return {
                'has_search': True,
                'has_result': True,
                'is_closed': False,
                'pqr': pqr_active,
                'route_history': route_history,
            }

        pqr_closed = PqrClosed.objects.filter(file_number=int(file_number)).select_related(
            'fk_type_damage',
            'fk_origin',
            'fk_node_reported__fk_district__fk_comuna',
        ).first()

        if pqr_closed:
            route_history = PqrClosedRoute.objects.filter(fk_pqr=pqr_closed).order_by('input_date')
            return {
                'has_search': True,
                'has_result': True,
                'is_closed': True,
                'pqr': pqr_closed,
                'route_history': route_history,
            }

        return {
            'has_search': True,
            'has_result': False,
            'error_message': f'No existe una PQR con el radicado #{file_number}.',
        }

    def post(self, request, *args, **kwargs):
        """
        Endpoint opcional JSON para búsquedas asíncronas.
        """
        start_time = time.time()

        try:
            action = request.POST.get('action')
            if action != 'search':
                raise ValidationError('Acción no válida')

            file_number = request.POST.get('file_number', '').strip()
            payload = self.search_by_file_number(file_number)

            if payload.get('has_result'):
                pqr = payload['pqr']
                payload = {
                    'type': 'success',
                    'data': {
                        'file_number': pqr.file_number,
                        'status': pqr.get_status_display(),
                        'name': pqr.name,
                        'email': pqr.email,
                        'phone_number': pqr.phone_number,
                    },
                }
            else:
                payload = {
                    'type': 'error',
                    'msg': payload.get('error_message', 'No fue posible consultar la PQR.'),
                }
        except Exception as e:
            payload = {'type': 'error', 'msg': str(e)}

        payload['time'] = str(time.time() - start_time)
        return JsonResponse(payload, safe=False)


class PqrExternalSearchView(GenericPqrSearch):
    """Búsqueda pública de PQR por número de radicado."""
    template_name = 'search/external.html'


class PqrInternalSearchView(LoginRequiredMixin, GenericPqrSearch):
    """Búsqueda interna (staff) de PQR por número de radicado."""
    template_name = 'search/internal.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['module'] = MODULE_NAME
        context['entity'] = 'Búsqueda PQR'
        context['list_url'] = reverse_lazy('pqr:internalsearch_pqr')
        context['show_sidebar'] = True
        return context
