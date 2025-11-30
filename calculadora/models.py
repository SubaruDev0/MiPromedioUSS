from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class Carrera(models.Model):
    nombre = models.CharField(max_length=100, verbose_name="Nombre de la Carrera")
    codigo = models.CharField(max_length=20, unique=True, verbose_name="Código")

    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name = "Carrera"
        verbose_name_plural = "Carreras"

class PerfilUsuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Usuario")
    carrera = models.ForeignKey(Carrera, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Carrera")

    def __str__(self):
        return self.user.username
    
    class Meta:
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuario"

class Ramo(models.Model):
    ANIO_CHOICES = [
        ('1', 'Primero'),
        ('2', 'Segundo'),
        ('3', 'Tercero'),
        ('4', 'Cuarto'),
        ('5', 'Quinto'),
        ('6', 'Sexto'),
        ('7', 'Séptimo'),
        ('8', 'Octavo'),
        ('9', 'Noveno'),
        ('10', 'Décimo'),
    ]
    
    nombre = models.CharField(max_length=100, verbose_name="Nombre del Ramo")
    codigo = models.CharField(max_length=20, verbose_name="Código", blank=True, null=True)
    semestre = models.IntegerField(default=1, verbose_name="Semestre")
    carrera = models.ForeignKey(Carrera, on_delete=models.CASCADE, related_name='ramos', verbose_name="Carrera")
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ramos', null=True, blank=True, verbose_name="Usuario")
    anio_academico = models.CharField(max_length=2, choices=ANIO_CHOICES, default='1', verbose_name="Año en el que vas")
    asistencia = models.IntegerField(default=0, verbose_name="Asistencia (%)", validators=[MinValueValidator(0), MaxValueValidator(100)])
    nota_objetivo = models.FloatField(default=3.95, validators=[MinValueValidator(1.0), MaxValueValidator(7.0)], verbose_name="Nota Objetivo")
    is_historical = models.BooleanField(default=False, verbose_name="Es Histórico")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")

    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name = "Ramo"
        verbose_name_plural = "Ramos"
        ordering = ['-is_historical', 'anio_academico', 'semestre', 'nombre']

class Evaluacion(models.Model):
    TIPO_CHOICES = [
        ('SOLEMNE', 'Solemne'),
        ('TALLER', 'Taller'),
        ('CONTROL', 'Control'),
        ('LABORATORIO', 'Laboratorio'),
        ('PROYECTO', 'Proyecto'),
        ('OTRO', 'Otro'),
    ]

    nombre = models.CharField(max_length=100, verbose_name="Nombre de la Evaluación")
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='SOLEMNE', verbose_name="Tipo")
    ponderacion = models.FloatField(help_text="Porcentaje de la nota (0-100)", validators=[MinValueValidator(0), MaxValueValidator(100)], verbose_name="Ponderación")
    nota = models.FloatField(null=True, blank=True, validators=[MinValueValidator(1.0), MaxValueValidator(7.0)], verbose_name="Nota")
    ramo = models.ForeignKey(Ramo, on_delete=models.CASCADE, related_name='evaluaciones', verbose_name="Ramo")

    def __str__(self):
        return f"{self.nombre} - {self.ramo.nombre}"
    
    def get_order_priority(self):
        """Retorna prioridad de ordenamiento: Solemnes primero, luego Talleres/Parciales"""
        priority_map = {
            'SOLEMNE': 1,
            'CONTROL': 2,
            'LABORATORIO': 3,
            'PROYECTO': 4,
            'TALLER': 5,
            'OTRO': 6,
        }
        return priority_map.get(self.tipo, 99)

    class Meta:
        verbose_name = "Evaluación"
        verbose_name_plural = "Evaluaciones"
        ordering = ['tipo', 'nombre']  # Primero por tipo, luego por nombre
