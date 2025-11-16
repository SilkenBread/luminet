from django.contrib import admin
from leaflet.admin import LeafletGeoAdmin

from apps.infrastructure.models import *
from import_export import resources
from import_export.admin import ImportExportModelAdmin

# Cambiamos el nombre del grupo en el admin
admin.site.index_title = "Panel de Control"
admin.site.site_header = "Administración Alumbrado Público"

# MODELOS AUXILIARES
@admin.register(LuminaireTech)
class LuminaireTechAdmin(admin.ModelAdmin):
    search_fields = ('id','code','name')
    list_display = ('id','code','name')

@admin.register(ArmType)
class ArmTypeAdmin(admin.ModelAdmin):
    search_fields = ('id','code','name')
    list_display = ('id','code','name')

@admin.register(OpticProtection)
class OpticProtectionAdmin(admin.ModelAdmin):
    search_fields = ('id','code','name')
    list_display = ('id','code','name')

@admin.register(LuminaireType)
class LuminaireTypeAdmin(admin.ModelAdmin):
    search_fields = ('id','code','name')
    list_display = ('id','code','name')

@admin.register(PhotoCellType)
class PhotoCellTypeAdmin(admin.ModelAdmin):
    search_fields = ('id','code','name')
    list_display = ('id','code','name')

@admin.register(LightedSpace)
class LightedSpaceAdmin(admin.ModelAdmin):
    search_fields = ('id','code','name')
    list_display = ('id','code','name')

@admin.register(LuminaireSupport)
class LuminaireSupportAdmin(admin.ModelAdmin):
    search_fields = ('id','code','name')
    list_display = ('id','code','name')

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    search_fields = ('id','code','name')
    list_display = ('id','code','name')

@admin.register(SupportType)
class SupportTypeAdmin(admin.ModelAdmin):
    search_fields = ('id','code','name')
    list_display = ('id','code','name')

@admin.register(SupportCimentation)
class SupportCimentationAdmin(admin.ModelAdmin):
    search_fields = ('id','code','name')
    list_display = ('id','code','name')

@admin.register(NetCaliber)
class NetCaliberAdmin(admin.ModelAdmin):
    search_fields = ('id','code','name')
    list_display = ('id','code','name')

@admin.register(TrafoPower)
class TrafoPowerAdmin(admin.ModelAdmin):
    search_fields = ('id','power')
    list_display = ('id','power')

@admin.register(SupportHeight)
class SupportHeightAdmin(admin.ModelAdmin):
    search_fields = ('id','value')
    list_display = ('id','value')

@admin.register(BreakingCapacity)
class BreakingCapacityAdmin(admin.ModelAdmin):
    search_fields = ('id','value')
    list_display = ('id','value')

# MODELOS UBICACION
class ComunaResource(resources.ModelResource):
    class Meta:
        model = Comuna

@admin.register(Comuna)
class ComunaAdmin(ImportExportModelAdmin, LeafletGeoAdmin):
    resource_class= ComunaResource
    search_fields = ('id','name','type')
    list_display = ('id','name','type')
    list_filter = ['type']
    readonly_fields = ['user_creation', 'user_updated','date_creation','date_updated']

class DistrictResource(resources.ModelResource):
    class Meta:
        model = District

@admin.register(District)
class DistrictAdmin(ImportExportModelAdmin, LeafletGeoAdmin):
    resource_class= DistrictResource
    search_fields = ('id','name','estrato','cod_unico','fk_comuna')
    list_display = ('id','name','estrato','cod_unico','fk_comuna')
    list_filter = ['fk_comuna','estrato']
    readonly_fields = ['user_creation', 'user_updated','date_creation','date_updated']

@admin.register(Node)
class NodeAdmin(LeafletGeoAdmin):
    search_fields = ('id','painting_code','fk_district')
    list_display = ('id','painting_code','fk_district')
    list_filter = ['fk_district__fk_comuna']
    readonly_fields = ['user_creation', 'user_updated','date_creation','date_updated']

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    search_fields = ('id','name')
    list_display = ('id','name')

class TrafoResource(resources.ModelResource):
    class Meta:
        model = Trafo

@admin.register(Trafo)
class TrafoAdmin(ImportExportModelAdmin):
    resource_class= TrafoResource
    search_fields = ('id','code','fk_node','owner','type','installationtype','using','power')
    list_display = ('id','code','fk_node','owner','type','installationtype','using','power','status')
    list_filter = ['owner','using','type']

@admin.register(Meter)
class MeterAdmin(admin.ModelAdmin):
    search_fields = ('id','fk_trafo')
    list_display = ('id','fk_trafo','inbox','connection','status')
    list_filter = ['connection','status']

@admin.register(Net)
class NetAdmin(admin.ModelAdmin):
    search_fields = ('id','fk_trafo','typeinstallation','conductor','fk_material','caliber','length','setting','surface','last_node','current_node')
    list_display = ('id','fk_trafo','typeinstallation','conductor','fk_material','caliber','length','setting','surface','last_node','current_node')
    list_filter = ['typeinstallation','conductor','surface','setting']

@admin.register(ApBox)
class ApBoxAdmin(admin.ModelAdmin):
    search_fields = ('id','fk_node','fk_trafo','type','owner','status')
    list_display = ('id','fk_node','fk_trafo','type','owner','status')
    list_filter = ['type','owner','status']

class LuminaireSettingResource(resources.ModelResource):
    class Meta:
        model = LuminaireSetting

@admin.register(LuminaireSetting)
class LuminaireSettingAdmin(ImportExportModelAdmin):
    resource_class= LuminaireSettingResource
    search_fields = ('id','name__icontains','fk_tech','power','fk_type')
    list_display = ('id','name','fk_tech','power','fk_type')
    list_filter = ['fk_tech']

class LuminaireResource(resources.ModelResource):
    class Meta:
        model = Luminaire

@admin.register(Luminaire)
class LuminaireAdmin(ImportExportModelAdmin):
    resource_class= LuminaireResource
    search_fields = ('id','code','fk_photocell','fk_opticprotection','fk_setting','fk_lightedspace','fk_armtype','fk_node','fk_trafo','height','status')
    list_display = ('id','code','fk_photocell','fk_opticprotection','fk_setting','fk_lightedspace','fk_armtype','fk_node','fk_trafo','height','financing','status')
    list_filter = ['fk_node__fk_district__fk_comuna', 'fk_lightedspace','fk_opticprotection','fk_photocell','financing','status']
    readonly_fields = ['user_creation', 'user_updated','date_creation','date_updated']

class SupportSettingResource(resources.ModelResource):
    class Meta:
        model = SupportSetting

@admin.register(SupportSetting)
class SupportSettingAdmin(ImportExportModelAdmin):
    resource_class= SupportSettingResource
    search_fields = ('id','name','fk_height','fk_material','fk_supporttype','fk_breaking_capacity')
    list_display = ('id','name','fk_height','fk_material','fk_supporttype','fk_breaking_capacity')
    list_filter = ['fk_supporttype','fk_material']
    readonly_fields = ['user_creation', 'user_updated','date_creation','date_updated']

class SupportResource(resources.ModelResource):
    class Meta:
        model = Support

@admin.register(Support)
class SupportAdmin(ImportExportModelAdmin):
    resource_class= SupportResource
    search_fields = ('id','fk_setting','fk_node','fk_trafo','fk_cimentation','status','owner')
    list_display = ('id','fk_setting','fk_node','fk_trafo','fk_cimentation','status','financing','owner')
    list_filter = ['fk_node__fk_district__fk_comuna','fk_setting','fk_cimentation','owner','financing','status']
    readonly_fields = ['user_creation', 'user_updated','date_creation','date_updated']
