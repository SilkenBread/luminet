from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from simple_history.admin import SimpleHistoryAdmin
from apps.users.models import User, Area, Crew, Zone


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'description', 'is_active', 'date_creation', 'date_updated']
    list_filter = ['is_active', 'date_creation']
    search_fields = ['name', 'description']
    readonly_fields = ['date_creation', 'date_updated', 'user_creation', 'user_updated']
    ordering = ['name']
    
    fieldsets = (
        ('Información General', {
            'fields': ('name', 'description', 'is_active')
        }),
        ('Auditoría', {
            'fields': ('date_creation', 'date_updated', 'user_creation', 'user_updated'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Crew)
class CrewAdmin(SimpleHistoryAdmin):
    list_display = ['id', 'name', 'fk_area', 'is_active', 'date_creation']
    list_filter = ['is_active', 'fk_area', 'date_creation']
    search_fields = ['name', 'fk_area__name']
    readonly_fields = ['date_creation', 'date_updated', 'user_creation', 'user_updated']
    ordering = ['name']
    
    fieldsets = (
        ('Información General', {
            'fields': ('name', 'fk_area', 'is_active')
        }),
        ('Auditoría', {
            'fields': ('date_creation', 'date_updated', 'user_creation', 'user_updated'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'fk_area', 'color_preview', 'date_creation']
    list_filter = ['fk_area', 'date_creation']
    search_fields = ['name', 'fk_area__name']
    readonly_fields = ['date_creation', 'date_updated', 'user_creation', 'user_updated']
    ordering = ['name']
    
    fieldsets = (
        ('Información General', {
            'fields': ('name', 'fk_area', 'color')
        }),
        ('Auditoría', {
            'fields': ('date_creation', 'date_updated', 'user_creation', 'user_updated'),
            'classes': ('collapse',)
        }),
    )
    
    def color_preview(self, obj):
        """Muestra una previsualización del color"""
        return format_html(
            '<div style="width: 30px; height: 30px; background-color: {}; border: 1px solid #ccc; border-radius: 4px;"></div>',
            obj.color
        )
    color_preview.short_description = 'Color'


@admin.register(User)
class UserAdmin(SimpleHistoryAdmin, BaseUserAdmin):
    list_display = ['username', 'gradient_display', 'full_name_display', 'email', 'dni', 'fk_area', 'is_active', 'is_staff']
    list_filter = ['is_active', 'is_staff', 'is_superuser', 'fk_area', 'fk_crew', 'groups']
    search_fields = ['username', 'first_name', 'last_name', 'email', 'dni']
    readonly_fields = ['date_joined', 'last_login', 'date_creation', 'date_updated', 'user_creation', 'user_updated', 'gradient_display']
    ordering = ['username']
    
    fieldsets = (
        ('Credenciales', {
            'fields': ('username', 'password')
        }),
        ('Información Personal', {
            'fields': ('first_name', 'last_name', 'email', 'dni', 'phone_number', 'gradient_display')
        }),
        ('Organización', {
            'fields': ('fk_area', 'fk_crew')
        }),
        ('Permisos', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        ('Fechas Importantes', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
        ('Auditoría', {
            'fields': ('date_creation', 'date_updated', 'user_creation', 'user_updated'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        ('Credenciales', {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
        ('Información Personal', {
            'classes': ('wide',),
            'fields': ('first_name', 'last_name', 'email', 'dni', 'phone_number'),
        }),
        ('Organización', {
            'classes': ('wide',),
            'fields': ('fk_area', 'fk_crew'),
        }),
        ('Permisos', {
            'classes': ('wide',),
            'fields': ('is_active', 'is_staff', 'is_superuser'),
        }),
    )
    
    def gradient_display(self, obj):
        """Muestra el gradiente único del usuario"""
        gradient = obj.get_gradient_colors()
        return format_html(
            '<div style="display: flex; align-items: center; gap: 10px;">'
            '<div style="width: 40px; height: 40px; border-radius: 50%; '
            'background: linear-gradient(135deg, {} 0%, {} 100%); '
            'display: flex; align-items: center; justify-content: center; '
            'color: white; font-weight: bold; font-size: 14px; '
            'box-shadow: 0 2px 4px rgba(0,0,0,0.1);">{}</div>'
            '<span style="color: #666; font-size: 12px;">{} → {}</span>'
            '</div>',
            gradient['from_hex'],
            gradient['to_hex'],
            obj.first_name[0].upper() + obj.last_name[0].upper() if obj.first_name and obj.last_name else obj.username[0].upper(),
            gradient['from'],
            gradient['to']
        )
    gradient_display.short_description = 'Gradiente de Usuario'
    
    def full_name_display(self, obj):
        """Muestra el nombre completo del usuario"""
        return obj.get_full_name() or '-'
    full_name_display.short_description = 'Nombre Completo'
