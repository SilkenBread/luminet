from django.contrib import admin
from apps.login.models import *

@admin.register(LoginHistory)
class LoginHistoryAdmin(admin.ModelAdmin):
    search_fields = ('id','fk_user','login_date','ip_address','connection')
    list_display = ('id','fk_user','login_date','ip_address','connection')
    list_filter = ['fk_user']
