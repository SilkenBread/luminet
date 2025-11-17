# standard library
import re, os
from datetime import datetime

# Django
from django.db import models, transaction
from django.forms.models import model_to_dict
from django.core.validators import RegexValidator

# django-crum
from crum import get_current_user

# django-simple-history
from simple_history.models import HistoricalRecords

# local Django
from apps.models import BaseModel, BaseRoute
from apps.infrastructure.models import Node

from django.contrib.auth.models import Group
from .choices import PQR_STATUS


class Origin(BaseModel):
    name = models.CharField(
        max_length=255,
        unique=False,
        blank=False,
        null=False,
        validators=[
            RegexValidator(
                regex=r'^[A-Za-zá-úüñÁ-ÚÜÑ\s]+$',
                message=('No es un nombre válido'),
                code='invalid_name'
            )
        ],
        verbose_name='Nombre')
    fk_group = models.ManyToManyField(Group, blank=True, verbose_name='Grupos')

    class Meta:
        db_table = 'ORIGIN_PQR'
        verbose_name = 'Origen PQR'
        verbose_name_plural = 'Origenes de PQRs'
        ordering = ['id']
    
    def __str__(self):
        return f"{self.name}"
    
    def save(self, force_insert=False,force_update=False,using=None,update_fields=None):
        user = get_current_user()
        if user is not None:
            setattr(self, 'user_creation' if not self.pk else 'user_updated', user)
        super(Origin, self).save()
    
    def toJSON(self):
        item = model_to_dict(self, exclude=['user_creation', 'user_updated'])
        return item

class GeneralTypeDamage(BaseModel):
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    name = models.CharField(
        max_length=255,
        unique=False,
        blank=False,
        null=False,
        validators=[
            RegexValidator(
                regex=r'^[A-Za-zá-úüñÁ-ÚÜÑ\s]+$',
                message=('No es un nombre válido'),
                code='invalid_name'
            )
        ],
        verbose_name='Nombre')
    
    class Meta:
        db_table = 'TYPE_DAMAGE_GENERAL'
        verbose_name = 'Tipo de daño externo'
        verbose_name_plural = 'Tipos de daños externos'
        ordering = ['id']
    
    def __str__(self):
        return f"{self.id}-{self.name}"
    
    def save(self, force_insert=False,force_update=False,using=None,update_fields=None):
        user = get_current_user()
        if user is not None:
            setattr(self, 'user_creation' if not self.pk else 'user_updated', user)
        super(GeneralTypeDamage, self).save()
    
    def toJSON(self):
        item = model_to_dict(self, exclude=['user_creation', 'user_updated'])
        return item

class CauseRejectPqr(BaseModel):
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    name = models.CharField(
        max_length=255,
        unique=False,
        blank=False,
        null=False,
        validators=[
            RegexValidator(
                regex=r'^[A-Za-zá-úüñÁ-ÚÜÑ\s]+$',
                message=('No es un nombre válido'),
                code='invalid_name'
            )
        ],
        verbose_name='Nombre')
    description = models.TextField(max_length=600, blank=False, null=True, verbose_name='Descripción')
    
    class Meta:
        db_table = 'CAUSE_REJECT_PQR'
        verbose_name = 'Causal para rechazar una PQR'
        verbose_name_plural = 'Causales para rechazar PQRs'
        ordering = ['id']
    
    def __str__(self):
        return f"{self.id}-{self.name}"
    
    def save(self, force_insert=False,force_update=False,using=None,update_fields=None):
        user = get_current_user()
        if user is not None:
            setattr(self, 'user_creation' if not self.pk else 'user_updated', user)
        super(CauseRejectPqr, self).save()
    
    def toJSON(self):
        item = model_to_dict(self, exclude=['user_creation', 'user_updated'])
        return item

class FileNumber(models.Model):
    value = models.PositiveBigIntegerField(blank=True, null=False, unique=True, verbose_name='Número de radicado')

    class Meta:
        db_table = 'FILE_NUMBER'
        verbose_name = 'Número de Radicado'
        verbose_name_plural = 'Números de Radicados'
        ordering = ['-id']

    def __str__(self):
        return f"{self.value}"
    
    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        with transaction.atomic():
            last_middle_year = datetime.now().year % 100

            if not self.value:
                last_instance = FileNumber.objects.order_by('-id').first()

                if last_instance is not None:
                    # Validamos que los dos primeros dígitos del último radicado guardado sean iguales a los dos últimos del año actual
                    if last_middle_year == (int(last_instance.value) // 1000000):
                        self.value = last_instance.value + 1
                    else:
                        FileNumber.objects.all().delete()
                        self.value = (last_middle_year * 1000000) + 1
                else:
                    self.value = (last_middle_year * 1000000) + 1  # Número de radicado para el primer registro
            super(FileNumber, self).save()
    
class PqrBase(models.Model):
    date_creation = models.DateTimeField(auto_now_add=True,null=True,blank=True)
    date_updated = models.DateTimeField(auto_now=True,null=True,blank=True)
    file_number = models.PositiveBigIntegerField(blank=True, null=False, unique=True, verbose_name='Número de radicado', db_index=True)
    status = models.PositiveSmallIntegerField(choices=PQR_STATUS, default=1, verbose_name='Estado', db_index=True)
    fk_type_damage = models.ForeignKey(GeneralTypeDamage, verbose_name='Tipo de daño', null=False, blank=False, on_delete=models.PROTECT)
    fk_node_reported = models.ForeignKey(Node, on_delete=models.PROTECT, null=True, blank=False, verbose_name='Nodo reportado', db_index=True)
    fk_origin = models.ForeignKey(Origin, on_delete=models.PROTECT, null=True, verbose_name='Origen')
    
    name = models.CharField(max_length=255, unique=False, blank=False, null=False,
        validators=[
            RegexValidator(
                regex=r'^[A-Za-zá-úüñÁ-ÚÜÑ\s]+$',
                message=('No es un nombre válido'),
                code='invalid_name'
            )
        ],
        verbose_name='Nombre')
    dni = models.PositiveBigIntegerField(unique=False, blank=True, null=True, validators=[
            RegexValidator(
                regex=r'^\d{7,10}$',
                message=('No es un número de documento válido'),
                code='invalid_dni'
            )
        ],
        verbose_name='Cédula ciudadania')
    phone_number = models.PositiveBigIntegerField(unique=False, blank=False, null=True,
        validators=[
            RegexValidator(
                regex=r'^(3|6)\d{9}$',
                message=('No es un número de teléfono válido'),
                code='invalid_phonenumber'
            )
        ],
        verbose_name='Número teléfono'
    )
    email = models.EmailField(verbose_name='Correo electrónico', null=True, blank=False, unique=False)
    observation = models.TextField(max_length=600, blank=False, null=False, verbose_name='Observaciones')

    class Meta:
        abstract=True

    def __str__(self):
        return f"#{self.file_number}"
    
    def toJSON(self):
        item = model_to_dict(self, exclude=['user_creation', 'user_updated'])
        item['status']= self.get_status_display()
        item['date_creation'] = self.date_creation.strftime('%Y-%m-%d %I:%M %p')
        item['fk_type_damage'] =str(self.fk_type_damage)
        item['fk_origin']=str(self.fk_origin)
        item['str_node_reported']= str(self.fk_node_reported)
        return item

class PqrActive(PqrBase):
    historical = HistoricalRecords()

    class Meta:
        db_table = 'PQR_ACTIVE'
        verbose_name = 'PQR activa'
        verbose_name_plural = 'PQRs activas'
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['file_number']),
            models.Index(fields=['fk_node_reported', 'status']),
        ]
        ordering = ['id']

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        with transaction.atomic():
            self.name = self.name.title()
        super(PqrActive, self).save()
    
    def toJSON(self):
        item = super().toJSON()  # Llamada al método toJSON del modelo base
        route_history = PqrActiveRoute.objects.filter(fk_pqr=self)
        item['route_history'] = [{**route.toJSON(), 'enum': idx + 1} for idx, route in enumerate(route_history)] # Agregar historial de rutas
        return item

class PqrClosed(PqrBase):
    historical = HistoricalRecords()

    class Meta:
        db_table = 'PQR_CLOSED'
        verbose_name = 'PQR cerrada'
        verbose_name_plural = 'PQRs cerradas'
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['file_number']),
            models.Index(fields=['fk_node_reported', 'status']),
        ]
        ordering = ['id']

    def toJSON(self):
        item = super().toJSON()  # Llamada al método toJSON del modelo base
        route_history = PqrClosedRoute.objects.filter(fk_pqr=self)
        item['route_history'] = [{**route.toJSON(), 'enum': idx + 1} for idx, route in enumerate(route_history)] # Agregar historial de rutas
        return item


class PqrRouteBase(BaseRoute):
    state= models.PositiveSmallIntegerField(choices=PQR_STATUS, null=False, blank=False, verbose_name='Estado', db_index=True)
    cause = models.ForeignKey(CauseRejectPqr, on_delete=models.PROTECT, null=True, blank=True, unique=False, verbose_name='Causal')

    class Meta:
        abstract=True

    def toJSON(self):
        item = super().toJSON()  # Llamada al método toJSON del modelo base
        item['state']= self.get_state_display()
        return item

class PqrActiveRoute(PqrRouteBase):
    fk_pqr = models.ForeignKey(PqrActive, null=False, blank=False, on_delete=models.PROTECT, verbose_name='PQR', db_index=True)

    class Meta:
        db_table = 'PQR_ACTIVE_ROUTE'
        verbose_name = 'Ruta PQR activa'
        verbose_name_plural = 'Ruta PQRs activas'
        indexes = [
            models.Index(fields=['fk_pqr']),
            models.Index(fields=['fk_pqr', 'state']),
        ]
        ordering = ['fk_pqr']

    def __str__(self):
        return f"{str(self.fk_pqr)}"

class PqrClosedRoute(PqrRouteBase):
    fk_pqr = models.ForeignKey(PqrClosed, null=False, blank=False, on_delete=models.PROTECT, verbose_name='PQR', db_index=True)

    class Meta:
        db_table = 'PQR_CLOSED_ROUTE'
        verbose_name = 'Ruta PQR cerrada'
        verbose_name_plural = 'Ruta PQRs cerradas'
        indexes = [
            models.Index(fields=['fk_pqr']),
            models.Index(fields=['fk_pqr', 'state']),
        ]
        ordering = ['fk_pqr']

    def __str__(self):
        return f"{str(self.fk_pqr)}"
