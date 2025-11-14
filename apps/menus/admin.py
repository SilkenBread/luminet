from django.contrib import admin
from django.utils.html import format_html
from .models import MenuItem, MenuGroup, MenuGroupItem

class MenuGroupItemInline(admin.TabularInline):
    """
    Inline para agregar y ordenar items dentro de un grupo de menú.
    """
    model = MenuGroupItem
    extra = 1
    autocomplete_fields = ['menu_item']
    ordering = ('order',)
    fields = ('menu_item', 'order')
    sortable_field_name = 'order'

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'resolved_url', 'parent', 'is_active', 'icon')
    list_filter = ('is_active', 'parent')
    search_fields = ('title', 'url_name')
    autocomplete_fields = ('parent',)
    
    def resolved_url(self, obj):
        try:
            return format_html('<a href="{}">{}</a>', obj.resolved_url(), obj.url_name)
        except Exception:
            return obj.url_name
    resolved_url.short_description = 'URL'

@admin.register(MenuGroup)
class MenuGroupAdmin(admin.ModelAdmin):
    list_display = ('title',)
    search_fields = ('title',)
    filter_horizontal = ('allowed_groups',)
    inlines = [MenuGroupItemInline]

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('allowed_groups')
