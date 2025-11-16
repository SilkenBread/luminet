from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'

    def get_active_users(self):
        from apps.users.models import User
        return User.objects.filter(is_active=True).count()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Dashboard - Luminet'
        context['list_url'] = reverse_lazy('core:dashboard')
        context['show_sidebar'] = True
        context['module'] = 'Dashboard'
        context['active_users_count'] = self.get_active_users()
        return context
