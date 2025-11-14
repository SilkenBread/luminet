# Django
from django.contrib.auth import password_validation
from django.contrib.auth.forms import AuthenticationForm
from django import forms
from django.utils.translation import gettext_lazy as _

# local Django
from apps.users.models import User

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
        'placeholder': 'Ingrese un username',
        'class': 'form-control',
        'autocomplete': 'off'
        }))
    password = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Ingrese una contraseña',
            'autocomplete': "off",
            'class': 'form-control',
            }),
    )


class ResetPasswordForm(forms.Form):
    username = forms.CharField(
        label="Nombre de usuario",
        widget=forms.TextInput(attrs={
        'placeholder': 'Ingrese un username',
        'class': 'form-control',
        'autocomplete': 'off',
        'required': True
    }))


class ChangePasswordForm(forms.Form):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Ingrese una contraseña',
            'class': 'form-control',
            'name':'Contrasena',
            'autocomplete': 'off'
            }),
        help_text=password_validation.password_validators_help_text_html()
    )
    confirmPassword = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirma la contraseña',
            'class': 'form-control',
            'autocomplete': 'off'
            })
    )

    def clean(self):
        cleaned = super().clean()
        password = cleaned['password']
        confirmPassword = cleaned['confirmPassword']

        # Validamos que las contraseñas sean iguales
        if password != confirmPassword:
            raise forms.ValidationError('Las contraseñas deben ser iguales')
        
        # Validamos la seguridad de la contraseña
        try:
            password_validation.validate_password(password, None)
        except forms.ValidationError as error:
            raise forms.ValidationError(error)
        return cleaned
