from django.urls import path

from apps.pqrs.views.creation import PqrCreateView, PqrIntenalCreateView, ValidateNodeInPqrView, PqrCreationAPI
from apps.pqrs.views.search import PqrExternalSearchView, PqrInternalSearchView
from .views.list import PqrReceiveListView, PqrReviewListView, PqrAtendedListView
from .views.tools import PqrStatusChangeAPI
from .views.reject import PqrRejectAPI
from .views.detail import PqrDetailAPI

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

    # APIs - Cambio de estado, Rechazo, Detalle
    path('api/statusChange/', PqrStatusChangeAPI.as_view(), name='api_pqr_status_change'),
    path('api/reject/', PqrRejectAPI.as_view(), name='api_pqr_reject'),
    path('api/detail/<int:pk>/', PqrDetailAPI.as_view(), name='api_pqr_detail'),
]
