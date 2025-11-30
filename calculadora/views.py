from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Ramo, Carrera, Evaluacion, PerfilUsuario
from .forms import RegistroUsuarioForm
import json

def home(request):
    """
    Vista de inicio.
    Muestra la calculadora rápida para todos los usuarios.
    """
    return render(request, 'calculadora/guest_calculator.html')

@login_required
def dashboard(request):
    """
    Dashboard principal del usuario (Mis Notas).
    Muestra ramos del período más reciente como actuales, y el resto como históricos.
    """
    # Obtener todos los ramos del usuario ordenados por período
    todos_ramos = Ramo.objects.filter(usuario=request.user).order_by('-anio_academico', '-semestre', '-created_at')

    if todos_ramos.exists():
        # Determinar el período más reciente (mayor año + semestre)
        ultimo_ramo = todos_ramos.first()
        anio_actual = ultimo_ramo.anio_academico
        semestre_actual = ultimo_ramo.semestre

        # Convertir a formato legible
        anio_num = dict(Ramo.ANIO_CHOICES).get(anio_actual, f'Año {anio_actual}')

        # Mapa de conversiones
        conversion_map = {
            'Primero': 'Primer año',
            'Segundo': 'Segundo año',
            'Tercero': 'Tercer año',
            'Cuarto': 'Cuarto año',
            'Quinto': 'Quinto año',
            'Sexto': 'Sexto año',
            'Séptimo': 'Séptimo año',
            'Octavo': 'Octavo año',
            'Noveno': 'Noveno año',
            'Décimo': 'Décimo año',
        }

        anio_actual_label = conversion_map.get(anio_num, anio_num)
        semestre_actual_label = f'Semestre {semestre_actual}'

        # Ramos actuales: del período más reciente
        ramos = todos_ramos.filter(anio_academico=anio_actual, semestre=semestre_actual)

        # Calcular promedio del período actual (se hará después de calcular promedios individuales)
        promedio_actual_periodo = 0

        # Ramos históricos: todos los demás, ordenados por período descendente (año desc, semestre asc)
        ramos_historicos_query = todos_ramos.exclude(anio_academico=anio_actual, semestre=semestre_actual).order_by('-anio_academico', 'semestre')

        # Agrupar históricos por año y semestre (primero por año, luego semestres dentro)
        from collections import OrderedDict
        ramos_historicos_agrupados = OrderedDict()

        for ramo in ramos_historicos_query:
            # Convertir el label a formato "Primer año", "Segundo año", etc.
            anio_num = dict(Ramo.ANIO_CHOICES).get(ramo.anio_academico, f'Año {ramo.anio_academico}')

            # Mapa de conversiones
            conversion_map = {
                'Primero': 'Primer año',
                'Segundo': 'Segundo año',
                'Tercero': 'Tercer año',
                'Cuarto': 'Cuarto año',
                'Quinto': 'Quinto año',
                'Sexto': 'Sexto año',
                'Séptimo': 'Séptimo año',
                'Octavo': 'Octavo año',
                'Noveno': 'Noveno año',
                'Décimo': 'Décimo año',
            }

            anio_label = conversion_map.get(anio_num, anio_num)

            # Crear estructura: año -> semestres -> ramos
            if ramo.anio_academico not in ramos_historicos_agrupados:
                ramos_historicos_agrupados[ramo.anio_academico] = {
                    'label': anio_label,
                    'semestres': OrderedDict()
                }

            if ramo.semestre not in ramos_historicos_agrupados[ramo.anio_academico]['semestres']:
                ramos_historicos_agrupados[ramo.anio_academico]['semestres'][ramo.semestre] = {
                    'ramos': [],
                    'promedio': 0
                }

            ramos_historicos_agrupados[ramo.anio_academico]['semestres'][ramo.semestre]['ramos'].append(ramo)
    else:
        ramos = Ramo.objects.none()
        ramos_historicos_agrupados = OrderedDict()
        anio_actual_label = None
        semestre_actual_label = None

    # Calcular promedios para todos los ramos
    all_ramos_list = []
    for anio_data in ramos_historicos_agrupados.values():
        for semestre_data in anio_data['semestres'].values():
            all_ramos_list.extend(semestre_data['ramos'])

    all_ramos = list(ramos) + all_ramos_list

    for ramo in all_ramos:
        evaluaciones = ramo.evaluaciones.all()
        if evaluaciones:
            weighted_sum = sum(e.nota * e.ponderacion for e in evaluaciones if e.nota)
            total_weight = sum(e.ponderacion for e in evaluaciones if e.nota)
            if total_weight > 0:
                ramo.promedio_actual = round(weighted_sum / total_weight, 1)
            else:
                ramo.promedio_actual = 0
        else:
            ramo.promedio_actual = 0

        # Convertir nota_objetivo de escala 1-7 a escala 10-70 para mostrar
        ramo.nota_objetivo_display = round(ramo.nota_objetivo * 10, 1)
    
    # Calcular promedio del período actual
    if ramos:
        promedios_ramos_actuales = [r.promedio_actual for r in ramos if r.promedio_actual > 0]
        if promedios_ramos_actuales:
            promedio_actual_periodo = round(sum(promedios_ramos_actuales) / len(promedios_ramos_actuales), 1)
        else:
            promedio_actual_periodo = 0
    
    # Calcular promedios por semestre y año
    for anio_academico, anio_data in ramos_historicos_agrupados.items():
        promedios_anio = []

        for semestre, semestre_data in anio_data['semestres'].items():
            ramos_semestre = semestre_data['ramos']
            if ramos_semestre:
                promedios_ramos = [r.promedio_actual for r in ramos_semestre if r.promedio_actual > 0]
                if promedios_ramos:
                    semestre_data['promedio'] = round(sum(promedios_ramos) / len(promedios_ramos), 1)
                    promedios_anio.append(semestre_data['promedio'])
                else:
                    semestre_data['promedio'] = 0

        # Calcular promedio del año
        if promedios_anio:
            anio_data['promedio'] = round(sum(promedios_anio) / len(promedios_anio), 1)
        else:
            anio_data['promedio'] = 0

    return render(request, 'calculadora/dashboard.html', {
        'ramos': ramos,
        'ramos_historicos_agrupados': ramos_historicos_agrupados,
        'anio_actual_label': anio_actual_label,
        'semestre_actual_label': semestre_actual_label,
        'promedio_actual_periodo': promedio_actual_periodo,
    })

@login_required
def ramo_detail(request, ramo_id):
    """
    Vista de detalle para un ramo específico.
    """
    ramo = get_object_or_404(Ramo, id=ramo_id, usuario=request.user)
    return render(request, 'calculadora/ramo_detail.html', {'ramo': ramo})

@login_required
def add_course(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        # codigo is optional now
        codigo = request.POST.get('codigo', '')
        anio_academico = request.POST.get('anio_academico')
        semestre = request.POST.get('semestre')
        asistencia = request.POST.get('asistencia', 0)
        
        # Crear Ramo
        carrera = None
        if hasattr(request.user, 'perfilusuario') and request.user.perfilusuario.carrera:
            carrera = request.user.perfilusuario.carrera
        else:
            carrera, _ = Carrera.objects.get_or_create(nombre="General", codigo="GEN")

        ramo = Ramo.objects.create(
            nombre=nombre,
            codigo=codigo,
            anio_academico=anio_academico,
            semestre=semestre,
            asistencia=asistencia,
            usuario=request.user,
            carrera=carrera,
            is_historical=False
        )

        # Crear Evaluaciones
        eval_names = request.POST.getlist('eval_names[]')
        eval_weights = request.POST.getlist('eval_weights[]')
        eval_types = request.POST.getlist('eval_types[]')

        for i in range(len(eval_names)):
            if eval_names[i] and eval_weights[i]:
                Evaluacion.objects.create(
                    nombre=eval_names[i],
                    tipo=eval_types[i],
                    ponderacion=float(eval_weights[i]),
                    ramo=ramo
                )
        
        return redirect('dashboard')

    # Pasar las opciones de año académico al template
    anio_choices = Ramo.ANIO_CHOICES
    return render(request, 'calculadora/add_course.html', {'anio_choices': anio_choices})

@login_required
def delete_course(request, ramo_id):
    ramo = get_object_or_404(Ramo, id=ramo_id, usuario=request.user)
    if request.method == 'POST':
        ramo.delete()
        return redirect('dashboard')
    return redirect('dashboard')

@login_required
def edit_course(request, ramo_id):
    ramo = get_object_or_404(Ramo, id=ramo_id, usuario=request.user)
    
    if request.method == 'POST':
        ramo.nombre = request.POST.get('nombre')
        ramo.anio_academico = request.POST.get('anio_academico')
        ramo.semestre = request.POST.get('semestre')
        ramo.asistencia = request.POST.get('asistencia')
        ramo.save()

        # Agregar nuevas evaluaciones
        eval_names = request.POST.getlist('eval_names[]')
        eval_weights = request.POST.getlist('eval_weights[]')
        eval_types = request.POST.getlist('eval_types[]')

        for i in range(len(eval_names)):
            if eval_names[i] and eval_weights[i]:
                Evaluacion.objects.create(
                    nombre=eval_names[i],
                    tipo=eval_types[i],
                    ponderacion=float(eval_weights[i]),
                    ramo=ramo
                )
        
        return redirect('dashboard')

    # Calcular peso total de evaluaciones existentes
    total_peso_existente = sum(eval.ponderacion for eval in ramo.evaluaciones.all())

    anio_choices = Ramo.ANIO_CHOICES
    return render(request, 'calculadora/edit_course.html', {
        'ramo': ramo,
        'anio_choices': anio_choices,
        'total_peso_existente': total_peso_existente
    })

def register(request):
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Obtener o crear la carrera
            carrera_nombre = form.cleaned_data.get('carrera')
            if carrera_nombre:
                carrera, _ = Carrera.objects.get_or_create(
                    nombre=carrera_nombre,
                    defaults={'codigo': carrera_nombre[:3].upper()}
                )
                PerfilUsuario.objects.create(user=user, carrera=carrera)
            
            login(request, user)
            return redirect('dashboard')
    else:
        form = RegistroUsuarioForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
@require_POST
def save_grade(request, evaluacion_id):
    """Guardar nota de una evaluación via AJAX"""
    try:
        evaluacion = get_object_or_404(Evaluacion, id=evaluacion_id, ramo__usuario=request.user)
        data = json.loads(request.body)
        nota = data.get('nota')

        print(f"[DEBUG] Guardando nota para evaluacion {evaluacion_id}: '{nota}' (tipo: {type(nota)})")

        if nota is not None and nota != '':
            evaluacion.nota = float(nota)
        else:
            evaluacion.nota = None

        evaluacion.save()
        print(f"[DEBUG] Nota guardada exitosamente: {evaluacion.nota}")
        return JsonResponse({'success': True, 'nota': evaluacion.nota})
    except Exception as e:
        print(f"[ERROR] Error al guardar nota: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@login_required
@require_POST
def delete_evaluacion(request, evaluacion_id):
    """Eliminar una evaluación via AJAX"""
    try:
        evaluacion = get_object_or_404(Evaluacion, id=evaluacion_id, ramo__usuario=request.user)
        evaluacion.delete()
        return JsonResponse({'success': True})
    except Exception as e:
        print(f"[ERROR] Error al eliminar evaluación: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@login_required
@require_POST
def save_nota_objetivo(request, ramo_id):
    """Guardar nota objetivo de un ramo via AJAX"""
    try:
        ramo = get_object_or_404(Ramo, id=ramo_id, usuario=request.user)
        data = json.loads(request.body)
        nota_objetivo = data.get('nota_objetivo')

        print(f"[DEBUG] Guardando nota objetivo para ramo {ramo_id}: '{nota_objetivo}'")

        if nota_objetivo is not None and nota_objetivo != '':
            # Convertir de escala 10-70 a escala 1-7
            ramo.nota_objetivo = float(nota_objetivo) / 10
        else:
            ramo.nota_objetivo = 3.95  # Por defecto: "pasar es pasar"

        ramo.save()
        print(f"[DEBUG] Nota objetivo guardada: {ramo.nota_objetivo}")
        return JsonResponse({'success': True, 'nota_objetivo': ramo.nota_objetivo})
    except Exception as e:
        print(f"[ERROR] Error al guardar nota objetivo: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

