from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class RegistroUsuarioForm(UserCreationForm):
    """Formulario de registro personalizado en español"""
    username = forms.CharField(
        label='Nombre de usuario',
        max_length=150,
        help_text='Requerido. 150 caracteres o menos. Letras, dígitos y @/./+/-/_ solamente.',
        widget=forms.TextInput(attrs={'class': 'grade-input', 'placeholder': 'Ej: juan.perez'})
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

