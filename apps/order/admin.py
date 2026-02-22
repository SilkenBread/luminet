# Django
from django.contrib import admin

# third-party
from import_export.admin import ImportExportModelAdmin
from import_export import resources

# local Django
from .models import (
    Priority, InternalTypeDamage, Activities, TimingRepair,
    CauseRejectOrder, TypeOrder, OrderActive, OrderClosed,
    OrderActiveRoute, OrderClosedRoute
)


class InternalTypeDamageResource(resources.ModelResource):
    class Meta:
        model = InternalTypeDamage


@admin.register(Priority)
class PriorityAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']


@admin.register(InternalTypeDamage)
class InternalTypeDamageAdmin(ImportExportModelAdmin):
    resource_class = InternalTypeDamageResource
    list_display = ['id', 'name', 'fk_priority', 'fk_general_damage']
    search_fields = ['name']
    list_filter = ['fk_priority']


@admin.register(Activities)
class ActivitiesAdmin(admin.ModelAdmin):
    list_display = ['id', 'code', 'name', 'is_active']
    search_fields = ['name', 'code']
    list_filter = ['is_active']


@admin.register(TimingRepair)
class TimingRepairAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'timing_reparation']


@admin.register(CauseRejectOrder)
class CauseRejectOrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'is_active']
    list_filter = ['is_active']


@admin.register(TypeOrder)
class TypeOrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'is_active']
    list_filter = ['is_active']


@admin.register(OrderActive)
class OrderActiveAdmin(admin.ModelAdmin):
    list_display = ['id', 'fk_pqr', 'status', 'fk_internal_type_damage', 'fk_priority', 'fk_area', 'fk_crew', 'date_creation']
    list_filter = ['status', 'fk_area', 'fk_priority']
    search_fields = ['id', 'fk_pqr__file_number']
    raw_id_fields = ['fk_pqr']


@admin.register(OrderClosed)
class OrderClosedAdmin(admin.ModelAdmin):
    list_display = ['id', 'fk_pqr', 'status', 'fk_internal_type_damage', 'fk_priority', 'fk_area', 'date_creation']
    list_filter = ['status', 'fk_area']
    search_fields = ['id']
    raw_id_fields = ['fk_pqr']


@admin.register(OrderActiveRoute)
class OrderActiveRouteAdmin(admin.ModelAdmin):
    list_display = ['id', 'fk_ot', 'state', 'input_date', 'output_date', 'cause']
    list_filter = ['state']


@admin.register(OrderClosedRoute)
class OrderClosedRouteAdmin(admin.ModelAdmin):
    list_display = ['id', 'fk_ot', 'state', 'input_date', 'output_date', 'cause']
    list_filter = ['state']
