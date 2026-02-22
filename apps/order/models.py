# standard library
import base64

# Django
from django.db import models
from django.forms.models import model_to_dict
from django.core.validators import RegexValidator
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile

# django-crum
from crum import get_current_user

# django-simple-history
from simple_history.models import HistoricalRecords

# local Django
from apps.models import BaseModel, BaseRoute
from config.settings import AUTH_USER_MODEL, MEDIA_URL, STATIC_URL
from .choices import OT_STATUS
from apps.users.models import Area, Crew, User


class Priority(BaseModel):
    name = models.CharField(
        max_length=255,
        unique=False,
        blank=False,
        null=False,
        validators=[
            RegexValidator(
                regex=r'^[A-Za-zá-úüñÁ-ÚÜÑ\s]+$',
                message='No es un nombre válido',
                code='invalid_name'
            )
        ],
        verbose_name='Nombre')

    class Meta:
        db_table = 'PRIORITY'
        verbose_name = 'Prioridad'
        verbose_name_plural = 'Prioridades'
        ordering = ['id']

    def __str__(self):
        return f"{self.name}"

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        user = get_current_user()
        if user is not None:
            setattr(self, 'user_creation' if not self.pk else 'user_updated', user)
        super(Priority, self).save()

    def toJSON(self):
        item = model_to_dict(self, exclude=['user_creation', 'user_updated'])
        return item


class InternalTypeDamage(BaseModel):
    name = models.CharField(max_length=255, unique=False, blank=False, null=False, verbose_name='Nombre')
    fk_priority = models.ForeignKey(Priority, on_delete=models.PROTECT, verbose_name='Prioridad')
    fk_general_damage = models.ForeignKey('pqrs.GeneralTypeDamage', on_delete=models.PROTECT, null=True, verbose_name='Tipo de daño general')

    class Meta:
        db_table = 'TYPE_DAMAGE_INTERNAL'
        verbose_name = 'Tipo de daño interno'
        verbose_name_plural = 'Tipos de daños internos'
        ordering = ['id']

    def __str__(self):
        return f"{self.name}"

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        user = get_current_user()
        if user is not None:
            setattr(self, 'user_creation' if not self.pk else 'user_updated', user)
        super(InternalTypeDamage, self).save()

    def toJSON(self):
        item = model_to_dict(self, exclude=['user_creation', 'user_updated'])
        return item


class Activities(BaseModel):
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    name = models.CharField(max_length=255, unique=True, blank=False, null=False, verbose_name='Nombre')
    code = models.PositiveIntegerField(unique=True, null=True, blank=False, verbose_name='Codigo')

    class Meta:
        db_table = 'ACTIVITIES'
        verbose_name = 'Actividad Terreno'
        verbose_name_plural = 'Actividades de Terreno'
        ordering = ['id']

    def __str__(self):
        return f"{self.code} {self.name}"

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        user = get_current_user()
        if user is not None:
            setattr(self, 'user_creation' if not self.pk else 'user_updated', user)
        super(Activities, self).save()

    def toJSON(self):
        item = model_to_dict(self, exclude=['user_creation', 'user_updated'])
        return item


class TimingRepair(BaseModel):
    name = models.CharField(
        max_length=255,
        unique=False,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex=r'^[A-Za-zá-úüñÁ-ÚÜÑ\s]+$',
                message='No es un nombre válido',
                code='invalid_name'
            )
        ],
        verbose_name='Nombre')
    timing_reparation = models.DurationField(verbose_name='Duracion')

    class Meta:
        db_table = 'TIMING_REPAIR'
        verbose_name = 'Tiempo Reparación'
        verbose_name_plural = 'Tiempos de Reparación'
        ordering = ['id']

    def __str__(self):
        return f"{self.name}"

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        user = get_current_user()
        if user is not None:
            setattr(self, 'user_creation' if not self.pk else 'user_updated', user)
        duration_hours = int(self.timing_reparation.total_seconds() / 3600)
        self.name = f"{duration_hours} HORAS"
        super(TimingRepair, self).save()

    def toJSON(self):
        item = model_to_dict(self, exclude=['user_creation', 'user_updated'])
        return item


class CauseRejectOrder(BaseModel):
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    name = models.CharField(
        max_length=255,
        unique=True,
        blank=False,
        null=False,
        validators=[
            RegexValidator(
                regex=r'^[A-Za-zá-úüñÁ-ÚÜÑ\s]+$',
                message='No es un nombre válido',
                code='invalid_name'
            )
        ],
        verbose_name='Nombre')

    class Meta:
        db_table = 'CAUSE_REJECT_ORDER'
        verbose_name = 'Causal para rechazar una orden'
        verbose_name_plural = 'Causales para rechazar ordenes'
        ordering = ['id']

    def __str__(self):
        return f"{self.id}-{self.name}"

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        user = get_current_user()
        if user is not None:
            setattr(self, 'user_creation' if not self.pk else 'user_updated', user)
        super(CauseRejectOrder, self).save()

    def toJSON(self):
        item = model_to_dict(self, exclude=['user_creation', 'user_updated'])
        return item


class TypeOrder(BaseModel):
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    name = models.CharField(
        max_length=255,
        unique=False,
        blank=False,
        null=False,
        validators=[
            RegexValidator(
                regex=r'^[A-Za-zá-úüñÁ-ÚÜÑ\s]+$',
                message='No es un nombre válido',
                code='invalid_name'
            )
        ],
        verbose_name='Nombre')

    class Meta:
        db_table = 'TYPE_ORDER'
        verbose_name = 'Tipo de orden'
        verbose_name_plural = 'Tipos de orden'
        ordering = ['id']

    def __str__(self):
        return f"{self.name}"

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        user = get_current_user()
        if user is not None:
            setattr(self, 'user_creation' if not self.pk else 'user_updated', user)
        super(TypeOrder, self).save()

    def toJSON(self):
        item = model_to_dict(self, exclude=['user_creation', 'user_updated'])
        return item


class OrderBase(BaseModel):
    fk_type_order = models.ForeignKey(TypeOrder, on_delete=models.PROTECT, null=True, blank=False, verbose_name='Tipo de orden')
    status = models.PositiveSmallIntegerField(choices=OT_STATUS, default=1, verbose_name='Estado')
    fk_internal_type_damage = models.ForeignKey(InternalTypeDamage, on_delete=models.PROTECT, null=True, blank=False, verbose_name='Tipo de daño interno')
    internal_observation = models.TextField(max_length=600, blank=False, null=True, verbose_name='Observaciones Internas')
    site_observation = models.TextField(max_length=600, blank=True, null=True, verbose_name='Observaciones en Terreno')
    fk_priority = models.ForeignKey(Priority, on_delete=models.PROTECT, null=False, blank=False, verbose_name='Prioridad asignada')

    fk_area = models.ForeignKey(Area, on_delete=models.PROTECT, blank=False, null=True, verbose_name='Área')
    fk_crew = models.ForeignKey(Crew, on_delete=models.PROTECT, null=True, blank=True, verbose_name='Cuadrilla')

    activities = models.ManyToManyField(Activities, blank=True, verbose_name='Actividades realizadas')
    fk_timingrepair = models.ForeignKey(TimingRepair, on_delete=models.PROTECT, null=True, blank=False, verbose_name='Tiempo de reparación')
    date_limit = models.DateTimeField(null=True, blank=True, verbose_name='Fecha limite')

    assigned_by = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True, related_name='assigned_by_%(class)s', verbose_name='Asignado por')
    closed_by = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True, related_name='closed_by_%(class)s', verbose_name='Cerrado por')

    image1 = models.ImageField(upload_to='ot_images/%Y/%m/%d', blank=True, null=True, verbose_name='Imagen 1')
    image2 = models.ImageField(upload_to='ot_images/%Y/%m/%d', blank=True, null=True, verbose_name='Imagen 2')

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.id} - PQR:{str(self.fk_pqr)}"

    @staticmethod
    def base64_to_file(base64_string, order_pk, prefix):
        try:
            image_data = base64.b64decode(base64_string)
            ext = '.jpg'
            file_name = f"OT{order_pk}-{prefix}{ext}"
            in_memory_uploaded_file = InMemoryUploadedFile(
                ContentFile(image_data), None, file_name, 'image/jpeg', len(image_data), None
            )
            in_memory_uploaded_file.seek(0)
            return in_memory_uploaded_file
        except Exception as e:
            raise ValueError(f"Error al guardar la imagen: {str(e)}")

    def get_image1(self):
        if self.image1:
            return '{}{}'.format(MEDIA_URL, self.image1)

    def get_image2(self):
        if self.image2:
            return '{}{}'.format(MEDIA_URL, self.image2)

    def toJSON(self):
        item = model_to_dict(self, exclude=['user_creation', 'user_updated'])
        item['fk_priority'] = str(self.fk_priority)
        item['fk_type_order'] = str(self.fk_type_order)
        item['fk_internal_type_damage'] = str(self.fk_internal_type_damage)
        item['fk_area'] = str(self.fk_area)
        item['fk_crew'] = str(self.fk_crew)
        item['status'] = self.get_status_display()
        item['date_creation'] = self.date_creation.strftime('%Y-%m-%d %H:%M:%S')
        item['date_limit'] = self.date_limit.strftime('%Y-%m-%d %H:%M:%S') if self.date_limit else ''
        item['activities'] = list(self.activities.values_list('name', flat=True)) if self.activities else None
        item['assigned_by'] = self.assigned_by.get_full_name() if self.assigned_by else None
        item['closed_by'] = self.closed_by.get_full_name() if self.closed_by else None
        item['image1'] = str(self.get_image1()) if self.image1 else '{}{}'.format(STATIC_URL, 'img/empty_picture.jpg')
        item['image2'] = str(self.get_image2()) if self.image2 else '{}{}'.format(STATIC_URL, 'img/empty_picture.jpg')
        return item


class OrderActive(OrderBase):
    fk_pqr = models.ForeignKey('pqrs.PqrActive', on_delete=models.PROTECT, null=False, blank=False, verbose_name='PQR de la orden', db_index=True)
    historical = HistoricalRecords()

    class Meta:
        db_table = 'ORDER_ACTIVE'
        verbose_name = 'Orden de trabajo activa'
        verbose_name_plural = 'Ordenes de trabajo activas'
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['fk_pqr']),
        ]
        ordering = ['id']

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super(OrderActive, self).save()

    def toJSON(self):
        item = super().toJSON()
        route_history = OrderActiveRoute.objects.filter(fk_ot=self)
        item['route_history'] = [{**route.toJSON(), 'enum': idx + 1} for idx, route in enumerate(route_history)]
        return item


class OrderClosed(OrderBase):
    fk_pqr = models.ForeignKey('pqrs.PqrClosed', on_delete=models.PROTECT, null=True, blank=False, verbose_name='PQR de la orden', db_index=True)
    historical = HistoricalRecords()

    class Meta:
        db_table = 'ORDER_CLOSED'
        verbose_name = 'Orden de trabajo cerrada'
        verbose_name_plural = 'Ordenes de trabajo cerradas'
        indexes = [
            models.Index(fields=['fk_pqr']),
        ]
        ordering = ['id']

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        user = get_current_user()
        if user is not None:
            setattr(self, 'user_creation' if not self.pk else 'user_updated', user)
        super(OrderClosed, self).save()

    def toJSON(self):
        item = super().toJSON()
        item['fk_pqr'] = self.fk_pqr.toJSON() if self.fk_pqr else None
        route_history = OrderClosedRoute.objects.filter(fk_ot=self)
        item['route_history'] = [{**route.toJSON(), 'enum': idx + 1} for idx, route in enumerate(route_history)]
        return item


class OrderRouteBase(BaseRoute):
    user_creation = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='%(app_label)s_%(class)s_creation', null=True, blank=True)
    state = models.PositiveSmallIntegerField(choices=OT_STATUS, null=False, blank=False, verbose_name='Estado', db_index=True)
    cause = models.ForeignKey(CauseRejectOrder, on_delete=models.PROTECT, null=True, blank=True, unique=False, verbose_name='Causal')

    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=['state']),
        ]

    def __str__(self):
        return f"{self.id}-{self.get_state_display()} {self.cause}"

    def toJSON(self):
        item = super().toJSON()
        item['user_creation'] = self.user_creation.get_full_name() if self.user_creation else ''
        item['state'] = self.get_state_display()
        item['cause'] = str(self.cause) if self.cause else ''
        return item


class OrderActiveRoute(OrderRouteBase):
    fk_ot = models.ForeignKey(OrderActive, null=False, blank=False, on_delete=models.PROTECT, verbose_name='Orden de trabajo', db_index=True)

    class Meta:
        db_table = 'ORDER_ACTIVE_ROUTE'
        verbose_name = 'Ruta Orden de trabajo activa'
        verbose_name_plural = 'Ruta Ordenes de trabajo activas'
        indexes = [
            models.Index(fields=['fk_ot']),
        ]
        ordering = ['fk_ot']


class OrderClosedRoute(OrderRouteBase):
    fk_ot = models.ForeignKey(OrderClosed, null=False, blank=False, on_delete=models.PROTECT, verbose_name='Orden de trabajo', db_index=True)

    class Meta:
        db_table = 'ORDER_CLOSED_ROUTE'
        verbose_name = 'Ruta Orden de trabajo cerrada'
        verbose_name_plural = 'Ruta Ordenes de trabajo cerradas'
        indexes = [
            models.Index(fields=['fk_ot']),
        ]
        ordering = ['fk_ot']
