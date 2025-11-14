from django.urls import path

from apps.login.views import *

app_name = 'login'

urlpatterns = [
    path('', LoginFormView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('reset/password/', CheckPasswordRecovery.as_view(), name='reset_password'),
    path('change/password/<str:token>/', ChangePasswordView.as_view(), name='change_password'),

    # API WEB VIEW
    path('login_apiview/', LoginWebView.as_view(), name='login_apiview' )
]