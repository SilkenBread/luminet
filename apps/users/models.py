# Django
from django.db import models
from django.contrib.auth.models import AbstractUser

from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.forms import model_to_dict

# django-crum
from crum import get_current_request, get_current_user

# django-simple-history
from simple_history.models import HistoricalRecords

# local Django
from apps.models import BaseModel
# from ..infrastructure.models import Comuna

from colorfield.fields import ColorField


class Zone(BaseModel):
    name = models.CharField(
        max_length=255, unique=True, blank=False, null=False, verbose_name="Nombre"
    )
    # comunas = models.ManyToManyField(Comuna, blank=True, verbose_name="Comunas")
    fk_area = models.ForeignKey(
        "Area", on_delete=models.PROTECT, blank=True, null=True, verbose_name="Área"
    )
    color = ColorField(default="#FF0000")

    class Meta:
        db_table = "ZONE"
        verbose_name = "Zona"
        verbose_name_plural = "Zonas"
        ordering = ["id"]

    def __str__(self):
        return f"{self.name}"

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        user = get_current_user()
        if user is not None:
            setattr(self, "user_creation" if not self.pk else "user_updated", user)
        super(Zone, self).save()

    def toJSON(self):
        item = model_to_dict(self, exclude=["user_creation", "user_updated"])
        return item


class Area(BaseModel):
    name = models.CharField(
        max_length=255, unique=True, blank=False, null=False, verbose_name="Nombre"
    )
    description = models.TextField(
        blank=True, null=True, max_length=500, verbose_name="Descripción"
    )
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        db_table = "AREA"
        verbose_name = "Área"
        verbose_name_plural = "Áreas"
        ordering = ["id"]

    def __str__(self):
        return f"{self.name}"

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        user = get_current_user()
        if user is not None:
            setattr(self, "user_creation" if not self.pk else "user_updated", user)
        super(Area, self).save()


class Crew(BaseModel):
    name = models.CharField(
        max_length=255, unique=True, blank=False, null=False, verbose_name="Nombre"
    )
    fk_area = models.ForeignKey(
        Area, on_delete=models.PROTECT, blank=False, null=True, verbose_name="Área"
    )
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    historical = HistoricalRecords()

    class Meta:
        db_table = "CREW"
        verbose_name = "Cuadrilla"
        verbose_name_plural = "Cuadrillas"
        ordering = ["id"]

    def __str__(self):
        return f"{self.name}"

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        user = get_current_user()
        if user is not None:
            setattr(self, "user_creation" if not self.pk else "user_updated", user)
        super(Crew, self).save()

    def toJSON(self):
        item = model_to_dict(self, exclude=["user_creation", "user_updated"])
        return item


# Función de compatibilidad para migraciones antiguas
def user_avatar_upload_path(instance, filename):
    """
    DEPRECATED: Esta función se mantiene solo para compatibilidad con migraciones antiguas.
    El campo avatar ha sido removido del modelo User.
    """
    extension = filename.split(".")[-1]
    return f"users/{instance.id}-{instance.dni}.{extension}"


class User(AbstractUser, BaseModel):
    phone_number = models.PositiveBigIntegerField(
        unique=False,
        blank=False,
        null=False,
        validators=[
            RegexValidator(
                regex=r"^(3|6)\d{9}$",
                message=("No es un número de teléfono válido"),
                code="invalid_phonenumber",
            )
        ],
        verbose_name="Número teléfono",
    )
    dni = models.PositiveBigIntegerField(
        unique=True,
        blank=False,
        null=False,
        validators=[
            RegexValidator(
                regex=r"^\d{7,10}$",
                message=("No es un número de documento válido"),
                code="invalid_dni",
            )
        ],
        verbose_name="Cédula ciudadania",
    )
    fk_area = models.ForeignKey(
        Area, on_delete=models.PROTECT, blank=False, null=True, verbose_name="Área"
    )
    fk_crew = models.ForeignKey(
        Crew, on_delete=models.PROTECT, blank=True, null=True, verbose_name="Cuadrilla"
    )
    historical = HistoricalRecords()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["first_name", "last_name", "email", "dni", "phone_number"]

    class Meta:
        db_table = "USER"
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        ordering = ["id"]

    def clean(self):
        # Llamar al método clean original para cualquier otra validación
        super().clean()

        # Validación de que fk_crew y fk_area están en la misma área
        if self.fk_crew and self.fk_area:
            if self.fk_crew.fk_area != self.fk_area:
                raise ValidationError(
                    {
                        "fk_crew": "La cuadrilla seleccionada no pertenece al área especificada.",
                        "fk_area": "El área especificada no coincide con la cuadrilla seleccionada.",
                    }
                )

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        self.first_name = self.first_name.title()
        self.last_name = self.last_name.title()
        self.email = self.email.lower()
        super(User, self).save()

    def get_gradient_colors(self):
        """
        Genera un gradiente único basado en el ID del usuario.
        Retorna un diccionario con los colores del gradiente.
        """
        # Lista de combinaciones de gradientes atractivos
        gradients = [
            {"from": "blue-500", "to": "purple-600", "from_hex": "#3b82f6", "to_hex": "#9333ea"},
            {"from": "pink-500", "to": "rose-600", "from_hex": "#ec4899", "to_hex": "#e11d48"},
            {"from": "green-500", "to": "teal-600", "from_hex": "#22c55e", "to_hex": "#0d9488"},
            {"from": "orange-500", "to": "red-600", "from_hex": "#f97316", "to_hex": "#dc2626"},
            {"from": "indigo-500", "to": "blue-600", "from_hex": "#6366f1", "to_hex": "#2563eb"},
            {"from": "cyan-500", "to": "blue-600", "from_hex": "#06b6d4", "to_hex": "#2563eb"},
            {"from": "violet-500", "to": "purple-600", "from_hex": "#8b5cf6", "to_hex": "#9333ea"},
            {"from": "fuchsia-500", "to": "pink-600", "from_hex": "#d946ef", "to_hex": "#db2777"},
            {"from": "emerald-500", "to": "green-600", "from_hex": "#10b981", "to_hex": "#16a34a"},
            {"from": "amber-500", "to": "orange-600", "from_hex": "#f59e0b", "to_hex": "#ea580c"},
        ]
        
        # Usar el ID del usuario para seleccionar un gradiente de forma consistente
        index = self.id % len(gradients)
        return gradients[index]

    def get_group_session(self):
        try:
            request = get_current_request()
            groups = self.groups.all()
            if groups.exists():
                if "group" not in request.session:
                    request.session["group"] = groups[0]
        except:
            pass

    def toJSON(self):
        item = model_to_dict(
            self, exclude=["password", "user_permissions", "last_login"]
        )
        if self.last_login:
            item["last_login"] = self.last_login.strftime("%Y-%m-%d")
        item["date_joined"] = self.date_joined.strftime("%Y-%m-%d")
        item["gradient"] = self.get_gradient_colors()
        item["full_name"] = self.get_full_name()
        item["groups"] = [{"id": g.id, "name": g.name} for g in self.groups.all()]
        return item


class Reporter(models.Model):
    name = models.CharField(
        max_length=255,
        unique=False,
        blank=False,
        null=False,
        validators=[
            RegexValidator(
                regex=r"^[A-Za-zá-úüñÁ-ÚÜÑ\s]+$",
                message=("No es un nombre válido"),
                code="invalid_name",
            )
        ],
        verbose_name="Nombre",
    )
    dni = models.PositiveBigIntegerField(
        unique=True,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex=r"^\d{7,10}$",
                message=("No es un número de documento válido"),
                code="invalid_dni",
            )
        ],
        verbose_name="Cédula ciudadania",
    )
    phone_number = models.PositiveBigIntegerField(
        unique=False,
        blank=False,
        null=True,
        validators=[
            RegexValidator(
                regex=r"^(3|6)\d{9}$",
                message=("No es un número de teléfono válido"),
                code="invalid_phonenumber",
            )
        ],
        verbose_name="Número teléfono",
    )
    email = models.EmailField(
        verbose_name="Correo electrónico", null=True, blank=False, unique=False
    )

    def __str__(self):
        return f"{self.dni} {self.name}"

    class Meta:
        db_table = "REPORTER"
        verbose_name = "Reportador"
        verbose_name_plural = "Reportadores"
        ordering = ["id"]
