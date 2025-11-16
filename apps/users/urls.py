from django.urls import path
from apps.users.views.user.views import UserListView

app_name = 'users'

urlpatterns = [
    path('', UserListView.as_view(), name='user_list'),
]
