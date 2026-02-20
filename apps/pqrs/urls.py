from django.urls import path

from apps.pqrs.views.creation import PqrCreateView, PqrIntenalCreateView, ValidateNodeInPqrView, PqrCreationAPI
from apps.pqrs.views.search import PqrExternalSearchView, PqrInternalSearchView
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
    path('api/validateNode/', ValidateNodeInPqrView.as_view(), name='validate_node_pqr'),
    path('api/create/', PqrCreationAPI.as_view(), name='api_create_pqr'),

    # BUSQUEDA DE PQRs
    path('search/', PqrExternalSearchView.as_view(), name='externalsearch_pqr'), # Externa
    path('search/internal/', PqrInternalSearchView.as_view(), name='internalsearch_pqr'), # Interna
    
    # TODO: Agregar URLs para editar, ver detalle, etc.
]
