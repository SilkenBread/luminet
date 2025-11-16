# standard library
import json, re

# Django
from django.db import models, transaction
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.contrib.gis.db import models
from django.core.validators import RegexValidator
from django.forms import model_to_dict

# django-crum
from crum import get_current_user

# django-simple-history
from simple_history.models import HistoricalRecords

# local Django
from apps.infrastructure.choices import *
from apps.models import BaseModel
# from apps.telemanagement.models import SmartPhotocell


"""
    Modelos auxiliares para opciones de seleccion multiple que puedan crecer a lo largo del tiempo
"""


class Inventory(BaseModel):
    code = models.CharField(max_length=3, unique=True, verbose_name="Código")
    name = models.CharField(
        max_length=64, unique=True, verbose_name="Nombre", blank=False, null=False
    )

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.code}-{self.name}"


""" Luminarias"""


class LuminaireTech(Inventory):
    class Meta:
        db_table = "LUMINAIRE_TECH"
        verbose_name = "Tecnología Luminaria"
        verbose_name_plural = "Tecnología de Luminarias"
        ordering = ["id"]

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        user = get_current_user()
        if user is not None:
            setattr(self, "user_creation" if not self.pk else "user_updated", user)
        super(LuminaireTech, self).save()


class ArmType(Inventory):
    class Meta:
        db_table = "ARM_TYPE"
        verbose_name = "Tipo de brazo"
        verbose_name_plural = "Tipos de brazos"
        ordering = ["id"]

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        user = get_current_user()
        if user is not None:
            setattr(self, "user_creation" if not self.pk else "user_updated", user)
        super(ArmType, self).save()


class OpticProtection(Inventory):
    class Meta:
        db_table = "OPTIC_PROTECTION"
        verbose_name = "Protección óptica"
        verbose_name_plural = "Protecciones ópticas"
        ordering = ["id"]

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        user = get_current_user()
        if user is not None:
            setattr(self, "user_creation" if not self.pk else "user_updated", user)
        super(OpticProtection, self).save()


class LuminaireType(Inventory):
    class Meta:
        db_table = "LUMINAIRE_TYPE"
        verbose_name = "Tipo Luminaria"
        verbose_name_plural = "Tipos de Luminarias"
        ordering = ["id"]

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        user = get_current_user()
        if user is not None:
            setattr(self, "user_creation" if not self.pk else "user_updated", user)
        super(LuminaireType, self).save()


class PhotoCellType(Inventory):
    class Meta:
        db_table = "PHOTOCELL_TYPE"
        verbose_name = "Tipo control de encendido"
        verbose_name_plural = "Tipos de control de encendido"
        ordering = ["id"]

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        user = get_current_user()
        if user is not None:
            setattr(self, "user_creation" if not self.pk else "user_updated", user)
        super(PhotoCellType, self).save()


class LightedSpace(Inventory):
    class Meta:
        db_table = "LIGHTED_SPACE"
        verbose_name = "Espacio Iluminado"
        verbose_name_plural = "Espacios Iluminados"
        ordering = ["id"]

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        user = get_current_user()
        if user is not None:
            setattr(self, "user_creation" if not self.pk else "user_updated", user)
        super(LightedSpace, self).save()


class LuminaireSupport(Inventory):
    class Meta:
        db_table = "LUMINAIRE_SUPPORT"
        verbose_name = "Soporte luminaria"
        verbose_name_plural = "Soportes de luminarias"
        ordering = ["id"]

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        user = get_current_user()
        if user is not None:
            setattr(self, "user_creation" if not self.pk else "user_updated", user)
        super(LuminaireSupport, self).save()


""" Apoyos"""


class Material(Inventory):
    class Meta:
        db_table = "MATERIAL"
        verbose_name = "Material"
        verbose_name_plural = "Materiales"
        ordering = ["id"]

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        user = get_current_user()
        if user is not None:
            setattr(self, "user_creation" if not self.pk else "user_updated", user)
        super(Material, self).save()


class SupportType(Inventory):
    class Meta:
        db_table = "SUPPORT_TYPE"
        verbose_name = "Tipo poste"
        verbose_name_plural = "Tipos de postes"
        ordering = ["id"]

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        user = get_current_user()
        if user is not None:
            setattr(self, "user_creation" if not self.pk else "user_updated", user)
        super(SupportType, self).save()


class SupportCimentation(Inventory):
    class Meta:
        db_table = "SUPPORT_CIMENTATION"
        verbose_name = "Tipo cimentación"
        verbose_name_plural = "Tipos de cimentaciones"
        ordering = ["id"]

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        user = get_current_user()
        if user is not None:
            setattr(self, "user_creation" if not self.pk else "user_updated", user)
        super(SupportCimentation, self).save()


class NetCaliber(Inventory):
    class Meta:
        db_table = "NET_CALIBER"
        verbose_name = "Calibre de Red"
        verbose_name_plural = "Calibres de Redes"
        ordering = ["id"]

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        user = get_current_user()
        if user is not None:
            setattr(self, "user_creation" if not self.pk else "user_updated", user)
        super(NetCaliber, self).save()


class TrafoPower(BaseModel):
    power = models.DecimalField(
        max_digits=10,
        unique=True,
        null=True,
        decimal_places=2,
        verbose_name="Potencia (W)",
    )

    class Meta:
        db_table = "TRAFO_POWER"
        verbose_name = "Potencia transformador"
        verbose_name_plural = "Potencias de transformadores"
        ordering = ["id"]

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        user = get_current_user()
        if user is not None:
            setattr(self, "user_creation" if not self.pk else "user_updated", user)
        super(TrafoPower, self).save()


class SupportHeight(BaseModel):
    value = models.DecimalField(
        max_digits=10,
        unique=True,
        null=True,
        decimal_places=2,
        verbose_name="Altura (m)",
    )

    class Meta:
        db_table = "SUPPORT_HEIGHT"
        verbose_name = "Altura poste"
        verbose_name_plural = "Alturas de postes"
        ordering = ["id"]

    def __str__(self):
        return f"{self.value}"

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        user = get_current_user()
        if user is not None:
            setattr(self, "user_creation" if not self.pk else "user_updated", user)
        super(SupportHeight, self).save()


class BreakingCapacity(BaseModel):
    value = models.PositiveIntegerField(
        unique=True, null=True, verbose_name="Capacidad ruptura"
    )

    class Meta:
        db_table = "BREAKING_CAPACITY"
        verbose_name = "Capacidad de ruptura"
        verbose_name_plural = "Capacidades de ruptura"
        ordering = ["id"]

    def __str__(self):
        return f"{self.value}"

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        user = get_current_user()
        if user is not None:
            setattr(self, "user_creation" if not self.pk else "user_updated", user)
        super(BreakingCapacity, self).save()


""" MODELOS PARA UBICACION """


class Comuna(BaseModel):
    name = models.CharField(
        max_length=255, unique=True, blank=False, null=False, verbose_name="Nombre"
    )
    type = models.PositiveSmallIntegerField(
        default=1, choices=TYPE_AREA, verbose_name="Tipo zona"
    )
    centerPoint = models.PointField(
        "Punto central", null=True, blank=True, spatial_index=False
    )
    poly = models.PolygonField("Área Comuna", null=True, blank=True, spatial_index=True)

    class Meta:
        db_table = "COMUNA"
        verbose_name = "Comuna"
        verbose_name_plural = "Comunas"
        ordering = ["id"]

    def __str__(self):
        return f"{self.name}"

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        user = get_current_user()
        if user is not None:
            setattr(self, "user_creation" if not self.pk else "user_updated", user)
        super(Comuna, self).save()


class District(BaseModel):
    name = models.CharField(
        max_length=255, blank=False, null=False, verbose_name="Nombre"
    )
    estrato = models.CharField(max_length=2, default="NR", verbose_name="Estrato")
    cod_unico = models.CharField(
        verbose_name="Código único",
        unique=True,
        null=True,
        blank=True,
        max_length=4,
        validators=[
            RegexValidator(
                regex=r"^[0-9]{4}",
                message=("No cumple con el estandar Ej 0101"),
                code="invalid_name_device",
            ),
        ],
    )
    poly = models.MultiPolygonField(
        "Área Barrio", null=True, blank=True, spatial_index=True
    )
    fk_comuna = models.ForeignKey(
        Comuna, on_delete=models.PROTECT, blank=False, null=False, verbose_name="Comuna"
    )

    class Meta:
        db_table = "DISTRICT"
        verbose_name = "Barrio"
        verbose_name_plural = "Barrios"
        indexes = [
            models.Index(fields=["fk_comuna"]),
        ]
        ordering = ["id"]

    def __str__(self):
        return f"{self.name}-{self.fk_comuna}"

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        user = get_current_user()
        if user is not None:
            setattr(self, "user_creation" if not self.pk else "user_updated", user)
        super(District, self).save()


class Node(BaseModel):
    painting_code = models.PositiveIntegerField(
        unique=False,
        blank=True,
        null=False,
        default=0,
        validators=[
            RegexValidator(
                regex=r"^\d{7}$",
                message=("No cumple con la nemotecnia del código de pintado"),
                code="invalid_painting_code",
            ),
        ],
        verbose_name="Código pintado",
        db_index=True,
    )
    location = models.PointField(srid=4326, spatial_index=True)
    fk_district = models.ForeignKey(
        District,
        on_delete=models.PROTECT,
        blank=False,
        null=True,
        verbose_name="Barrio",
        db_index=True,
    )
    observation = models.TextField(
        max_length=300, blank=True, null=True, verbose_name="Observaciones"
    )
    is_duplicated = models.BooleanField(
        default=False, null=True, verbose_name="Duplicado"
    )
    address = models.CharField(
        max_length=300,
        unique=False,
        blank=True,
        null=True,
        verbose_name="Direccion Normalizada",
    )
    historical = HistoricalRecords()

    class Meta:
        db_table = "NODE"
        verbose_name = "Nodo"
        verbose_name_plural = "Nodos"
        indexes = [
            models.Index(fields=["painting_code", "fk_district"]),
        ]
        ordering = ["id"]

    def __str__(self):
        return f"{self.painting_code} ID:{self.id}"

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        user = get_current_user()
        if user is not None:
            setattr(self, "user_creation" if not self.pk else "user_updated", user)

        # Si existe una ubicacion se busca el barrio al que pertenece
        if self.location:
            district = District.objects.filter(poly__contains=self.location).first()
            self.fk_district = district if district else None
        super(Node, self).save()

    def toJSON(self):
        item = model_to_dict(
            self, exclude=["location", "user_creation", "user_updated"]
        )
        item["fk_district"] = self.fk_district.name if self.fk_district else None
        item["comuna"] = self.fk_district.fk_comuna.name if self.fk_district else None
        item["lng"] = self.location.x
        item["lat"] = self.location.y
        return item


""" MODELO MODELOS Y MARCAS """


class Brand(BaseModel):
    name = models.CharField(
        max_length=255,
        unique=True,
        blank=False,
        null=False,
        verbose_name="Nombre marca",
    )

    class Meta:
        db_table = "BRAND"
        verbose_name = "Marca"
        verbose_name_plural = "Marcas"
        ordering = ["id"]

    def __str__(self):
        return self.name

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        user = get_current_user()
        if user is not None:
            setattr(self, "user_creation" if not self.pk else "user_updated", user)
        super(Brand, self).save()

    def toJSON(self):
        item = model_to_dict(self, exclude=["user_creation", "user_updated"])
        return item


""" MODELO TRANSFORMADOR """


class Trafo(BaseModel):
    code = models.CharField(max_length=16, unique=True, verbose_name="Código")
    owner = models.PositiveSmallIntegerField(
        choices=TRAFO_PROPERTY, verbose_name="Propiedad"
    )
    type = models.PositiveSmallIntegerField(
        choices=TRAFO_TYPE, verbose_name="Tipo trafo"
    )
    installationtype = models.CharField(
        max_length=64, choices=TRAFO_INSTALLATION, verbose_name="Tipo instalación"
    )
    using = models.PositiveSmallIntegerField(choices=USING, verbose_name="Uso")
    power = models.ForeignKey(
        TrafoPower,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="Potencia",
    )
    fk_node = models.ForeignKey(
        Node, on_delete=models.PROTECT, blank=True, null=True, verbose_name="Nodo"
    )
    status = models.PositiveSmallIntegerField(
        choices=STATUS, default=2, verbose_name="Estado"
    )
    historical = HistoricalRecords()

    class Meta:
        db_table = "TRAFO"
        verbose_name = "Transformador"
        verbose_name_plural = "Transformadores"
        ordering = ["id"]

    def __str__(self):
        return f"{self.code}-{self.installationtype}"

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        user = get_current_user()
        if user is not None:
            setattr(self, "user_creation" if not self.pk else "user_updated", user)
        super(Trafo, self).save()

    def toJSON(self):
        item = model_to_dict(self, exclude=["user_creation", "user_updated"])
        item["owner"] = self.get_owner_display()
        item["type"] = self.get_type_display()
        item["installationtype"] = self.get_installationtype_display()
        item["using"] = self.get_using_display()
        item["power"] = str(self.power)
        item["status"] = self.get_status_display()
        return item


""" MODELO MEDIDOR """


class Meter(BaseModel):
    fk_trafo = models.ForeignKey(
        Trafo,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        verbose_name="Transformador",
    )
    inbox = models.BooleanField(null=True, blank=True, verbose_name="En caja")
    connection = models.BooleanField(null=True, blank=True, verbose_name="Conectado")
    status = models.PositiveSmallIntegerField(
        choices=STATUS, default=2, verbose_name="Estado"
    )
    historical = HistoricalRecords()

    class Meta:
        db_table = "METER"
        verbose_name = "Medidor"
        verbose_name_plural = "Medidores"
        ordering = ["id"]

    def __str__(self):
        return f"Medidor-{self.fk_trafo}"

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        user = get_current_user()
        if user is not None:
            setattr(self, "user_creation" if not self.pk else "user_updated", user)
        super(Meter, self).save()

    def toJSON(self):
        item = model_to_dict(self, exclude=["user_creation", "user_updated"])
        item["fk_trafo"] = str(self.fk_trafo)
        item["status"] = self.get_status_display()
        return item


""" MODELO DE RED """


class Net(BaseModel):
    fk_trafo = models.ForeignKey(
        Trafo,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        verbose_name="Transformador",
    )
    typeinstallation = models.PositiveSmallIntegerField(
        choices=NET_INSTALLATION, verbose_name="Tipo de instalación"
    )
    conductor = models.PositiveSmallIntegerField(
        choices=NET_CONDUCTOR, verbose_name="Tipo de conducto"
    )
    fk_material = models.ForeignKey(
        Material, on_delete=models.PROTECT, verbose_name="Material"
    )
    caliber = models.ForeignKey(
        NetCaliber,
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        verbose_name="Calibre AWG",
    )
    length = models.PositiveIntegerField(
        unique=False, blank=True, null=True, verbose_name="Longitud tramo (m)"
    )
    setting = models.PositiveSmallIntegerField(
        choices=NET_SETTING, verbose_name="Configuracion"
    )
    surface = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        choices=NET_SURFACE,
        verbose_name="Material de superficie",
    )

    last_node = models.ForeignKey(
        Node,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="net_last_node",
        verbose_name="Nodo anterior",
    )
    current_node = models.ForeignKey(
        Node,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="net_current_node",
        verbose_name="Nodo actual",
    )
    status = models.PositiveSmallIntegerField(
        choices=STATUS, default=2, verbose_name="Estado"
    )
    historical = HistoricalRecords()

    class Meta:
        db_table = "NET"
        verbose_name = "Red"
        verbose_name_plural = "Redes"
        ordering = ["id"]

    def __str__(self):
        return f"Red {self.id}"

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        user = get_current_user()
        if user is not None:
            setattr(self, "user_creation" if not self.pk else "user_updated", user)
        super(Net, self).save()

    def toJSON(self):
        item = model_to_dict(self, exclude=["user_creation", "user_updated"])
        item["fk_trafo"] = str(self.fk_trafo)
        item["typeinstallation"] = self.get_typeinstallation_display()
        item["conductor"] = self.get_conductor_display()
        item["fk_material"] = str(self.fk_material.name)
        item["caliber"] = str(self.caliber)
        item["setting"] = self.get_setting_display()
        item["last_node"] = str(self.last_node)
        item["current_node"] = str(self.current_node)
        return item


""" MODELO DE CAJA AP"""


class ApBox(BaseModel):
    fk_node = models.ForeignKey(
        Node, on_delete=models.PROTECT, blank=True, null=True, verbose_name="Nodo"
    )
    fk_trafo = models.ForeignKey(
        Trafo,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        verbose_name="Transformador",
    )
    type = models.PositiveSmallIntegerField(
        choices=APBOX_TYPE, verbose_name="Tipo de caja"
    )
    owner = models.PositiveSmallIntegerField(
        choices=APBOX_PROPERTY, verbose_name="Propiedad"
    )
    status = models.PositiveSmallIntegerField(
        choices=STATUS, default=2, verbose_name="Estado"
    )
    historical = HistoricalRecords()

    class Meta:
        db_table = "AP_BOX"
        verbose_name = "Caja AP"
        verbose_name_plural = "Cajas APs"
        ordering = ["id"]

    def __str__(self):
        return f"{self.fk_node.code}-CAJA AP"

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        user = get_current_user()
        if user is not None:
            setattr(self, "user_creation" if not self.pk else "user_updated", user)
        super(ApBox, self).save()

    def toJSON(self):
        item = model_to_dict(self, exclude=["user_creation", "user_updated"])
        item["fk_node"] = str(self.fk_node)
        item["fk_trafo"] = str(self.fk_trafo)
        item["type"] = self.get_type_display()
        item["owner"] = self.get_owner_display()
        item["status"] = self.get_status_display()
        return item


""" MODELOS DE LUMINARIAS """


class LuminaireSetting(BaseModel):
    name = models.CharField(
        max_length=255, unique=True, blank=True, null=True, verbose_name="Nombre"
    )
    fk_tech = models.ForeignKey(
        LuminaireTech,
        on_delete=models.PROTECT,
        blank=False,
        null=False,
        verbose_name="Tecnología luminaria",
    )
    power = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Potencia (W)"
    )
    fk_type = models.ForeignKey(
        LuminaireType,
        on_delete=models.PROTECT,
        blank=False,
        null=False,
        verbose_name="Tipo de luminaria",
    )
    sap_code = models.PositiveIntegerField(
        null=True, blank=True, unique=True, verbose_name="Código SAP"
    )
    historical = HistoricalRecords()

    class Meta:
        db_table = "LUMINAIRE_SETTING"
        verbose_name = "Configuración Luminaria"
        verbose_name_plural = "Configuraciones de Luminarias"
        ordering = ["id"]

    def __str__(self):
        return f"{self.name}"

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        self.name = f"{self.fk_type.name} {self.fk_tech.name} {self.power}W"
        user = get_current_user()
        if user is not None:
            setattr(self, "user_creation" if not self.pk else "user_updated", user)
        super(LuminaireSetting, self).save()


class Luminaire(BaseModel):
    code = models.PositiveIntegerField(
        unique=True, blank=True, null=True, verbose_name="Código luminaria"
    )
    fk_setting = models.ForeignKey(
        LuminaireSetting,
        on_delete=models.PROTECT,
        verbose_name="Configuración luminaria",
    )
    fk_opticprotection = models.ForeignKey(
        OpticProtection,
        on_delete=models.PROTECT,
        blank=False,
        null=False,
        verbose_name="Protección Óptica",
    )
    fk_photocell = models.ForeignKey(
        PhotoCellType,
        on_delete=models.PROTECT,
        blank=False,
        null=False,
        verbose_name="Tipo control de encendido",
    )
    fk_lightedspace = models.ForeignKey(
        LightedSpace,
        on_delete=models.PROTECT,
        blank=False,
        null=True,
        verbose_name="Espacio Iluminado",
    )
    fk_armtype = models.ForeignKey(
        ArmType,
        on_delete=models.PROTECT,
        blank=False,
        null=False,
        verbose_name="Tipo de brazo",
    )
    fk_support = models.ForeignKey(
        LuminaireSupport,
        on_delete=models.PROTECT,
        blank=False,
        null=True,
        verbose_name="Soporte",
    )
    height = models.PositiveIntegerField(
        default=0, blank=True, null=False, verbose_name="Altura (m)"
    )
    financing = models.BooleanField(
        default=False, null=False, blank=False, verbose_name="Financiación"
    )
    status = models.PositiveSmallIntegerField(
        choices=STATUS, default=2, verbose_name="Estado"
    )
    fk_node = models.ForeignKey(
        Node,
        on_delete=models.PROTECT,
        blank=False,
        null=False,
        verbose_name="Nodo",
        db_index=True,
    )
    fk_trafo = models.ForeignKey(
        Trafo,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        verbose_name="Transformador",
    )
    fk_brand = models.ForeignKey(
        Brand,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        verbose_name="Fabricante",
    )
    date_installation = models.DateField(
        blank=True, null=True, verbose_name="Fecha instalación"
    )
    # Telegestion
    # fk_photocell_smart = models.OneToOneField(SmartPhotocell, on_delete=models.PROTECT, blank=True, null=True, verbose_name='Fotocelda inteligente')
    historical = HistoricalRecords()

    class Meta:
        db_table = "LUMINAIRE"
        verbose_name = "Luminaria"
        verbose_name_plural = "Luminarias"
        indexes = [
            models.Index(fields=["fk_node"]),
        ]
        ordering = ["code"]

    def __str__(self):
        return f"{self.code}-{self.fk_setting.name}"

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        user = get_current_user()
        if user is not None:
            setattr(self, "user_creation" if not self.pk else "user_updated", user)
        super(Luminaire, self).save()

    def toJSON(self):
        item = model_to_dict(self, exclude=["user_creation", "user_updated"])
        item["fk_setting"] = str(self.fk_setting)
        item["fk_opticprotection"] = str(self.fk_opticprotection)
        item["fk_photocell"] = str(self.fk_photocell)
        item["fk_lightedspace"] = str(self.fk_lightedspace)
        item["fk_armtype"] = str(self.fk_armtype)
        item["fk_support"] = str(self.fk_support)
        item["fk_trafo"] = str(self.fk_trafo)
        item["fk_brand"] = str(self.fk_brand)
        item["date_installation"] = str(self.date_installation)
        item["status"] = self.get_status_display()
        return item


""" MODELOS DE APOYOS """


class SupportSetting(BaseModel):
    name = models.CharField(
        max_length=300, unique=False, blank=True, null=True, verbose_name="Nombre"
    )
    fk_height = models.ForeignKey(
        SupportHeight, on_delete=models.PROTECT, null=True, verbose_name="Altura (m)"
    )
    fk_material = models.ForeignKey(
        Material, on_delete=models.PROTECT, verbose_name="Material"
    )
    fk_supporttype = models.ForeignKey(
        SupportType, on_delete=models.PROTECT, verbose_name="Tipo de poste"
    )
    fk_breaking_capacity = models.ForeignKey(
        BreakingCapacity,
        on_delete=models.PROTECT,
        null=True,
        verbose_name="Capacidad ruptura (Kgf)",
    )
    historical = HistoricalRecords()

    class Meta:
        db_table = "SUPPORT_SETTING"
        verbose_name = "Configuración Apoyo"
        verbose_name_plural = "Configuraciones de Apoyos"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name}"

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        user = get_current_user()
        if user is not None:
            setattr(self, "user_creation" if not self.pk else "user_updated", user)
        super(SupportSetting, self).save()

    def toJSON(self):
        item = model_to_dict(self, exclude=["user_creation", "user_updated"])
        item["fk_height"] = str(self.fk_height)
        item["fk_material"] = self.fk_material.name
        item["fk_supporttype"] = self.fk_supporttype.name
        item["fk_breaking_capacity"] = str(self.fk_breaking_capacity)
        return item


class Support(BaseModel):
    fk_setting = models.ForeignKey(
        SupportSetting, on_delete=models.PROTECT, verbose_name="Configuración apoyo"
    )
    fk_node = models.ForeignKey(
        Node,
        on_delete=models.PROTECT,
        blank=False,
        null=False,
        verbose_name="Nodo",
        db_index=True,
    )
    fk_trafo = models.ForeignKey(
        Trafo,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        verbose_name="Transformador",
    )
    fk_cimentation = models.ForeignKey(
        SupportCimentation,
        on_delete=models.PROTECT,
        blank=False,
        null=False,
        verbose_name="Cimentación",
    )
    owner = models.PositiveSmallIntegerField(
        default=1,
        blank=False,
        null=False,
        choices=SUPPORT_PROPERTY,
        verbose_name="Propiedad",
    )
    financing = models.BooleanField(default=False, verbose_name="Financiación")
    status = models.PositiveSmallIntegerField(
        default=2, choices=SUPPORT_STATUS, verbose_name="Estado"
    )
    historical = HistoricalRecords()

    class Meta:
        db_table = "SUPPORT"
        verbose_name = "Apoyo"
        verbose_name_plural = "Apoyos"
        indexes = [
            models.Index(fields=["fk_node"]),
        ]
        ordering = ["-id"]

    def __str__(self):
        return f"{self.id} {str(self.fk_setting)}"

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        user = get_current_user()
        if user is not None:
            setattr(self, "user_creation" if not self.pk else "user_updated", user)
        super(Support, self).save()

    def toJSON(self):
        item = model_to_dict(self, exclude=["user_creation", "user_updated"])
        item["fk_setting"] = self.fk_setting.name
        item["fk_node"] = str(self.fk_node)
        item["fk_trafo"] = str(self.fk_trafo)
        item["fk_cimentation"] = self.fk_cimentation.name
        item["owner"] = self.get_owner_display()
        item["status"] = self.get_status_display()
        return item


@receiver(pre_save, sender=SupportSetting)
def before_save_support_setting(sender, instance, **kwargs):
    with transaction.atomic():
        instance.name = f"{instance.fk_material.name} {instance.fk_height}M {instance.fk_breaking_capacity}Kgf"
