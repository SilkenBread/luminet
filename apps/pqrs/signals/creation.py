
from django.dispatch import receiver
from django.db.models import signals

from django.urls import reverse
from django.apps import apps
from ..models import PqrActive, PqrActiveRoute, FileNumber
from config.settings import DOMAIN

from apps.utils.send_mails import GenericSendMail

@receiver(signals.pre_save, sender = PqrActive)
def create_pqr_file_number(sender, instance, **kwargs):
    if instance._state.adding and not instance.file_number:
        instance.file_number = FileNumber.objects.create().value

@receiver(signals.post_save, sender = PqrActive)
def send_email_pqr_creation(sender, instance, created, **kwargs):
    if created:
        # Crear ruta de la PQR
        routeInstance = PqrActiveRoute(fk_pqr = instance, state = 1)
        routeInstance.save()

        # Crear Reporter si la PQR tiene DNI, si esta creada actualizarla
        if instance.dni:
            Report = apps.get_model('user', 'Reporter')
            reporter, created = Report.objects.get_or_create(dni = instance.dni)
            if reporter:
                reporter.name = instance.name
                reporter.phone_number = instance.phone_number
                reporter.email = instance.email
                reporter.save()

    rutaEstadoPqr = f"{DOMAIN}{reverse('pqr:externalsearch_pqr')}"
    action_title = 'Consultar estado del reporte'

    # Las imagenes del estado de las PQR se encuentran en una cuenta beefre asociada al correo juan.rodriguez.rubio@correounivalle.edu.co
    base_src = "https://d15k2d11r6t6rl.cloudfront.net/public/users/Integrators/BeeProAgency/1072339_1057598"

    match instance.status:
        case 1:
            src = f"{base_src}/recibido.png"
            title_mail = f"Creación de Reporte #{instance.file_number}"
            text = f"ha sido creado y recibido satisfactoriamente con el radicado #{instance.file_number}. A este correo enviaremos las novedades sobre el estado del reporte."
        case 2:
            src = f"{base_src}/proceso.png"
            title_mail = f"Estado del Reporte #{instance.file_number}"
            text = f"con radicado #{instance.file_number} se encuentra en proceso de atención. En los próximos días se enviará a este correo las novedades de su reporte."
        case 3:
            src = f"{base_src}/resuelto.png"
            title_mail = f"Estado del Reporte #{instance.file_number}"
            text = f"con radicado #{instance.file_number} ya fue resuelto. Por lo tanto, se da cierre a esta PQR."
        case _:
            src = ''
            text= ''
    
    allowed_mail_status = [1, 2, 3]
    if instance.status not in allowed_mail_status:
        return
    
    params = {
        'email_to': instance.email,
        'subject': 'Reportes Alumbrado Público',
        'html': 'statepqr_email.html',
        'title_mail': title_mail,
        'body_mail': f"Señor(a) {instance.name}, su reporte por {str(instance.fk_type_damage.name)} {text}",
        'action_link': rutaEstadoPqr,
        'action_title': action_title,
        'image_src': src
    }
    GenericSendMail(params)
