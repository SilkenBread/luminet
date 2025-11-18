from django.contrib import admin
from django.utils.html import format_html

from simple_history.admin import SimpleHistoryAdmin

# local Django
from .models import *

# Django import export
from import_export import resources
from import_export.admin import ImportExportModelAdmin


class PqrActiveResource(resources.ModelResource):
    class Meta:
        model = PqrActive

@admin.register(PqrActive)
class PqrActiveAdmin(ImportExportModelAdmin):
    resource_class= PqrActiveResource
    search_fields = ('id','file_number','name','phone_number','dni','email','observation')
    list_display = ('id','file_number','name','phone_number','email','fk_type_damage','status')
    list_filter = ['date_creation', 'status','fk_type_damage']

# PQR CLOSED
class PqrClosedResource(resources.ModelResource):
    class Meta:
        model = PqrClosed

@admin.register(PqrClosed)
class PqrClosedAdmin(ImportExportModelAdmin):
    resource_class= PqrClosedResource
    search_fields = ('id','file_number','name','phone_number','dni','email','observation')
    list_display = ('id','file_number','name','phone_number','email','fk_type_damage','status')
    list_filter = ['date_creation', 'status','fk_type_damage']


@admin.register(GeneralTypeDamage)
class GeneralTypeDamageAdmin(admin.ModelAdmin):
    search_fields = ('id','name')
    list_display = ('id','name')
    readonly_fields = ['user_creation', 'user_updated','date_creation','date_updated']


@admin.register(Origin)
class OriginAdmin(admin.ModelAdmin):
    search_fields = ('id','name')
    list_display = ('id','name')
    readonly_fields = ['user_creation', 'user_updated','date_creation','date_updated']


@admin.register(CauseRejectPqr)
class CauseRejectPqrAdmin(admin.ModelAdmin):
    search_fields = ('id','name')
    list_display = ('id','name', 'description', 'is_active')
    readonly_fields = ['user_creation', 'user_updated','date_creation','date_updated']


@admin.register(PqrActiveRoute)
class PqrActiveRouteAdmin(admin.ModelAdmin):
    search_fields = ('id','fk_pqr','state','input_date','output_date')
    list_display = ('id','fk_pqr','state','input_date','output_date','cause')
    list_filter = ['state','cause']

@admin.register(PqrClosedRoute)
class PqrClosedRouteAdmin(admin.ModelAdmin):
    search_fields = ('id','fk_pqr','state','input_date','output_date')
    list_display = ('id','fk_pqr','state','input_date','output_date','cause')
    list_filter = ['state','cause']


