# 🚀 Deploy Rápido - Mi Promedio USS

## 📌 Información Esencial

- **URL:** https://mi-promedio-uss.fly.dev
- **Admin:** https://mi-promedio-uss.fly.dev/admin/
- **Usuario:** `admin` | **Password:** `admin123USS`

## 🔧 Comandos Más Usados

```bash
# Deploy
flyctl deploy

# Logs
flyctl logs -a mi-promedio-uss

# Estado
flyctl status -a mi-promedio-uss

# SSH
flyctl ssh console -a mi-promedio-uss

# Migraciones
flyctl ssh console -a mi-promedio-uss -C "python manage.py migrate"

# Reiniciar
flyctl apps restart mi-promedio-uss
```

## 📂 Archivos Importantes

- `Dockerfile` - Configuración del contenedor
- `fly.toml` - Configuración de Fly.io
- `requirements.txt` - Dependencias Python
- `mi_promedio_uss/settings.py` - Settings de producción
- `DEPLOYMENT_GUIDE.md` - **Documentación completa** ⭐

## 🔐 Secrets Configurados

```bash
flyctl secrets list -a mi-promedio-uss
```

- `DATABASE_URL` - PostgreSQL connection
- `SECRET_KEY` - Django secret
- `DEBUG` - False en producción
- `ALLOWED_HOSTS` - mi-promedio-uss.fly.dev

## 📊 Base de Datos

- **PostgreSQL:** mi-promedio-uss-db
- **Tamaño:** 3GB (plan gratuito)
- **Región:** GRU (São Paulo)

```bash
# Conectar a PostgreSQL
flyctl postgres connect -a mi-promedio-uss-db
```

## 🆘 Troubleshooting Rápido

### App no responde
```bash
flyctl logs -a mi-promedio-uss
flyctl apps restart mi-promedio-uss
```

### Problemas con estáticos
```bash
flyctl ssh console -a mi-promedio-uss -C "python manage.py collectstatic --noinput"
```

### Rollback
```bash
flyctl releases rollback -a mi-promedio-uss
```

## 📖 Documentación Completa

Ver `DEPLOYMENT_GUIDE.md` para instrucciones detalladas, configuraciones y troubleshooting completo.
