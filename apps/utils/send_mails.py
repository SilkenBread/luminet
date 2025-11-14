# standard library
import smtplib, environ, os
from pathlib import Path

# Django
from django.template.loader import render_to_string

# MIME
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def GenericSendMail(params):
        """
        Metodo genérico para envío de correos

        Author: Johan Sabogal
        Email: canoas430@gmail.com
        """
        try:
            data = {}
            BASE_DIR = Path(__file__).resolve().parent.parent

            # initialize environment variables
            env = environ.Env()
            environ.Env.read_env(os.path.join(BASE_DIR, '.env'))
            
            # URL = settings.DOMAIN if not settings.DEBUG else self.request.META['HTTP_HOST']
            mailServer = smtplib.SMTP(env('EMAIL_HOST'), env('EMAIL_PORT'))
            mailServer.starttls()
            mailServer.login(env('EMAIL_HOST_USER'),
                             env('EMAIL_HOST_PASSWORD'))
            
            # ============> NORMALMENTE ES EL CAMPO EMAIL QUIEN HACE ESTA PARTE, PERO EN ESTE CASO EL USERNAME ES EL EMAIL
            email_to = params["email_to"]
            mensaje = MIMEMultipart()
            mensaje['From'] = env('EMAIL_HOST_USER')
            mensaje['To'] = email_to
            mensaje['Subject'] = params["subject"]
            content = render_to_string(params["html"], params)
            mensaje.attach(MIMEText(content, 'html'))
            mailServer.sendmail(env('EMAIL_HOST_USER'),
                                email_to,
                                mensaje.as_string())
            data["type"] = "success"; data["msg"] = "Envio de correo exitoso"
        except Exception as e:
            data['error'] = str(e)
        return data
