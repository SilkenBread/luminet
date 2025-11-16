# standard library
import os
import environ
from pathlib import Path

# Django
from django.template.loader import render_to_string

# Resend
import resend
from resend import Emails

def GenericSendMail(params):
    """
    Metodo genérico para envío de correos usando Resend
    """
    try:
        data = {}
        BASE_DIR = Path(__file__).resolve().parent.parent

        env = environ.Env()
        environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

        resend.api_key = env("RESEND_API_KEY")

        email_data = {
            "from": env("EMAIL_HOST_USER"),  # ej: "Mi App <onboarding@resend.dev>"
            "to": [params["email_to"]],
            "subject": params["subject"],
            "html": render_to_string(params["html"], params),
        }

        Emails.send(email_data)  # ✔ correcto para la versión 2.x

        data["type"] = "success"
        data["msg"] = "Envio de correo exitoso"

    except Exception as e:
        data["error"] = str(e)

    return data
