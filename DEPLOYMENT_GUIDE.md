# 🚀 Guía Completa de Deploy - Mi Promedio USS en Fly.io

**Fecha de Deploy:** 30 de Noviembre de 2025  
**Aplicación:** https://mi-promedio-uss.fly.dev  
**Base de Datos:** PostgreSQL 3GB (Plan Gratuito)  
**Región:** GRU (São Paulo, Brasil)

---

## 📋 Tabla de Contenidos

1. [Resumen del Deploy](#resumen-del-deploy)
2. [Archivos Creados y Configurados](#archivos-creados-y-configurados)
3. [Configuración Realizada](#configuración-realizada)
4. [Credenciales y Secrets](#credenciales-y-secrets)
5. [Comandos Útiles](#comandos-útiles)
6. [Actualizaciones Futuras](#actualizaciones-futuras)
7. [Troubleshooting](#troubleshooting)
8. [Optimizaciones para Plan Gratuito](#optimizaciones-para-plan-gratuito)

---

## 🎯 Resumen del Deploy

### ✅ Estado Actual
- **Estado:** ✅ DESPLEGADO Y FUNCIONANDO
- **URL Producción:** https://mi-promedio-uss.fly.dev
- **Base de Datos:** PostgreSQL conectada y migraciones ejecutadas
- **Superusuario:** Creado (usuario: `admin`)
- **Archivos Estáticos:** Configurados con WhiteNoise

### 📊 Recursos Utilizados (Plan Gratuito)
- **Máquinas VM:** 1 de 3 disponibles (shared-cpu-1x, 256MB RAM)
- **PostgreSQL:** 3GB de almacenamiento
- **Región:** GRU (São Paulo) - más cercana a Chile
- **Tráfico:** Dentro del límite de 160GB/mes

---

## 📁 Archivos Creados y Configurados

### 1. **requirements.txt**
```txt
Django==5.1.3
gunicorn==21.2.0
psycopg2-binary==2.9.9
whitenoise==6.6.0
python-decouple==3.8
dj-database-url==2.1.0
```

**Propósito:** Define todas las dependencias de Python necesarias para producción.

### 2. **runtime.txt**
```txt
python-3.12.0
```

**Propósito:** Especifica la versión de Python para Fly.io.

### 3. **Dockerfile**
```dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

EXPOSE 8080

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "mi_promedio_uss.wsgi:application"]
```

**Características:**
- Imagen ligera de Python 3.12
- Instala PostgreSQL client para conexión a BD
- Recolecta archivos estáticos automáticamente
- Ejecuta Gunicorn con 2 workers
- Optimizado para recursos mínimos

### 4. **fly.toml**
```toml
app = "mi-promedio-uss"
primary_region = "gru"

[build]

[deploy]
  release_command = "python manage.py migrate --noinput"

[env]
  PORT = "8080"

[http_service]
  internal_port = 8080
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 0
  processes = ["app"]

[[vm]]
  cpu_kind = "shared"
  cpus = 1
  memory_mb = 256
```

**Configuraciones Clave:**
- `release_command`: Ejecuta migraciones automáticamente antes de cada deploy
- `auto_stop_machines`: Apaga la máquina cuando no hay tráfico (ahorra recursos)
- `auto_start_machines`: Inicia automáticamente cuando llega una petición
- `min_machines_running = 0`: Permite apagar completamente (plan gratuito)
- `memory_mb = 256`: Memoria mínima para mantenerse en plan gratuito

### 5. **mi_promedio_uss/settings.py (Actualizado)**

#### Cambios Principales:

```python
from decouple import config, Csv
import dj_database_url

# Variables de entorno
SECRET_KEY = config('SECRET_KEY', default='...')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=Csv())

# WhiteNoise para archivos estáticos
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # ← AGREGADO
    # ... resto del middleware
]

# Base de datos dinámica (PostgreSQL en producción, SQLite en desarrollo)
if config('DATABASE_URL', default=None):
    DATABASES = {
        'default': dj_database_url.config(
            default=config('DATABASE_URL'),
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Archivos estáticos
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Seguridad en producción
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    
    CSRF_TRUSTED_ORIGINS = [
        'https://*.fly.dev',
        'https://mi-promedio-uss.fly.dev',
    ]
```

### 6. **.dockerignore**
```
*.pyc
__pycache__
*.sqlite3
db.sqlite3
.env
.git
.gitignore
venv/
.vscode/
.idea/
*.log
staticfiles/
media/
```

**Propósito:** Evita copiar archivos innecesarios al contenedor Docker (reduce tamaño de imagen).

### 7. **.gitignore**
```
*.pyc
__pycache__/
*.sqlite3
db.sqlite3
.env
venv/
staticfiles/
media/
*.log
.DS_Store
.idea/
.vscode/
```

### 8. **.env.example**
```env
DEBUG=False
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=your-app-name.fly.dev,localhost
DATABASE_URL=postgres://user:password@host:5432/database
```

**Propósito:** Template para configuración local de desarrollo.

---

## ⚙️ Configuración Realizada

### 1. Instalación de Fly.io CLI

```bash
# Instalar flyctl
curl -L https://fly.io/install.sh | sh

# Agregar al PATH
export PATH="$HOME/.fly/bin:$PATH"
echo 'export PATH="$HOME/.fly/bin:$PATH"' >> ~/.zshrc

# Verificar instalación
flyctl version
```

### 2. Autenticación

```bash
flyctl auth login
# Se abrió el navegador y se autenticó exitosamente como: subaru0.dev@gmail.com
```

### 3. Creación de la Aplicación

```bash
flyctl apps create mi-promedio-uss
```

**Resultado:** App creada en la organización personal.

### 4. Creación de PostgreSQL

```bash
flyctl postgres create --name mi-promedio-uss-db \
  --region gru \
  --initial-cluster-size 1 \
  --vm-size shared-cpu-1x \
  --volume-size 3
```

**Credenciales Generadas:**
- **Username:** `postgres`
- **Password:** `hoI8hee9nxYJMxB`
- **Hostname:** `mi-promedio-uss-db.internal`
- **Port:** `5432`
- **Connection String:** `postgres://postgres:hoI8hee9nxYJMxB@mi-promedio-uss-db.flycast:5432`

⚠️ **IMPORTANTE:** Estas credenciales se generaron automáticamente y no se pueden recuperar después. Ya están guardadas en los secrets de la app.

### 5. Conexión de la Base de Datos

```bash
flyctl postgres attach --app mi-promedio-uss mi-promedio-uss-db
```

**Resultado:** 
- Base de datos `mi_promedio_uss` creada
- Usuario `mi_promedio_uss` creado
- Variable `DATABASE_URL` agregada automáticamente a los secrets

---

## 🔐 Credenciales y Secrets

### Variables de Entorno Configuradas

```bash
# SECRET_KEY generado con Django
flyctl secrets set SECRET_KEY="js74(sec$)9n5k9#wc_0y(%q%hf$o22$=(&pdf$n9vz1a6lbng" -a mi-promedio-uss

# DEBUG en False para producción
flyctl secrets set DEBUG=False -a mi-promedio-uss

# ALLOWED_HOSTS
flyctl secrets set ALLOWED_HOSTS="mi-promedio-uss.fly.dev" -a mi-promedio-uss
```

### Verificar Secrets

```bash
flyctl secrets list -a mi-promedio-uss
```

**Secrets Configurados:**
- ✅ `DATABASE_URL` (configurado automáticamente al conectar PostgreSQL)
- ✅ `SECRET_KEY` (generado con Django)
- ✅ `DEBUG` (False)
- ✅ `ALLOWED_HOSTS` (mi-promedio-uss.fly.dev)

### Credenciales del Superusuario

**Usuario Admin Django:**
- **Username:** `admin`
- **Password:** `admin123USS`
- **Email:** `admin@example.com`

**Acceso:** https://mi-promedio-uss.fly.dev/admin/

---

## 🛠️ Comandos Útiles

### Deploy y Actualizaciones

```bash
# Deploy completo
flyctl deploy

# Deploy sin health checks
flyctl deploy --ha=false

# Ver estado de la aplicación
flyctl status -a mi-promedio-uss

# Ver información de la app
flyctl info -a mi-promedio-uss
```

### Logs y Debugging

```bash
# Ver logs en tiempo real
flyctl logs -a mi-promedio-uss

# Ver logs históricos
flyctl logs -a mi-promedio-uss --history

# Ver últimas 100 líneas
flyctl logs -a mi-promedio-uss | tail -100
```

### SSH y Consola

```bash
# Conectar a la consola SSH
flyctl ssh console -a mi-promedio-uss

# Ejecutar comando remoto
flyctl ssh console -a mi-promedio-uss -C "python manage.py migrate"

# Shell de Django
flyctl ssh console -a mi-promedio-uss -C "python manage.py shell"
```

### Base de Datos

```bash
# Ver bases de datos
flyctl postgres db list -a mi-promedio-uss-db

# Conectar a PostgreSQL
flyctl postgres connect -a mi-promedio-uss-db

# Ejecutar migraciones
flyctl ssh console -a mi-promedio-uss -C "python manage.py migrate"

# Ver estado de migraciones
flyctl ssh console -a mi-promedio-uss -C "python manage.py showmigrations"
```

### Gestión de Máquinas

```bash
# Listar máquinas
flyctl machine list -a mi-promedio-uss

# Reiniciar app
flyctl apps restart mi-promedio-uss

# Detener máquina
flyctl machine stop <MACHINE_ID> -a mi-promedio-uss

# Iniciar máquina
flyctl machine start <MACHINE_ID> -a mi-promedio-uss
```

### Secrets y Variables

```bash
# Listar secrets
flyctl secrets list -a mi-promedio-uss

# Agregar nuevo secret
flyctl secrets set NUEVA_VARIABLE="valor" -a mi-promedio-uss

# Eliminar secret
flyctl secrets unset VARIABLE -a mi-promedio-uss
```

### Releases y Rollback

```bash
# Ver releases
flyctl releases -a mi-promedio-uss

# Rollback a versión anterior
flyctl releases rollback -a mi-promedio-uss
```

### Abrir en Navegador

```bash
# Abrir app en navegador
flyctl apps open -a mi-promedio-uss

# Abrir dashboard
flyctl dashboard -a mi-promedio-uss
```

---

## 🔄 Actualizaciones Futuras

### Proceso de Actualización

1. **Hacer cambios en el código localmente**
2. **Probar localmente**
   ```bash
   python manage.py runserver
   ```

3. **Commit a git (opcional pero recomendado)**
   ```bash
   git add .
   git commit -m "Descripción de cambios"
   git push
   ```

4. **Deployar a Fly.io**
   ```bash
   flyctl deploy
   ```
   Las migraciones se ejecutan automáticamente gracias a `release_command` en `fly.toml`.

5. **Verificar**
   ```bash
   flyctl logs -a mi-promedio-uss
   flyctl status -a mi-promedio-uss
   ```

### Agregar Nuevas Migraciones

```bash
# Crear migraciones localmente
python manage.py makemigrations

# Deploy (las migraciones se ejecutan automáticamente)
flyctl deploy

# O ejecutarlas manualmente si es necesario
flyctl ssh console -a mi-promedio-uss -C "python manage.py migrate"
```

### Actualizar Dependencias

1. Actualizar `requirements.txt`
2. Deploy:
   ```bash
   flyctl deploy
   ```

### Agregar Nuevas Variables de Entorno

```bash
flyctl secrets set NUEVA_VARIABLE="valor" -a mi-promedio-uss
```

---

## 🐛 Troubleshooting

### Problema: App no responde (503/502)

**Solución:**
```bash
# Ver logs
flyctl logs -a mi-promedio-uss

# Verificar estado
flyctl status -a mi-promedio-uss

# Reiniciar
flyctl apps restart mi-promedio-uss
```

### Problema: Error de base de datos

**Solución:**
```bash
# Verificar conexión
flyctl ssh console -a mi-promedio-uss -C "python manage.py dbshell"

# Verificar migraciones
flyctl ssh console -a mi-promedio-uss -C "python manage.py showmigrations"

# Ejecutar migraciones
flyctl ssh console -a mi-promedio-uss -C "python manage.py migrate"
```

### Problema: Archivos estáticos no cargan

**Solución:**
```bash
# Verificar STATIC_ROOT
flyctl ssh console -a mi-promedio-uss -C "ls -la /app/staticfiles/"

# Recolectar estáticos manualmente
flyctl ssh console -a mi-promedio-uss -C "python manage.py collectstatic --noinput"
```

### Problema: Cold Start lento (primera petición demora)

**Explicación:** Cuando la app está detenida (auto_stop_machines), la primera petición tarda 10-15 segundos mientras la máquina se inicia.

**Soluciones:**
- Mantener al menos 1 máquina corriendo:
  ```toml
  # En fly.toml
  min_machines_running = 1
  ```
  ⚠️ Esto consume recursos continuamente.

- O simplemente aceptar el cold start (recomendado para plan gratuito).

### Problema: Error CSRF

**Solución:** Verificar que el dominio esté en `CSRF_TRUSTED_ORIGINS`:
```python
# En settings.py
CSRF_TRUSTED_ORIGINS = [
    'https://*.fly.dev',
    'https://mi-promedio-uss.fly.dev',
]
```

### Problema: Error de memoria (OOM)

**Solución:** Aumentar memoria temporalmente:
```bash
flyctl scale memory 512 -a mi-promedio-uss
```
⚠️ Esto puede salirse del plan gratuito si se mantiene permanentemente.

---

## 💰 Optimizaciones para Plan Gratuito

### Configuraciones Actuales

✅ **Auto-stop habilitado:** La app se apaga cuando no hay tráfico  
✅ **Min machines = 0:** Permite apagar completamente  
✅ **Memory = 256MB:** Mínimo necesario  
✅ **1 worker de Gunicorn:** Reduce uso de memoria  
✅ **Sin health checks:** Evita despertar la app innecesariamente

### Monitorear Uso

```bash
# Dashboard web
flyctl dashboard -a mi-promedio-uss

# Ver uso actual
flyctl status -a mi-promedio-uss

# Ver máquinas
flyctl machine list -a mi-promedio-uss
```

### Límites del Plan Gratuito

- **3 VMs pequeñas** (shared-cpu-1x, 256MB cada una)
- **3GB PostgreSQL**
- **160GB tráfico saliente/mes**
- **Certificados SSL gratuitos**

### Tips para Mantenerse Gratis

1. ✅ Mantener solo 1 máquina corriendo
2. ✅ Usar auto-stop cuando sea posible
3. ✅ Mantener memoria en 256MB
4. ✅ Optimizar consultas a base de datos
5. ✅ Comprimir imágenes y assets estáticos
6. ✅ Usar caché de Django cuando sea posible

---

## 📊 Información de la Infraestructura

### Aplicación Django

- **Nombre:** mi-promedio-uss
- **URL:** https://mi-promedio-uss.fly.dev
- **Región:** GRU (São Paulo, Brasil)
- **IP IPv6:** `2a09:8280:1::b5:d05a:0`
- **IP IPv4 compartida:** `66.241.124.187`

### Base de Datos PostgreSQL

- **Nombre:** mi-promedio-uss-db
- **Base de datos:** mi_promedio_uss
- **Versión:** PostgreSQL 17.2
- **Región:** GRU
- **Volumen:** 3GB
- **Usuario:** mi_promedio_uss (creado automáticamente)

### Máquina Virtual

- **ID:** 3287e353c52558
- **Tipo:** shared-cpu-1x
- **CPUs:** 1
- **RAM:** 256MB
- **Región:** GRU
- **Estado:** Started (puede auto-stop)

---

## 🎓 Checklist de Verificación

### ✅ Deploy Inicial Completado

- [x] Archivos de configuración creados
- [x] Dockerfile optimizado
- [x] fly.toml configurado
- [x] settings.py actualizado para producción
- [x] Fly.io CLI instalado
- [x] Autenticado en Fly.io
- [x] Aplicación creada
- [x] PostgreSQL creado y conectado
- [x] Variables de entorno configuradas
- [x] Deploy ejecutado exitosamente
- [x] Migraciones ejecutadas
- [x] Superusuario creado
- [x] App accesible en https://mi-promedio-uss.fly.dev

### 🔍 Verificación Post-Deploy

- [x] Login de admin funciona
- [x] Archivos estáticos cargan correctamente
- [x] HTTPS habilitado
- [x] Base de datos PostgreSQL conectada
- [x] Migraciones aplicadas

### 📝 Próximos Pasos Recomendados

- [ ] Probar todas las funcionalidades de la app
- [ ] Crear algunos datos de prueba
- [ ] Verificar cálculo de promedios
- [ ] Probar desde dispositivo móvil
- [ ] Configurar dominio personalizado (opcional)
- [ ] Configurar backups de base de datos (opcional)

---

## 📞 Recursos y Soporte

### Documentación Oficial

- **Fly.io Docs:** https://fly.io/docs/
- **Django Deployment:** https://docs.djangoproject.com/en/5.0/howto/deployment/
- **WhiteNoise:** http://whitenoise.evans.io/

### Enlaces Útiles

- **Dashboard Fly.io:** https://fly.io/dashboard/javier-morales-subaru
- **App Monitoring:** https://fly.io/apps/mi-promedio-uss/monitoring
- **PostgreSQL Dashboard:** https://fly.io/apps/mi-promedio-uss-db

### Comandos de Emergencia

```bash
# Si algo sale mal, rollback rápido
flyctl releases rollback -a mi-promedio-uss

# Si la app no responde, reiniciar
flyctl apps restart mi-promedio-uss

# Si necesitas debuggear, SSH
flyctl ssh console -a mi-promedio-uss

# Ver logs en tiempo real
flyctl logs -a mi-promedio-uss
```

---

## 🎉 ¡Deploy Exitoso!

Tu aplicación **Mi Promedio USS** está ahora desplegada y funcionando en:

🌐 **https://mi-promedio-uss.fly.dev**

### Credenciales de Acceso

👤 **Admin:**
- Usuario: `admin`
- Contraseña: `admin123USS`
- URL Admin: https://mi-promedio-uss.fly.dev/admin/

---

**Última actualización:** 30 de Noviembre de 2025  
**Versión:** 1.0  
**Deploy por:** Subaru Dev (GitHub Copilot)
