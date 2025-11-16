from django.urls import path
from apps.users.views.user.views import UserListView, UserCreateView, UserUpdateView
from apps.users.views.user.apis import UserDeleteAPIView

app_name = 'users'

urlpatterns = [
    path('', UserListView.as_view(), name='user_list'),
    path('create/', UserCreateView.as_view(), name='user_create'),
    path('edit/<int:pk>/', UserUpdateView.as_view(), name='user_edit'),
    path('delete/<int:pk>/', UserDeleteAPIView.as_view(), name='user_delete'),
]
