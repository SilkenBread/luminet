from django.db import models
from django.contrib.auth.models import Group
from django.urls import reverse

class MenuItem(models.Model):
    """
    Un elemento individual del menú que puede ser parte de múltiples grupos.
    """
    title = models.CharField(max_length=100, verbose_name="Título")
    url_name = models.CharField(
        max_length=100,
        verbose_name="Nombre de URL",
        help_text="Nombre del patrón de URL de Django (ej: 'infrastructure:list')"
    )
    icon = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Clase o nombre del icono (ej: 'layout-dashboard' para Lucide)"
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name="Menú Padre"
    )
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    order = models.PositiveIntegerField(default=0, verbose_name="Orden")

    url_kwargs = models.JSONField(blank=True, null=True, default=dict, help_text="Parámetros para reverse()")

    class Meta:
        verbose_name = "Item de Menú"
        verbose_name_plural = "Items de Menú"
        ordering = ['order', 'title']

    def __str__(self):
        return self.title

    def resolved_url(self):
        """Devuelve la URL resuelta usando reverse() y pasando kwargs si existen"""
        try:
            if self.url_kwargs:
                return reverse(self.url_name, kwargs=self.url_kwargs)
            return reverse(self.url_name)
        except Exception:
            return '#'  # URL inválida

    def has_access(self, user):
        """Verifica si el usuario tiene acceso al item"""
        if user.is_authenticated:
            if user.is_superuser:
                return True
            # Verificar si el usuario pertenece a algún grupo permitido
            # Nota: Este método se mantiene para compatibilidad con el código existente
            # En la nueva estructura, los grupos se manejan a través de MenuGroup
            return user.groups.filter(pk__in=self.groups.values_list('pk', flat=True)).exists()
        return False

class MenuGroup(models.Model):
    """
    Un grupo lógico de menú que puede estar asociado a múltiples grupos de usuarios.
    """
    title = models.CharField(max_length=120, unique=True, verbose_name="Título")
    allowed_groups = models.ManyToManyField(
        Group,
        related_name='menu_groups',
        blank=True,
        verbose_name="Grupos permitidos",
        help_text="Si no se selecciona ningún grupo, el menú será público"
    )
    items = models.ManyToManyField(
        MenuItem,
        through='MenuGroupItem',
        related_name='menu_groups',
        verbose_name="Items del menú"
    )

    class Meta:
        verbose_name = "Grupo de Menú"
        verbose_name_plural = "Grupos de Menú"

    def __str__(self):
        return self.title

class MenuGroupItem(models.Model):
    """
    Modelo intermedio para almacenar el orden de los items dentro de un grupo.
    """
    menu_group = models.ForeignKey(MenuGroup, on_delete=models.CASCADE)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = (('menu_group', 'menu_item'),)
        ordering = ['order']

    def __str__(self):
        return f"{self.menu_group}: {self.menu_item} ({self.order})"
    
        