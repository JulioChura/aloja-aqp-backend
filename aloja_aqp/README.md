## Diagrama de la base de datos

Puedes visualizar el modelo entidad-relación de la base de datos en la siguiente imagen:

![Diagrama ER](docs/diagrama_bd.png)

# AlojaAQP Backend

AlojaAQP es una plataforma backend desarrollada en Django y Django REST Framework para la gestión de alojamientos universitarios en Arequipa, Perú. Permite a estudiantes buscar, filtrar y reservar alojamientos cercanos a universidades, así como a propietarios publicar y administrar sus propiedades.

## Características principales
- **Gestión de alojamientos**: Publicación, edición, ocultamiento y borrado lógico de alojamientos.
- **Búsqueda avanzada**: Filtros por precio, habitaciones, servicios, cercanía a universidades/campus y búsqueda por texto.
- **Gestión de usuarios**: Registro y autenticación de estudiantes y propietarios (con validación de DNI vía RENIEC y Google Login).
- **Reseñas y favoritos**: Los estudiantes pueden dejar reseñas y marcar alojamientos como favoritos.
- **Servicios y lugares cercanos**: Relación de alojamientos con servicios y puntos de interés cercanos.
- **Carga de fotos en Cloudinary**.
- **Documentación automática de la API** con Swagger y Redoc.

## Estructura de carpetas
- `accommodations/`: Lógica de alojamientos, servicios, distancias, fotos, reseñas, favoritos.
- `users/`: Modelos y vistas de usuarios, perfiles de estudiante y propietario, autenticación.
- `universities/`: Universidades y campus.
- `core/`: Base para futuras extensiones.

## Modelos principales
- **User, OwnerProfile, StudentProfile**: Usuarios y sus perfiles.
- **Accommodation, AccommodationType, AccommodationStatus**: Alojamientos y su tipología.
- **PredefinedService, AccommodationService**: Servicios disponibles en los alojamientos.
- **University, UniversityCampus, UniversityDistance**: Universidades, campus y distancias a alojamientos.
- **Review, Favorite**: Reseñas y favoritos de estudiantes.

## Variables de entorno necesarias (`.env`)
- `CLOUDINARY_CLOUD_NAME`
- `CLOUDINARY_API_KEY`
- `CLOUDINARY_API_SECRET`
- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `DECOLECTA_API_KEY`
- `MAPBOX_ACCESS_TOKEN`

## Instalación y ejecución local

### 1. Clonar el repositorio y ubicarse en la carpeta del backend

```bash
cd aloja-aqp-backend/aloja_aqp
```

### 2. Crear y configurar el archivo `.env`
Copia el archivo `.env.example` (si existe) o crea uno nuevo con las variables listadas arriba.

### 3. Construir y levantar los servicios con Docker

```bash
docker-compose up --build
```
Esto levantará:
- Backend Django en http://localhost:8000
- Base de datos PostgreSQL en localhost:5432
- PgAdmin para administración de la base de datos

### 4. Acceso a la API y documentación
- Swagger: http://localhost:8000/docs/
- Redoc: http://localhost:8000/redoc/


## Carga de datos iniciales obligatorios

Para que el sistema funcione correctamente, debes cargar los estados de publicación de alojamientos (draft, published, hidden, deleted). Ejecuta el siguiente comando:

```bash
docker-compose exec backend python manage.py cargar_estados_alojamiento
```

## Comandos útiles
- Migraciones: `docker-compose exec backend python manage.py migrate`
- Crear superusuario: `docker-compose exec backend python manage.py createsuperuser`
- Ejecutar tests: `docker-compose exec backend pytest`



## Dependencias principales
Ver `requirements.txt` para la lista completa. Destacan:
- Django 5.2+
- djangorestframework
- djangorestframework-simplejwt
- django-allauth
- cloudinary
- psycopg2-binary
- celery (para tareas asíncronas, si se usan)

## Licencia
MIT

---

> Generado automáticamente por GitHub Copilot a partir del análisis del código y configuración del proyecto.
