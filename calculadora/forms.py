from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

class RegistroUsuarioForm(UserCreationForm):
    """Formulario de registro personalizado en español"""
    # Validador personalizado que permite espacios
    username_validator = RegexValidator(
        regex=r'^[\w\s.@+-]+$',
        message='Introduce un nombre válido. Puede contener letras, números, espacios y los caracteres @/./+/-/_',
        code='invalid_username'
    )
    
    username = forms.CharField(
        label='Nombre completo o usuario',
        max_length=150,
        help_text='Puedes usar tu nombre completo o un nombre de usuario. Ejemplo: Javier Morales o javi.morales',
        widget=forms.TextInput(attrs={'class': 'grade-input', 'placeholder': 'Ej: Javier Morales'}),
        validators=[username_validator]
    )
    password1 = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={'class': 'grade-input'}),
        help_text='Tu contraseña debe contener al menos 8 caracteres y no puede ser completamente numérica.'
    )
    password2 = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput(attrs={'class': 'grade-input'}),
        help_text='Ingresa la misma contraseña para verificación.'
    )
    email = forms.EmailField(
        label='Correo electrónico',
        required=False,
        widget=forms.EmailInput(attrs={'class': 'grade-input', 'placeholder': 'ejemplo@uss.cl'})
    )
    carrera = forms.CharField(
        label='Carrera',
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'grade-input', 'placeholder': 'Ej: Ingeniería Civil Informática'}),
        required=True
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personalizar mensajes de error en español
        self.error_messages = {
            'password_mismatch': 'Las dos contraseñas no coinciden.',
        }
        # Remover el validador por defecto de Django que no permite espacios
        if 'username' in self.fields:
            self.fields['username'].validators = [self.username_validator]

