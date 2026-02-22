from django.urls import path
from .views.list import (
    OrderActiveListState1,
    OrderActiveListState2,
    OrderActiveListState3,
    OrderClosedListState4,
)
from .views.creation import (
    GetOrderFieldsAPI,
    ConfirmOrderCreationAPI,
    SetOrderActiveAPI,
)
from .views.tools import OrderStatusChangeAPI

app_name = 'order'

urlpatterns = [
    # List views por área
    path('OrderActive/<str:area>/state1/', OrderActiveListState1.as_view(), name='list_ot_active_state1'),
    path('OrderActive/<str:area>/state2/', OrderActiveListState2.as_view(), name='list_ot_active_state2'),
    path('OrderActive/<str:area>/state3/', OrderActiveListState3.as_view(), name='list_ot_active_state3'),
    path('OrderClosed/<str:area>/state4/', OrderClosedListState4.as_view(), name='list_ot_closed_state4'),

    # APIs
    path('api/getFields/', GetOrderFieldsAPI.as_view(), name='api_get_order_fields'),
    path('api/confirmCreation/', ConfirmOrderCreationAPI.as_view(), name='confirm_order_creation'),
    path('api/setOrderActive/', SetOrderActiveAPI.as_view(), name='api_set_orderactive'),
    path('api/changeStatus/<str:model>/<int:id>/<int:state>/', OrderStatusChangeAPI.as_view(), name='api_order_status_change'),
]
