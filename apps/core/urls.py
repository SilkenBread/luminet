from django.urls import path

from apps.core.views.dashboard import DashboardView
from apps.core.views.home import HomeView

app_name = 'core'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
]