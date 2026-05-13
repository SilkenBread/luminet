from django.urls import path

from apps.infrastructure.views.location.comunaViews import ComunaSearchAllView
from apps.infrastructure.views.location.districtViews import DistrictSearchByComuna
from apps.infrastructure.views.location.nodeViews import (
    NodeInDistrictView,
    NodeSearchComunaView,
    NodeSearchId,
    NodeSearchInArea,
    NodeSearchPaintingCode,
    SearchInfrastructureInNodeView,
)
from apps.infrastructure.views.node.crud import (
    NodeCreateAPI,
    NodeDeleteAPI,
    NodeUpdateAPI,
)
from apps.infrastructure.views.node.list import NodeListView


app_name = "infrastructure"

urlpatterns = [
    # Vista principal de Nodos
    path("nodes/", NodeListView.as_view(), name="list_nodes"),

    # APIs CRUD de Node
    path("api/node/create/", NodeCreateAPI.as_view(), name="api_node_create"),
    path("api/node/<int:pk>/", NodeUpdateAPI.as_view(), name="api_node_detail"),
    path("api/node/<int:pk>/delete/", NodeDeleteAPI.as_view(), name="api_node_delete"),

    # APIs de búsqueda de Nodes
    path("api/nodes/by-painting-code/<int:painting_code>/", NodeSearchPaintingCode.as_view(), name="search_node"),
    path("api/nodes/by-district/", NodeInDistrictView.as_view(), name="nodes_by_district"),
    path("api/nodes/by-comuna/", NodeSearchComunaView.as_view(), name="nodes_by_comuna"),
    path("api/nodes/by-id/<int:id>/", NodeSearchId.as_view(), name="node_by_id"),
    path("api/nodes/in-area/", NodeSearchInArea.as_view(), name="nodes_in_area"),
    path("api/nodes/<int:pk>/infrastructure/", SearchInfrastructureInNodeView.as_view(), name="node_infrastructure"),

    # APIs de geografía consumidas por el mapa
    path("api/comunas/", ComunaSearchAllView.as_view(), name="api_comunas"),
    path("api/comunas/<int:comuna>/districts/", DistrictSearchByComuna.as_view(), name="api_districts_by_comuna"),
]
