import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mi_promedio_uss.settings')
django.setup()

from calculadora.models import Carrera, Ramo, Evaluacion

def populate():
    # Create Carrera
    carrera, created = Carrera.objects.get_or_create(nombre='Ingeniería Civil Informática', codigo='ICI')
    
    # Create Ramo 1: Programación Avanzada
    ramo1, created = Ramo.objects.get_or_create(nombre='Programación Avanzada', codigo='PA101', carrera=carrera, nota_objetivo=3.95)
    
    Evaluacion.objects.get_or_create(nombre='Solemne 1', tipo='SOLEMNE', ponderacion=20, nota=7.0, ramo=ramo1)
    Evaluacion.objects.get_or_create(nombre='Solemne 2', tipo='SOLEMNE', ponderacion=20, nota=7.0, ramo=ramo1)
    Evaluacion.objects.get_or_create(nombre='Solemne 3', tipo='SOLEMNE', ponderacion=20, nota=7.0, ramo=ramo1)
    Evaluacion.objects.get_or_create(nombre='Taller 1', tipo='TALLER', ponderacion=20, nota=7.0, ramo=ramo1)
    Evaluacion.objects.get_or_create(nombre='Taller 2', tipo='TALLER', ponderacion=20, nota=7.0, ramo=ramo1)

    # Create Ramo 2: Arquitectura de Computadores
    ramo2, created = Ramo.objects.get_or_create(nombre='Arquitectura de Computadores', codigo='AC102', carrera=carrera, nota_objetivo=3.95)
    
    Evaluacion.objects.get_or_create(nombre='Solemne 1', tipo='SOLEMNE', ponderacion=20, nota=6.5, ramo=ramo2)
    Evaluacion.objects.get_or_create(nombre='Solemne 2', tipo='SOLEMNE', ponderacion=20, nota=6.1, ramo=ramo2)
    Evaluacion.objects.get_or_create(nombre='Solemne 3', tipo='SOLEMNE', ponderacion=30, nota=None, ramo=ramo2)
    Evaluacion.objects.get_or_create(nombre='Talleres y Controles', tipo='TALLER', ponderacion=30, nota=None, ramo=ramo2)

    print("Dummy data populated successfully.")

if __name__ == '__main__':
    populate()
