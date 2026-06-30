from django.views.generic import TemplateView

class HomeView(TemplateView):
    """
    Página de inicio pública de Luminet.

    Métodos HTTP: GET
    Respuesta: HTML (home.html)
    """
    template_name = 'home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Inicio'
        context['show_sidebar'] = True
        return context
