from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Ramo, Carrera, Evaluacion, PerfilUsuario
from .forms import RegistroUsuarioForm
import json
from django.core.cache import cache
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.views.decorators.http import require_POST
from django import forms
from django.utils import timezone

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
    try:
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
            promedio_actual_periodo = 0

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
    except Exception as e:
        # Si hay error, mostrar dashboard vacío
        print(f"Error en dashboard: {e}")
        return render(request, 'calculadora/dashboard.html', {
            'ramos': Ramo.objects.none(),
            'ramos_historicos_agrupados': {},
            'anio_actual_label': None,
            'semestre_actual_label': None,
            'promedio_actual_periodo': 0,
        })

@login_required
def ramo_detail(request, ramo_id):
    """
    Vista de detalle para un ramo específico.
    """
    ramo = get_object_or_404(Ramo, id=ramo_id, usuario=request.user)
    return render(request, 'calculadora/ramo_detail.html', {'ramo': ramo})


@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_panel(request):
    """Panel muy sencillo para administradores: listar usuarios y limpiar cache."""
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'clear_cache':
            try:
                cache.clear()
                messages.success(request, 'Cache limpiada correctamente.')
            except Exception as e:
                messages.error(request, f'Error limpiando cache: {e}')
        return redirect('admin_panel')

    users = User.objects.all().order_by('-date_joined')
    # Pass minimal fields to template
    users_data = users.values('id', 'username', 'email', 'is_staff', 'is_superuser', 'date_joined', 'last_login')
    return render(request, 'calculadora/admin_panel.html', {
        'users': users_data,
        'users_count': users.count()
    })


@login_required
def notifications_view(request):
    """Mostrar notificaciones guardadas en cache para el usuario."""
    key = f'notifications:{request.user.id}'
    notifications = cache.get(key, [])
    return render(request, 'calculadora/notifications.html', {'notifications': notifications})


@login_required
def profile_view(request):
    """Mostrar y editar datos de perfil (username, email)."""
    class UsernameForm(forms.Form):
        username = forms.CharField(max_length=150)

    if request.method == 'POST':
        form = UsernameForm(request.POST)
        if form.is_valid():
            new_username = form.cleaned_data['username']
            # Validar unicidad
            if User.objects.exclude(id=request.user.id).filter(username=new_username).exists():
                messages.error(request, 'El nombre de usuario ya está en uso.')
            else:
                request.user.username = new_username
                request.user.save()
                messages.success(request, 'Nombre de usuario actualizado.')
                return redirect('profile')
    else:
        form = UsernameForm(initial={'username': request.user.username})

    return render(request, 'calculadora/profile.html', {'form': form})


@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Contraseña actualizada correctamente.')
            return redirect('profile')
        else:
            messages.error(request, 'Corrige los errores en el formulario.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'calculadora/change_password.html', {'form': form})


@login_required
@user_passes_test(lambda u: u.is_superuser)
@require_POST
def admin_delete_user(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        if user.is_superuser:
            messages.error(request, 'No puedes eliminar a otro superusuario.')
        else:
            user.delete()
            messages.success(request, f'Usuario {user.username} eliminado.')
    except User.DoesNotExist:
        messages.error(request, 'Usuario no encontrado.')
    return redirect('admin_panel')


@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_user_ramos(request, user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, 'Usuario no encontrado.')
        return redirect('admin_panel')

    ramos = Ramo.objects.filter(usuario=user).order_by('-anio_academico', '-semestre')
    return render(request, 'calculadora/admin_user_ramos.html', {'target_user': user, 'ramos': ramos})

@login_required
def add_course(request):
    if request.method == 'POST':
        try:
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

            # VALIDACIÓN SERVIDOR: pesos obligatorios y suman 100
            weights = []
            for w in eval_weights:
                try:
                    weights.append(float(w))
                except Exception:
                    weights.append(0.0)

            total_weights = round(sum(weights), 4)
            if total_weights != 100.0:
                messages.error(request, 'La suma de porcentajes de las evaluaciones debe ser exactamente 100%.')
                ramo.delete()
                return render(request, 'calculadora/add_course.html', {'anio_choices': Ramo.ANIO_CHOICES, 'form_data': request.POST})

            for i in range(len(eval_names)):
                if eval_names[i] and eval_weights[i]:
                    # Clamp ponderacion a 0-100 por seguridad
                    try:
                        ponder = float(eval_weights[i])
                    except Exception:
                        ponder = 0.0
                    ponder = max(0.0, min(100.0, ponder))
                    Evaluacion.objects.create(
                        nombre=eval_names[i],
                        tipo=eval_types[i],
                        ponderacion=ponder,
                        ramo=ramo
                    )
            # Añadir notificación en cache para el usuario
            try:
                key = f'notifications:{request.user.id}'
                notifications = cache.get(key, [])
                notifications.insert(0, {
                    'message': f"Ramo '{ramo.nombre}' creado exitosamente.",
                    'created_at': timezone.now().isoformat(),
                    'link': ''
                })
                # Mantener sólo las 25 más recientes
                cache.set(key, notifications[:25], None)
            except Exception:
                pass

            return redirect('dashboard')
        except Exception as e:
            print(f"Error al crear ramo: {e}")
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
        try:
            ramo.nombre = request.POST.get('nombre')
            ramo.anio_academico = request.POST.get('anio_academico')
            ramo.semestre = request.POST.get('semestre')
            ramo.asistencia = request.POST.get('asistencia')
            ramo.save()

            # Actualizar ponderaciones de evaluaciones existentes
            eval_ids = request.POST.getlist('eval_ids[]')
            eval_existing_weights = request.POST.getlist('eval_existing_weights[]')
            
            for i in range(len(eval_ids)):
                if eval_ids[i] and eval_existing_weights[i]:
                    evaluacion = Evaluacion.objects.get(id=eval_ids[i], ramo=ramo)
                    try:
                        p = float(eval_existing_weights[i])
                    except Exception:
                        p = 0.0
                    evaluacion.ponderacion = max(0.0, min(100.0, p))
                    evaluacion.save()

            # Agregar nuevas evaluaciones
            eval_names = request.POST.getlist('eval_names[]')
            eval_weights = request.POST.getlist('eval_weights[]')
            eval_types = request.POST.getlist('eval_types[]')
            # VALIDACIÓN SERVIDOR: comprobar que la suma total (existentes + nuevas) sea 100
            existing = [float(w) for w in eval_existing_weights if w not in (None, '', [])]
            new = []
            for w in eval_weights:
                try:
                    new.append(float(w))
                except Exception:
                    new.append(0.0)

            total_weights = round(sum(existing) + sum(new), 4)
            if total_weights != 100.0:
                messages.error(request, 'La suma de porcentajes de las evaluaciones debe ser exactamente 100%.')
                return render(request, 'calculadora/edit_course.html', {
                    'ramo': ramo,
                    'anio_choices': Ramo.ANIO_CHOICES,
                    'total_peso_existente': sum(eval.ponderacion for eval in ramo.evaluaciones.all())
                })

            for i in range(len(eval_names)):
                if eval_names[i] and eval_weights[i]:
                    try:
                        ponder = float(eval_weights[i])
                    except Exception:
                        ponder = 0.0
                    ponder = max(0.0, min(100.0, ponder))
                    Evaluacion.objects.create(
                        nombre=eval_names[i],
                        tipo=eval_types[i],
                        ponderacion=ponder,
                        ramo=ramo
                    )
            
            return redirect('dashboard')
        except Exception as e:
            print(f"Error al editar ramo: {e}")
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
            try:
                user = form.save()
                # Obtener o crear la carrera (si existe el campo)
                carrera_nombre = form.cleaned_data.get('carrera')
                if carrera_nombre:
                    try:
                        carrera, _ = Carrera.objects.get_or_create(
                            nombre=carrera_nombre,
                            defaults={'codigo': carrera_nombre[:3].upper()}
                        )
                        PerfilUsuario.objects.create(user=user, carrera=carrera)
                    except Exception as e:
                        # Si falla la creación del perfil, continuar igual
                        print(f"Error creando perfil: {e}")
                
                login(request, user)
                return redirect('dashboard')
            except Exception as e:
                # Agregar el error al formulario
                form.add_error(None, f"Error al crear usuario: {str(e)}")
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
            try:
                n = float(nota)
            except Exception:
                return JsonResponse({'success': False, 'error': 'Nota inválida'}, status=400)
            # Clamp nota a rango 10-70
            if n < 10: n = 10
            if n > 70: n = 70
            evaluacion.nota = n
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

