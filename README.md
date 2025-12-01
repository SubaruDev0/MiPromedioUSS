# MiPromedioUSS

MiPromedioUSS es una aplicación web (Django) pensada para estudiantes que quieren gestionar sus ramos y calcular promedios de forma práctica y confiable. Incluye una calculadora rápida y calculadoras por ramo con soporte para repete (examen de recuperación), historial organizado por año y semestre, y persistencia de notas y metas.

---

## Características principales

- Calculadora rápida: calcula promedio con varias evaluaciones y muestra si se alcanza la nota objetivo.
- Calculadora por ramo: misma lógica que la rápida (con sección Repete, modos de reemplazo y mensaje de resultado).
- Guardado automático de notas por evaluación (AJAX).
- Guardado persistente de la nota objetivo por ramo.
- Gestión de ramos: crear, editar (agregar/eliminar evaluaciones, talleres, parciales, solemnes), eliminar.
- Históricos organizados por Año -> Semestre -> Ramos con promedios por semestre y por año.
- Soporta hasta 10 años académicos (Primer año … Décimo año).
- Interfaz y mensajes en español.

---

## Escalas y convención de notas

- Las evaluaciones y la entrada del usuario se manejan en escala 10–70 (más intuitiva para ingresar notas).
- El campo `Ramo.nota_objetivo` se almacena internamente en escala 1–7 (por ejemplo `3.95` ≈ `39.5` en escala 10–70). La app hace la conversión al mostrar/guardar.
- Los cálculos intermedios y la lógica de repete trabajan con la escala 10–70 para evitar confusiones visuales.

---

## Requisitos

- Python 3.10+ (probado con 3.12)
- Django 5.x (u otra 5.x compatible)
- sqlite3 (incluido por defecto)

---

## Instalación rápida (local)

1. Clona el repo:

```bash
git clone <url-del-repo> MiPromedioUSS
cd MiPromedioUSS
```

2. Crear y activar virtualenv (ejemplo unix/zsh):

```bash
python -m venv venv
source venv/bin/activate
```

3. Instalar dependencias (si tienes `requirements.txt`):

```bash
pip install -r requirements.txt
# si no existe requirements.txt al menos instala Django
pip install django
```

4. Migraciones y datos iniciales:

```bash
python manage.py migrate
```

5. Crear superusuario (opcional):

```bash
python manage.py createsuperuser
```

6. Ejecutar servidor de desarrollo:

```bash
python manage.py runserver
# abrir http://127.0.0.1:8000/
```

---

## Flujo rápido de uso

- Crear Ramo: `Nuevo Ramo` → nombre, año, semestre, asistencia → agregar evaluaciones (Solemne / Parciales / Talleres) con porcentajes.
- En `Mis Notas` (Periodo actual): editar notas directamente en las tarjetas (se guardan automáticamente).
- Si tu promedio es menor que la nota objetivo aparece la sección de Repete (ingresas la nota de repete y eliges modo de reemplazo). Se calcula Promedio Final y se muestra si pasaste o no.
- `Históricas`: los ramos de periodos anteriores aparecen organizados por Año → Semestre; desde ahí puedes también editar notas o abrir el editor del ramo.

---

## Endpoints AJAX importantes

- `POST /save_grade/<evaluacion_id>/` — guardar nota de una evaluación (JSON: `{ "nota": "45" }`).
- `POST /delete_evaluacion/<evaluacion_id>/` — eliminar evaluación.
- `POST /save_nota_objetivo/<ramo_id>/` — guardar nota objetivo del ramo (JSON: `{ "nota_objetivo": 65 }` en escala 10-70).

> En las llamadas AJAX el token CSRF se incluye desde las plantillas.

---

## Notas de desarrollo y decisiones relevantes

- Las ponderaciones de parciales/talleres se distribuyen en centésimos para que la suma total sea exacta (ej.: 6.66 / 6.67 / 6.67).
- El orden de evaluación por defecto está pensado para mostrar primero las solemnes, luego controles/laboratorios/proyectos y finalmente talleres/otros.
- El dashboard determina el período "actual" en base al ramo más reciente (año + semestre) y marca lo demás como históricos. Los históricos se agrupan por año y dentro de cada año por semestre.
- Los promedios se calculan en tres niveles: promedio del ramo (ponderado por evaluaciones), promedio por semestre (promedio de promedios de ramos), promedio por año (promedio de promedios de semestres).

---

## Tests y validación rápida

- Ejecuta `python manage.py check` para verificar configuración y advertencias de Django.
- Pruebas manuales recomendadas:
  - Crear un ramo con evaluaciones que sumen 100% y comprobar guardado.
  - Editar notas en `Mis Notas` y confirmar que se guardan y recalculan.
  - Probar flujo de Repete con ambos modos de reemplazo.

---

## Roadmap / Ideas futuras

- Tests automáticos (unitarios e integración).
- Exportar histórico a CSV/PDF.
- Mejorar accesibilidad (labels) y añadir internacionalización (i18n).
- Mejorar UI/UX y agregar dark mode.

---

## Contribuir

1. Haz fork y crea una rama por feature/bugfix.
2. Abre un Pull Request con descripción clara.
3. Ejecuta `makemigrations` y `migrate` si cambias modelos.

---

## Licencia

Este proyecto no incluye licencia por defecto. Si lo deseas añade un `LICENSE` (ej. MIT) según prefieras.

---

Si quieres que lo cree en el repo ahora, lo agrego (o ajusto el contenido a tu público: más técnico, más corto, con badges, etc.).

