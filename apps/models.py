from django.db import models
from config.settings import AUTH_USER_MODEL


class BaseModel(models.Model):
    """
    Base model class that provides common fields for all models.

    Attributes:
        user_creation (ForeignKey): The user who created the model instance.
        date_creation (DateTimeField): The date and time when the model instance was created.
        user_updated (ForeignKey): The user who last updated the model instance.
        date_updated (DateTimeField): The date and time when the model instance was last updated.
    """
    class Meta:
        abstract = True
        
    user_creation = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='%(app_label)s_%(class)s_creation', null=True, blank=True, verbose_name='Usuario Creación')
    date_creation = models.DateTimeField(auto_now_add=True, null=True, blank=True, verbose_name='Fecha Creación')
    user_updated = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='%(app_label)s_%(class)s_updated', null=True, blank=True, verbose_name='Usuario Actualización')
    date_updated = models.DateTimeField(auto_now=True, null=True, blank=True, verbose_name='Fecha Actualización')

