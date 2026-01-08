# Guía rápida para instalar y configurar Celery + Redis en Windows

## 1. Instalar Redis

Redis es el broker recomendado para Celery. En Windows, puedes instalarlo así:

### Opción fácil (usando Docker)
Si tienes Docker instalado:
```
docker run -d -p 6379:6379 --name redis redis
```

### Opción manual (sin Docker)
1. Descarga Redis para Windows desde: https://github.com/microsoftarchive/redis/releases
2. Extrae y ejecuta `redis-server.exe`.

## 2. Instalar dependencias en tu entorno Python

```
pip install celery redis
```

## 3. Configurar Celery en Django

En tu archivo `settings.py` agrega:
```python
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
```

## 4. Ejecutar los servicios

- Inicia Redis (Docker o ejecutando `redis-server.exe`).
- Inicia el worker de Celery:
```
celery -A aloja_aqp worker --loglevel=info
```
- Inicia tu servidor Django normalmente:
```
python manage.py runserver
```

## 5. Probar que funciona

Crea o edita una propiedad desde la API/admin. Verifica en la consola del worker Celery que se ejecuta la tarea.

---
Si tienes dudas, dime en qué paso te quedaste y te ayudo.