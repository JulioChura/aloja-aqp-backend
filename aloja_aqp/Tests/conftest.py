import pytest
from django.contrib.auth import get_user_model
from users.models import UserStatus
from accommodations.models import AccommodationStatus, AccommodationType, PredefinedService
from universities.models import University, UniversityCampus

User = get_user_model()

# ============= DATOS GLOBALES (usados en toda la app) =============

@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    """Crear datos base que existen en producción"""
    with django_db_blocker.unblock():
        # Estados de Accommodation
        AccommodationStatus.objects.get_or_create(name='public')
        AccommodationStatus.objects.get_or_create(name='published')
        AccommodationStatus.objects.get_or_create(name='draft')
        AccommodationStatus.objects.get_or_create(name='deleted')
        
        # Estados de User
        UserStatus.objects.get_or_create(name='active')
        
        # Tipos de Accommodation
        AccommodationType.objects.get_or_create(name='Departamento')
        AccommodationType.objects.get_or_create(name='Minidepartamento')
        AccommodationType.objects.get_or_create(name='Cuarto')
        
        # Universidades reales
        University.objects.get_or_create(
            abbreviation='UNSA',
            defaults={'name': 'Universidad Nacional de San Agustín', 'address': 'Calle Santa Catalina 117'}
        )
        University.objects.get_or_create(
            abbreviation='UCSM',
            defaults={'name': 'Universidad Católica de Santa María', 'address': 'Urb. San José'}
        )
        University.objects.get_or_create(
            abbreviation='UCSP',
            defaults={'name': 'Universidad Católica San Pablo', 'address': 'Campus Campiña Paisajista'}
        )
        University.objects.get_or_create(
            abbreviation='UC',
            defaults={'name': 'Universidad Continental', 'address': 'Av. San Martín'}
        )
        
        # Servicios predefinidos
        PredefinedService.objects.get_or_create(name='Luz')
        PredefinedService.objects.get_or_create(name='Agua')
        PredefinedService.objects.get_or_create(name='Internet')
        PredefinedService.objects.get_or_create(name='Lavanderia')

@pytest.fixture
def accommodation_statuses(db):
    return {
        'public': AccommodationStatus.objects.get(name='public'),
        'published': AccommodationStatus.objects.get(name='published'),
        'draft': AccommodationStatus.objects.get(name='draft'),
        'deleted': AccommodationStatus.objects.get(name='deleted'),
    }

@pytest.fixture
def user_status_active(db):
    return UserStatus.objects.get(name='active')

@pytest.fixture
def accommodation_types(db):
    return {
        'departamento': AccommodationType.objects.get(name='Departamento'),
        'minidepartamento': AccommodationType.objects.get(name='Minidepartamento'),
        'cuarto': AccommodationType.objects.get(name='Cuarto'),
    }

@pytest.fixture
def universities(db):
    return {
        'UNSA': University.objects.get(abbreviation='UNSA'),
        'UCSM': University.objects.get(abbreviation='UCSM'),
        'UCSP': University.objects.get(abbreviation='UCSP'),
        'UC': University.objects.get(abbreviation='UC'),
    }

@pytest.fixture
def services(db):
    return {
        'luz': PredefinedService.objects.get(name='Luz'),
        'agua': PredefinedService.objects.get(name='Agua'),
        'internet': PredefinedService.objects.get(name='Internet'),
        'lavanderia': PredefinedService.objects.get(name='Lavanderia'),
    }