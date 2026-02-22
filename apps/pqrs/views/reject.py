# standard library
import time

# Django
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.views.generic import View
from django.urls import reverse
from django.conf import settings as setting

# local Django
from apps.mixins import APIPermissionValidation
from .tools import PqrStatusChangeHandler
from apps.utils.send_mails import GenericSendMail
from ..models import PqrActive, CauseRejectPqr


class PqrRejectAPI(LoginRequiredMixin, APIPermissionValidation, View):
    permission_required = ['pqrs.change_pqractive']

    @transaction.atomic
    def pqr_annulment(self, **params):
        pqr_handler = PqrStatusChangeHandler(params['pqr'])
        pqr_handler.validate_status(0, params['user'])
        pqr_handler.change_status(0)
        pqr_handler.create_route(2, params['cause'])
        pqr_handler.move_to_close()

        # Anular órdenes asociadas si existen
        try:
            from apps.order.views.tools import OrderStatusChangeHandler
            orders = params['pqr'].orderactive_set.all()

            for order in orders:
                order_handler = OrderStatusChangeHandler(order)
                init_state = order.status
                order_handler.validate_status(0, params['user'])
                order_handler.change_status(0)
                order_handler.create_route(params['user'], init_state)
                order_handler.move_to_close()
        except (ImportError, AttributeError):
            pass

        self.send_email_annulment(params['pqr'], params['cause'])
        return {'type': 'success', 'msg': f'Se ha anulado la PQR #{params["pqr"].file_number} correctamente.'}

    def send_email_annulment(self, pqr, cause):
        base_src = "https://d15k2d11r6t6rl.cloudfront.net/public/users/Integrators/BeeProAgency/1072339_1057598"
        src = f"{base_src}/resuelto.png"

        text = cause.description if cause else ''

        URL = setting.DOMAIN if not setting.DEBUG else f"http://{self.request.META['HTTP_HOST']}"
        try:
            rutaEstadoPqr = f"{URL}{reverse('pqr:externalsearch_pqr')}"
        except Exception:
            rutaEstadoPqr = URL

        params = {
            'email_to': pqr.email,
            'subject': 'Reportes Alumbrado Público',
            'html': 'statepqr_email.html',
            'title_mail': 'Anulación de Reporte',
            'body_mail': f"Señor(a) {pqr.name}, su reporte por {str(pqr.fk_type_damage)} ha sido anulado. {text}",
            'action_link': rutaEstadoPqr,
            'action_title': 'Consultar estado del reporte',
            'image_src': src
        }
        GenericSendMail(params)

    def get(self, request, *args, **kwargs):
        try:
            start_time = time.time()
            causes = CauseRejectPqr.objects.filter(is_active=True).values('id', 'name')
            data = {'type': 'success', 'data': list(causes)}
        except Exception as e:
            data = {'type': 'error', 'msg': str(e)}
        data['time'] = str(time.time() - start_time)
        return JsonResponse(data, safe=False)

    def post(self, request, *args, **kwargs):
        try:
            start_time = time.time()
            params = {
                'pqr': get_object_or_404(PqrActive, id=int(request.POST['id_pqr'])),
                'cause': get_object_or_404(CauseRejectPqr, id=int(request.POST['id_cause'])),
                'user': request.user
            }
            # Anulación de PQR
            data = self.pqr_annulment(**params)

            # Eliminación de PQR activa e históricos
            params['pqr'].pqractiveroute_set.all().delete()
            params['pqr'].delete()
        except Exception as e:
            data = {'type': 'error', 'msg': str(e)}
        data['time'] = str(time.time() - start_time)
        return JsonResponse(data, safe=False)
