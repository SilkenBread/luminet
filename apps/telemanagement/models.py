from django.db import models
from crum import get_current_user
from apps.models import BaseModel


class SmartPhotocell(BaseModel):
    devui = models.CharField(max_length=16, verbose_name='DevEUI', unique=True)
    is_active = models.BooleanField(default=True, verbose_name='Activo')

    class Meta:
        db_table = 'SMART_PHOTOCELL'
        verbose_name = 'Fotocelda Inteligente'
        verbose_name_plural = 'Fotoceldas Inteligentes'
        ordering = ['id']

    def __str__(self):
        return self.devui

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        user = get_current_user()
        if user is not None:
            setattr(self, 'user_creation' if not self.pk else 'user_updated', user)
        super(SmartPhotocell, self).save(force_insert, force_update, using, update_fields)
