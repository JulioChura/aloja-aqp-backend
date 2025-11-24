import pytest
from django.contrib.auth import get_user_model
from accommodations.models import (
    Accommodation, AccommodationStatus, AccommodationType,
    UniversityDistance, PredefinedService, AccommodationService
)
from users.models import OwnerProfile, StudentProfile, UserStatus
from universities.models import University, UniversityCampus

User = get_user_model()

@pytest.fixture
def accommodation_statuses(db):
    draft, _ = AccommodationStatus.objects.get_or_create(name='draft')
    published, _ = AccommodationStatus.objects.get_or_create(name='published')
    hidden, _ = AccommodationStatus.objects.get_or_create(name='hidden')
    deleted, _ = AccommodationStatus.objects.get_or_create(name='deleted')
    return {'draft': draft, 'published': published, 'hidden': hidden, 'deleted': deleted}

@pytest.fixture
def user_statuses(db):
    active, _ = UserStatus.objects.get_or_create(name='active')
    inactive, _ = UserStatus.objects.get_or_create(name='inactive')
    return {'active': active, 'inactive': inactive}

@pytest.fixture
def accommodation_type(db):
    acc_type, _ = AccommodationType.objects.get_or_create(
        name='Departamento',
        defaults={'description': 'Departamento completo'}
    )
    return acc_type

@pytest.fixture
def owner_user(db, user_statuses):
    user = User.objects.create_user(
        email='owner@test.com',
        password='testpass123',
        first_name='Owner',
        last_name='Test'
    )
    owner = OwnerProfile.objects.create(
        user=user,
        dni='12345678',
        phone_number='987654321',
        verified=True,
        status=user_statuses['active']
    )
    return owner

@pytest.fixture
def student_user(db, user_statuses):
    user = User.objects.create_user(
        email='student@test.com',
        password='testpass123',
        first_name='Student',
        last_name='Test'
    )
    student = StudentProfile.objects.create(
        user=user,
        phone_number='912345678',
        status=user_statuses['active']
    )
    return student

@pytest.fixture
def university(db):
    univ, _ = University.objects.get_or_create(
        abbreviation='UNSA',
        defaults={
            'name': 'Universidad Nacional de San Agustín',
            'address': 'Calle Santa Catalina 117'
        }
    )
    return univ

@pytest.fixture
def campus(db, university):
    campus, _ = UniversityCampus.objects.get_or_create(
        university=university,
        name='Campus Central',
        defaults={
            'address': 'Calle Santa Catalina 117',
            'latitude': -16.3988,
            'longitude': -71.5350
        }
    )
    return campus

@pytest.fixture
def accommodations(db, owner_user, accommodation_type, accommodation_statuses):
    acc1 = Accommodation.objects.create(
        owner=owner_user,
        title='Departamento cerca UNSA',
        description='Departamento amoblado',
        accommodation_type=accommodation_type,
        address='Calle Arequipa 123',
        latitude=-16.3990,
        longitude=-71.5352,
        monthly_price=800.00,
        rooms=2,
        status=accommodation_statuses['published']
    )
    acc2 = Accommodation.objects.create(
        owner=owner_user,
        title='Habitación económica',
        description='Habitación para estudiante',
        accommodation_type=accommodation_type,
        address='Av. Ejército 456',
        latitude=-16.4000,
        longitude=-71.5360,
        monthly_price=400.00,
        rooms=1,
        status=accommodation_statuses['published']
    )
    acc3 = Accommodation.objects.create(
        owner=owner_user,
        title='Departamento Premium',
        description='Lujoso departamento',
        accommodation_type=accommodation_type,
        address='Calle Moral 789',
        latitude=-16.3980,
        longitude=-71.5340,
        monthly_price=1500.00,
        rooms=3,
        status=accommodation_statuses['published']
    )
    return [acc1, acc2, acc3]

@pytest.fixture
def university_distances(db, accommodations, campus):
    distances = []
    for idx, acc in enumerate(accommodations):
        dist = UniversityDistance.objects.create(
            accommodation=acc,
            campus=campus,
            distance_km=0.5 + (idx * 0.3),
            walk_time_minutes=10 + (idx * 5),
            bus_time_minutes=5 + (idx * 2)
        )
        distances.append(dist)
    return distances

@pytest.fixture
def services(db):
    wifi, _ = PredefinedService.objects.get_or_create(name='WiFi', defaults={'icon_class': 'fa-wifi'})
    parking, _ = PredefinedService.objects.get_or_create(name='Estacionamiento', defaults={'icon_class': 'fa-car'})
    laundry, _ = PredefinedService.objects.get_or_create(name='Lavandería', defaults={'icon_class': 'fa-tshirt'})
    return {'wifi': wifi, 'parking': parking, 'laundry': laundry}