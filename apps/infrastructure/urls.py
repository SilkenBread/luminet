
from django.urls import path
from apps.infrastructure.views.location.nodeViews import NodeSearchPaintingCode


app_name='infrastructure'

urlpatterns = [
    path('searchNodesByPaintingCode/<int:painting_code>/', NodeSearchPaintingCode.as_view(), name='search_node'),
]