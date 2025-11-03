import os
import shutil
import django

# Nombre del archivo de base de datos (ajústalo si no usas SQLite)
DB_NAME = 'db.sqlite3'

# Carpetas de tus apps donde Django crea migraciones
APPS = [
    'users',
    'universities',
    'accommodations',
    'points',
    'core'
    # agrega aquí todas tus apps con modelos
]

print(" Eliminando migraciones y base de datos...")

# 1️⃣ Borrar archivo de base de datos
if os.path.exists(DB_NAME):
    os.remove(DB_NAME)
    print(f"Base de datos '{DB_NAME}' eliminada.")
else:
    print("No se encontró la base de datos.")

# 2️⃣ Eliminar carpetas de migraciones (manteniendo __init__.py)
for app in APPS:
    migrations_path = os.path.join(app, 'migrations')
    if os.path.exists(migrations_path):
        for file in os.listdir(migrations_path):
            if file != '__init__.py' and file.endswith('.py'):
                os.remove(os.path.join(migrations_path, file))
            elif file.endswith('.pyc'):
                os.remove(os.path.join(migrations_path, file))
        print(f"Migraciones borradas en: {app}/migrations/")
    else:
        print(f" No se encontró: {app}/migrations/")

print("\n  Migraciones y base de datos eliminadas correctamente.")
print("Ahora ejecuta:")
print("python manage.py makemigrations")
print("python manage.py migrate")
