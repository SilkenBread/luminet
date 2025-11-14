from django.template.loader import render_to_string
from django.http import HttpResponse
from weasyprint import HTML
from django.conf import settings
import json
from datetime import datetime

class PDFGenerator:
    def __init__(self, template_path):
        """
        Inicializa el generador de PDF con la ruta de la plantilla base
        
        Args:
            template_path (str): Ruta a la plantilla HTML base
        """
        self.template_path = template_path

    def generate_pdf(self, context_data, filename=None):
        """
        Genera un PDF a partir de una plantilla HTML y datos de contexto
        
        Args:
            context_data (dict): Datos para renderizar en la plantilla
            filename (str, optional): Nombre del archivo PDF a generar
        
        Returns:
            HttpResponse: Respuesta HTTP con el PDF generado
        """
        # Renderiza la plantilla HTML con el contexto
        html_string = render_to_string(self.template_path, context_data)
        
        # Genera el PDF
        html = HTML(string=html_string, base_url=settings.STATIC_URL)
        pdf = html.write_pdf()
        
        # Configura la respuesta HTTP
        if not filename:
            filename = f'report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
