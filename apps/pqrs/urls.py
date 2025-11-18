from django.urls import path

from apps.pqrs.views.creation import PqrCreateView, PqrIntenalCreateView
from .views.list import PqrReceiveListView, PqrReviewListView, PqrAtendedListView

app_name = 'pqrs'

urlpatterns = [
    # Listados de PQRs por estado
    path('recibidas/', PqrReceiveListView.as_view(), name='list_receivepqr'),
    path('revision/', PqrReviewListView.as_view(), name='list_reviewpqr'),
    path('atendidas/', PqrAtendedListView.as_view(), name='list_atendedpqr'),

    # CREACION DE PQRs
    path('crear/', PqrCreateView.as_view(), name='create_pqr'), # Externa
    path('crear/interna/', PqrIntenalCreateView.as_view(), name='create_internal_pqr'), # Interna
    
    # TODO: Agregar URLs para editar, ver detalle, etc.
]
