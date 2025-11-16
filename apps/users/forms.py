from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from apps.users.models import User, Area, Crew


class UserForm(UserCreationForm):
    """Formulario para crear y editar usuarios"""
    
    first_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200',
            'placeholder': 'Ingrese el nombre'
        }),
        label='Nombre'
    )
    
    last_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200',
            'placeholder': 'Ingrese el apellido'
        }),
        label='Apellido'
    )
    
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200',
            'placeholder': 'Ingrese el nombre de usuario'
        }),
        label='Nombre de Usuario',
        help_text='Requerido. 150 caracteres o menos. Letras, dígitos y @/./+/-/_ solamente.'
    )
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200',
            'placeholder': 'usuario@ejemplo.com'
        }),
        label='Correo Electrónico'
    )
    
    dni = forms.IntegerField(
        required=True,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200',
            'placeholder': 'Ingrese la cédula (7-10 dígitos)',
            'min': '1000000',
            'max': '9999999999'
        }),
        label='Cédula de Ciudadanía'
    )
    
    phone_number = forms.IntegerField(
        required=True,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200',
            'placeholder': 'Ingrese el teléfono (10 dígitos)'
        }),
        label='Número de Teléfono',
        help_text='Debe iniciar con 3 o 6 y tener 10 dígitos.'
    )
    
    fk_area = forms.ModelChoiceField(
        queryset=Area.objects.filter(is_active=True),
        required=True,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200'
        }),
        label='Área',
        empty_label='Seleccione un área'
    )
    
    fk_crew = forms.ModelChoiceField(
        queryset=Crew.objects.filter(is_active=True),
        required=False,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200'
        }),
        label='Cuadrilla (Opcional)',
        empty_label='Seleccione una cuadrilla'
    )
    
    password1 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200',
            'placeholder': 'Ingrese la contraseña'
        }),
        label='Contraseña'
    )
    
    password2 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200',
            'placeholder': 'Confirme la contraseña'
        }),
        label='Confirmar Contraseña'
    )
    
    is_active = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 focus:ring-2'
        }),
        label='Usuario Activo'
    )
    
    is_staff = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 focus:ring-2'
        }),
        label='Es Staff (Acceso al Admin)'
    )
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'dni', 'phone_number', 
                  'fk_area', 'fk_crew', 'password1', 'password2', 'is_active', 'is_staff']
    
    def clean_dni(self):
        """Validar que el DNI tenga entre 7 y 10 dígitos"""
        dni = self.cleaned_data.get('dni')
        if dni:
            dni_str = str(dni)
            if len(dni_str) < 7 or len(dni_str) > 10:
                raise ValidationError('El DNI debe tener entre 7 y 10 dígitos.')
        return dni
    
    def clean_phone_number(self):
        """Validar que el teléfono inicie con 3 o 6 y tenga 10 dígitos"""
        phone = self.cleaned_data.get('phone_number')
        if phone:
            phone_str = str(phone)
            if len(phone_str) != 10:
                raise ValidationError('El número de teléfono debe tener exactamente 10 dígitos.')
            if not phone_str.startswith(('3', '6')):
                raise ValidationError('El número de teléfono debe iniciar con 3 o 6.')
        return phone
    
    def clean(self):
        """Validación adicional para verificar que la cuadrilla pertenece al área seleccionada"""
        cleaned_data = super().clean()
        fk_area = cleaned_data.get('fk_area')
        fk_crew = cleaned_data.get('fk_crew')
        
        if fk_crew and fk_area:
            if fk_crew.fk_area != fk_area:
                raise ValidationError({
                    'fk_crew': 'La cuadrilla seleccionada no pertenece al área especificada.'
                })
        
        return cleaned_data


class UserUpdateForm(forms.ModelForm):
    """Formulario para editar usuarios (sin cambiar contraseña obligatoriamente)"""
    
    first_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200',
            'placeholder': 'Ingrese el nombre'
        }),
        label='Nombre'
    )
    
    last_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200',
            'placeholder': 'Ingrese el apellido'
        }),
        label='Apellido'
    )
    
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 bg-gray-100 border border-gray-300 rounded-lg cursor-not-allowed',
            'readonly': True
        }),
        label='Nombre de Usuario',
        help_text='El nombre de usuario no se puede modificar'
    )
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200',
            'placeholder': 'usuario@ejemplo.com'
        }),
        label='Correo Electrónico'
    )
    
    dni = forms.IntegerField(
        required=True,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200',
            'placeholder': 'Ingrese la cédula (7-10 dígitos)',
            'min': '1000000',
            'max': '9999999999'
        }),
        label='Cédula de Ciudadanía'
    )
    
    phone_number = forms.IntegerField(
        required=True,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200',
            'placeholder': 'Ingrese el teléfono (10 dígitos)'
        }),
        label='Número de Teléfono',
        help_text='Debe iniciar con 3 o 6 y tener 10 dígitos.'
    )
    
    fk_area = forms.ModelChoiceField(
        queryset=Area.objects.filter(is_active=True),
        required=True,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200'
        }),
        label='Área',
        empty_label='Seleccione un área'
    )
    
    fk_crew = forms.ModelChoiceField(
        queryset=Crew.objects.filter(is_active=True),
        required=False,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200'
        }),
        label='Cuadrilla (Opcional)',
        empty_label='Seleccione una cuadrilla'
    )
    
    is_active = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 focus:ring-2'
        }),
        label='Usuario Activo'
    )
    
    is_staff = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 focus:ring-2'
        }),
        label='Es Staff (Acceso al Admin)'
    )
    
    change_password = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 focus:ring-2',
            'id': 'id_change_password'
        }),
        label='Cambiar contraseña'
    )
    
    new_password1 = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200',
            'placeholder': 'Ingrese la nueva contraseña'
        }),
        label='Nueva Contraseña'
    )
    
    new_password2 = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200',
            'placeholder': 'Confirme la nueva contraseña'
        }),
        label='Confirmar Nueva Contraseña'
    )
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'dni', 'phone_number', 
                  'fk_area', 'fk_crew', 'is_active', 'is_staff']
    
    def clean_dni(self):
        """Validar que el DNI tenga entre 7 y 10 dígitos"""
        dni = self.cleaned_data.get('dni')
        if dni:
            dni_str = str(dni)
            if len(dni_str) < 7 or len(dni_str) > 10:
                raise ValidationError('El DNI debe tener entre 7 y 10 dígitos.')
        return dni
    
    def clean_phone_number(self):
        """Validar que el teléfono inicie con 3 o 6 y tenga 10 dígitos"""
        phone = self.cleaned_data.get('phone_number')
        if phone:
            phone_str = str(phone)
            if len(phone_str) != 10:
                raise ValidationError('El número de teléfono debe tener exactamente 10 dígitos.')
            if not phone_str.startswith(('3', '6')):
                raise ValidationError('El número de teléfono debe iniciar con 3 o 6.')
        return phone
    
    def clean(self):
        """Validaciones adicionales"""
        cleaned_data = super().clean()
        fk_area = cleaned_data.get('fk_area')
        fk_crew = cleaned_data.get('fk_crew')
        change_password = cleaned_data.get('change_password')
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')
        
        # Validar cuadrilla pertenece al área
        if fk_crew and fk_area:
            if fk_crew.fk_area != fk_area:
                raise ValidationError({
                    'fk_crew': 'La cuadrilla seleccionada no pertenece al área especificada.'
                })
        
        # Validar contraseñas si se marca cambiar contraseña
        if change_password:
            if not new_password1:
                raise ValidationError({
                    'new_password1': 'Debe ingresar una nueva contraseña.'
                })
            if not new_password2:
                raise ValidationError({
                    'new_password2': 'Debe confirmar la nueva contraseña.'
                })
            if new_password1 != new_password2:
                raise ValidationError({
                    'new_password2': 'Las contraseñas no coinciden.'
                })
            if len(new_password1) < 8:
                raise ValidationError({
                    'new_password1': 'La contraseña debe tener al menos 8 caracteres.'
                })
        
        return cleaned_data
    
    def save(self, commit=True):
        """Guardar el usuario y cambiar contraseña si es necesario"""
        user = super().save(commit=False)
        
        if self.cleaned_data.get('change_password'):
            user.set_password(self.cleaned_data['new_password1'])
        
        if commit:
            user.save()
        
        return user
