"""
Fixtures y configuración base para las pruebas de accommodations.
Este módulo contiene las clases base y métodos para crear datos de prueba.
"""
from django.test import TestCase
from decimal import Decimal
from accommodations.models import (
    Accommodation, AccommodationStatus, AccommodationType,
    UniversityDistance, PredefinedService, AccommodationService
)
from users.models import OwnerProfile, UserStatus, User
from universities.models import University, UniversityCampus


class AccommodationTestBase(TestCase):
    """Clase base con configuración común para todas las pruebas de accommodations"""

    def setUp(self):
        """Configuración inicial: crear estados, tipos, propietario y universidad"""
        # Crear estados de alojamiento
        self.status_published = AccommodationStatus.objects.create(name='published')
        self.status_draft = AccommodationStatus.objects.create(name='draft')
        self.status_hidden = AccommodationStatus.objects.create(name='hidden')
        self.status_deleted = AccommodationStatus.objects.create(name='deleted')

        # Crear estados de usuario
        self.user_status_active = UserStatus.objects.create(name='active')
        self.user_status_inactive = UserStatus.objects.create(name='inactive')

        # Crear tipos de alojamiento
        self.accommodation_type_dept = AccommodationType.objects.create(
            name='Departamento',
            description='Departamento completo'
        )
        self.tipo_departamento = self.accommodation_type_dept  # Alias para claridad

        self.accommodation_type_room = AccommodationType.objects.create(
            name='Cuarto',
            description='Habitación individual'
        )
        self.tipo_cuarto = self.accommodation_type_room  # Alias para claridad

        self.accommodation_type_mini = AccommodationType.objects.create(
            name='Minidepartamento',
            description='Minidepartamento'
        )

        # Crear propietario
        self.owner = self.create_owner_profile(
            email='owner@test.com',
            dni='12345678',
            first_name='Owner',
            last_name='Test'
        )

        # Crear universidades y campus
        self.unsa = self.create_university('UNSA', 'Universidad Nacional de San Agustín')
        self.campus_unsa = self.create_campus(
            university=self.unsa,
            name='Campus Ingeniería',
            latitude=-16.3988,
            longitude=-71.5350
        )

        self.ucsm = self.create_university('UCSM', 'Universidad Católica de Santa María')
        self.campus_ucsm = self.create_campus(
            university=self.ucsm,
            name='Campus Principal',
            latitude=-16.4050,
            longitude=-71.5300
        )

        # Crear servicios predefinidos
        self.service_wifi = PredefinedService.objects.create(
            name='WiFi',
            icon_class='fa-wifi'
        )
        self.servicio_wifi = self.service_wifi  # Alias para claridad

        self.service_parking = PredefinedService.objects.create(
            name='Estacionamiento',
            icon_class='fa-car'
        )
        
        self.service_laundry = PredefinedService.objects.create(
            name='Lavandería',
            icon_class='fa-tshirt'
        )

        # Servicio adicional para pruebas de múltiples filtros
        self.service_water = PredefinedService.objects.create(
            name='Agua',
            icon_class='fa-water'
        )
        self.servicio_agua = self.service_water  # Alias para claridad
        

    def create_owner_profile(self, email, dni, first_name='Test', last_name='Owner'):
        """Helper para crear un perfil de propietario"""
        user = User.objects.create_user(
            email=email,
            password='testpass123',
            first_name=first_name,
            last_name=last_name
        )
        owner = OwnerProfile.objects.create(
            user=user,
            dni=dni,
            phone_number='987654321',
            verified=True,
            status=self.user_status_active
        )
        return owner

    def create_university(self, abbreviation, name, address='Dirección de prueba'):
        """Helper para crear una universidad"""
        university, _ = University.objects.get_or_create(
            abbreviation=abbreviation,
            defaults={
                'name': name,
                'address': address
            }
        )
        return university

    def create_campus(self, university, name, latitude, longitude, address='Campus address'):
        """Helper para crear un campus universitario"""
        campus, _ = UniversityCampus.objects.get_or_create(
            university=university,
            name=name,
            defaults={
                'address': address,
                'latitude': latitude,
                'longitude': longitude
            }
        )
        return campus

    def create_accommodation(self, title, price, rooms=1, status=None, 
                           accommodation_type=None, owner=None, **kwargs):
        """
        Helper para crear un alojamiento con parámetros personalizables.
        
        Args:
            title: Título del alojamiento
            price: Precio mensual (Decimal o str)
            rooms: Número de habitaciones (default: 1)
            status: Estado del alojamiento (default: self.status_published)
            accommodation_type: Tipo (default: self.accommodation_type_dept)
            owner: Propietario (default: self.owner)
            **kwargs: Parámetros adicionales (address, latitude, longitude, etc.)
        """
        if status is None:
            status = self.status_published
        if accommodation_type is None:
            accommodation_type = self.accommodation_type_dept
        if owner is None:
            owner = self.owner

        defaults = {
            'address': kwargs.get('address', f'Dirección {title}'),
            'latitude': kwargs.get('latitude', -16.4000),
            'longitude': kwargs.get('longitude', -71.5350),
            'description': kwargs.get('description', f'Descripción de {title}'),
        }

        accommodation = Accommodation.objects.create(
            owner=owner,
            title=title,
            accommodation_type=accommodation_type,
            monthly_price=Decimal(str(price)),
            rooms=rooms,
            status=status,
            **defaults
        )
        return accommodation

    def create_university_distance(self, accommodation, campus, distance_km, 
                                  walk_time=None, bus_time=None):
        """
        Helper para crear una distancia a universidad.
        
        Args:
            accommodation: Instancia de Accommodation
            campus: Instancia de UniversityCampus
            distance_km: Distancia en kilómetros (Decimal o str)
            walk_time: Tiempo caminando en minutos (opcional)
            bus_time: Tiempo en bus en minutos (opcional)
        """
        # Usar get_or_create para evitar duplicados
        distance, created = UniversityDistance.objects.get_or_create(
            accommodation=accommodation,
            campus=campus,
            defaults={
                'distance_km': Decimal(str(distance_km)),
                'walk_time_minutes': walk_time,
                'bus_time_minutes': bus_time
            }
        )
        # Si ya existía, actualizar los valores
        if not created:
            distance.distance_km = Decimal(str(distance_km))
            distance.walk_time_minutes = walk_time
            distance.bus_time_minutes = bus_time
            distance.save()
        return distance

    def create_accommodation_with_distance(self, title, price, campus, distance_km,
                                          walk_time=None, bus_time=None, **kwargs):
        """
        Helper para crear un alojamiento con su distancia a un campus en un solo paso.
        
        Args:
            title: Título del alojamiento
            price: Precio mensual
            campus: Campus universitario
            distance_km: Distancia en km
            walk_time: Tiempo caminando (opcional)
            bus_time: Tiempo en bus (opcional)
            **kwargs: Parámetros adicionales para create_accommodation
        """
        accommodation = self.create_accommodation(title, price, **kwargs)
        self.create_university_distance(
            accommodation, campus, distance_km, walk_time, bus_time
        )
        return accommodation

    def add_service_to_accommodation(self, accommodation, service, detail=''):
        """Helper para agregar un servicio a un alojamiento"""
        return AccommodationService.objects.create(
            accommodation=accommodation,
            service=service,
            detail=detail
        )
