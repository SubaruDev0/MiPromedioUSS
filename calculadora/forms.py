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
        label='Nombre de usuario',
        max_length=150,
        help_text='No uses espacios. Usa guiones bajos (_) para separar palabras. Ejemplo: Javier_Morales',
        widget=forms.TextInput(attrs={'class': 'grade-input', 'placeholder': 'Ej: Javier_Morales'}),
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
    # Lista simplificada y abreviada de carreras por áreas (el usuario debe elegir una)
    CARRERAS_CHOICES = [
        ('Medicina', 'Medicina'),
        ('Odontología', 'Odontología'),
        ('Enfermería', 'Enfermería'),
        ('Nutrición y Dietética', 'Nutrición y Dietética'),
        ('Obstetricia', 'Obstetricia'),
        ('Tecnología Médica', 'Tecnología Médica'),
        ('Kinesiología', 'Kinesiología'),
        ('Fonoaudiología', 'Fonoaudiología'),
        ('Terapia Ocupacional', 'Terapia Ocupacional'),
        ('Química y Farmacia', 'Química y Farmacia'),
        ('Bioquímica', 'Bioquímica'),
        ('Ingeniería Civil', 'Ingeniería Civil'),
        ('Ingeniería Civil Industrial', 'Ing. Civil Industrial'),
        ('Ingeniería Civil en Informática y Computación', 'Ing. Civil en Informática'),
        ('Ingeniería Civil en Minas', 'Ing. Civil en Minas'),
        ('Geología', 'Geología'),
        ('Ing. Recursos Naturales y Sostenibilidad', 'Ing. Recursos Naturales y Sostenibilidad'),
        ('Ingeniería en Expediciones y Ecoturismo', 'Ing. Expediciones y Ecoturismo'),
        ('Pedagogía en Educación Básica', 'Pedagogía en Educación Básica'),
        ('Pedagogía Parvularia', 'Pedagogía en Educación Parvularia'),
        ('Pedagogía en Educación Diferencial', 'Pedagogía en Educación Diferencial'),
        ('Pedagogía en Inglés', 'Pedagogía en Inglés'),
        ('Educación Física', 'Educación Física'),
        ('Derecho', 'Derecho'),
        ('Psicología', 'Psicología'),
        ('Trabajo Social', 'Trabajo Social'),
        ('Historia', 'Historia'),
        ('Administración Pública', 'Administración Pública'),
        ('Ingeniería Comercial', 'Ingeniería Comercial'),
        ('Contabilidad y Auditoría', 'Contabilidad y Auditoría'),
        ('Economía', 'Economía'),
        ('Marketing y Gestión Comercial', 'Marketing y Gestión Comercial'),
        ('Arquitectura', 'Arquitectura'),
        ('Animación Digital', 'Animación Digital')
    ]

    carrera = forms.ChoiceField(
        label='Carrera',
        choices=CARRERAS_CHOICES,
        widget=forms.Select(attrs={'class': 'grade-input'}),
        required=True,
        help_text='Elige una carrera de la lista'
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
    
    def clean_username(self):
        """Sobrescribir validación de username para permitir espacios"""
        username = self.cleaned_data.get('username')
        # Validar longitud
        if len(username) > 150:
            raise forms.ValidationError('El nombre de usuario no puede tener más de 150 caracteres.')
        # Validar con nuestro regex personalizado (permite espacios)
        if not self.username_validator.regex.match(username):
            raise forms.ValidationError(self.username_validator.message)
        # Validar que no exista otro usuario con ese nombre
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Este nombre de usuario ya está en uso.')
        return username

