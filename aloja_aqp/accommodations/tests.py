from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from users.models import User, UserStatus, OwnerProfile, StudentProfile
from universities.models import University, UniversityCampus
from .models import Accommodation, AccommodationStatus, AccommodationType, Favorite, UniversityDistance, PredefinedService, AccommodationService

class AccommodationManagementTests(APITestCase):
    """
    PU003: GESTIÓN DE ANUNCIOS (PROPIETARIOS)
    -------------------------------------------------------------------
    Objetivo: Verificar el ciclo de vida: Creación (Draft) -> Publicación -> Edición.
    También verificamos el guardado masivo de distancias (Bulk).
    """

    def setUp(self):
        # --- 1. CONFIGURACIÓN DE DATOS MAESTROS (Status y Types) ---
        self.status_draft = AccommodationStatus.objects.create(name="draft")
        self.status_published = AccommodationStatus.objects.create(name="published")
        self.type_apartment = AccommodationType.objects.create(name="Departamento")

        # --- 2. CREACIÓN DE USUARIO PROPIETARIO ---
        self.owner_user = User.objects.create_user(email='propietario@test.com', password='password123')
        self.owner_profile = OwnerProfile.objects.create(
            user=self.owner_user, 
            dni='88888888', 
            status=UserStatus.objects.create(name='active')
        )

        # --- 3. CREACIÓN DE UNIVERSIDAD (Para pruebas de distancia) ---
        self.uni = University.objects.create(name="UNSA") 
        
        self.campus = UniversityCampus.objects.create(
            university=self.uni, 
            name="Ingenierías", 
            latitude=-16.4, 
            longitude=-71.5
        )

    def test_create_accommodation_draft(self):
        """
        PU003-1: Creación exitosa de anuncio.
        Resultado esperado: Status 201 y estado del anuncio 'draft'.
        """
        print("\n" + "="*70)
        print("PU003-1: CREAR ANUNCIO EN DRAFT")
        print("="*70)
        
        # Autenticamos como propietario
        print(f"\n[SETUP] Autenticando propietario: {self.owner_user.email}")
        self.client.force_authenticate(user=self.owner_user)

        url = reverse('accommodation-list') # /api/accommodations/
        data = {
            'title': 'Habitación cerca a la UNSA',
            'description': 'Habitación iluminada',
            'accommodation_type': self.type_apartment.id,
            'address': 'Av. Independencia 123',
            'latitude': -16.409047,
            'longitude': -71.537451,
            'monthly_price': '350.00',
            'coexistence_rules': 'No fumar',
            'rooms': 1
        }

        print(f"\n[INPUT] Datos del anuncio:")
        print(f"  - Título: {data['title']}")
        print(f"  - Precio mensual: S/. {data['monthly_price']}")
        print(f"  - Tipo: {self.type_apartment.name}")
        print(f"  - Dirección: {data['address']}")
        print(f"\n[EXPECTED] Status: 201 CREATED, Estado: 'draft'")

        # --- EJECUCIÓN ---
        resp = self.client.post(url, data, format='json')

        # --- VERIFICACIÓN ---
        print(f"\n[RESULT] Status: {resp.status_code}")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data['title'], 'Habitación cerca a la UNSA')
        
        # Verificar en BD que el estado se asignó automáticamente a "draft"
        acc = Accommodation.objects.get(id=resp.data['id'])
        print(f"[RESULT] Anuncio creado:")
        print(f"  - ID: {acc.id}")
        print(f"  - Estado: {acc.status.name}")
        print(f"  - Propietario: {acc.owner.user.email}")
        
        self.assertEqual(acc.status.name, 'draft', "El estado inicial debe ser draft")
        self.assertEqual(acc.owner, self.owner_profile, "El dueño debe ser el usuario logueado")
        
        print("\n✓ TEST EXITOSO")
        print("="*70)

    def test_publish_accommodation(self):
        """
        PU003-2: Publicación de anuncio.
        Prerrequisito: Tener un anuncio en 'draft'.
        Resultado esperado: Status 200 y cambio de estado a 'published'.
        """
        print("\n" + "="*70)
        print("PU003-2: PUBLICAR ANUNCIO")
        print("="*70)
        
        print(f"\n[SETUP] Autenticando propietario: {self.owner_user.email}")
        self.client.force_authenticate(user=self.owner_user)

        # Creamos un alojamiento previo en estado draft
        print(f"\n[SETUP] Creando anuncio en estado DRAFT...")
        acc = Accommodation.objects.create(
            owner=self.owner_profile,
            title="Borrador",
            monthly_price=100,
            status=self.status_draft
        )
        print(f"  - ID: {acc.id}")
        print(f"  - Título: {acc.title}")
        print(f"  - Estado inicial: {acc.status.name}")

        # Llamamos a la "Action" personalizada 'publish' definida en la ViewSet
        # URL típica: /api/accommodations/{id}/publish/
        url = reverse('accommodation-publish', kwargs={'pk': acc.id})
        
        print(f"\n[INPUT] POST a {url}")
        print(f"[EXPECTED] Status: 200 OK, Estado: 'published'")
        
        # --- EJECUCIÓN ---
        resp = self.client.post(url)

        # --- VERIFICACIÓN ---
        print(f"\n[RESULT] Status: {resp.status_code}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        
        acc.refresh_from_db() # Recargamos desde BD
        print(f"[RESULT] Estado actualizado: {acc.status.name}")
        self.assertEqual(acc.status.name, 'published', "El estado debió cambiar a published")
        
        print("\n✓ TEST EXITOSO: Anuncio publicado correctamente")
        print("="*70)

    def test_save_calculated_distances(self):
        """
        PU003-4: Guardado de distancias a universidades (Bulk).
        Nota: El backend NO calcula, recibe el cálculo del frontend y lo guarda.
        """
        print("\n" + "="*70)
        print("PU003-4: GUARDAR DISTANCIAS A UNIVERSIDADES (BULK)")
        print("="*70)
        
        print(f"\n[SETUP] Autenticando propietario: {self.owner_user.email}")
        self.client.force_authenticate(user=self.owner_user)
        
        # Creamos el alojamiento
        print(f"\n[SETUP] Creando alojamiento...")
        acc = Accommodation.objects.create(
            owner=self.owner_profile, title="Casa", monthly_price=500, status=self.status_draft
        )
        print(f"  - ID Anuncio: {acc.id}")
        print(f"  - Título: {acc.title}")

        url = reverse('university-distances-bulk') # /api/university-distances/bulk/
        
        # Simulamos los datos que enviaría el Frontend después de calcular con Mapbox
        payload = {
            "accommodation": acc.id,
            "distances": [
                {
                    "campus": self.campus.id,
                    "distance_km": "2.50",
                    "walk_time_minutes": 15,
                    "bus_time_minutes": 10
                }
            ]
        }

        print(f"\n[INPUT] Guardando distancias:")
        print(f"  - Campus: {self.campus.name} (ID: {self.campus.id})")
        print(f"  - Distancia: {payload['distances'][0]['distance_km']} km")
        print(f"  - Tiempo caminando: {payload['distances'][0]['walk_time_minutes']} min")
        print(f"  - Tiempo en bus: {payload['distances'][0]['bus_time_minutes']} min")
        print(f"\n[EXPECTED] Status: 201 CREATED, Registro en BD")

        # --- EJECUCIÓN ---
        resp = self.client.post(url, payload, format='json')

        # --- VERIFICACIÓN ---
        print(f"\n[RESULT] Status: {resp.status_code}")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        
        # Verificar que se guardó en la tabla intermedia
        exists = UniversityDistance.objects.filter(accommodation=acc, campus=self.campus).exists()
        self.assertTrue(exists, "La distancia debió guardarse en la BD")
        
        distance_obj = UniversityDistance.objects.get(accommodation=acc, campus=self.campus)
        print(f"[RESULT] Distancia guardada en BD:")
        print(f"  - ID: {distance_obj.id}")
        print(f"  - Distancia: {distance_obj.distance_km} km")
        
        print("\n✓ TEST EXITOSO: Distancias guardadas correctamente")
        print("="*70)


class FavoriteManagementTests(APITestCase):
    """
    PU004: GESTIÓN DE FAVORITOS (ESTUDIANTES)
    -------------------------------------------------------------------
    Objetivo: Verificar que los estudiantes puedan agregar y quitar favoritos.
    """

    def setUp(self):
        # Datos Maestros
        self.status_published = AccommodationStatus.objects.create(name="published")
        
        # 1. Crear Usuario Estudiante
        self.student_user = User.objects.create_user(email='estudiante@test.com', password='password123')
        self.student_profile = StudentProfile.objects.create(
            user=self.student_user, status=UserStatus.objects.create(name='active_s')
        )

        # 2. Crear Usuario Propietario y un Alojamiento
        owner_user = User.objects.create_user(email='owner@test.com', password='123')
        owner_profile = OwnerProfile.objects.create(user=owner_user, dni='123', status=UserStatus.objects.get(name='active_s'))
        
        self.accommodation = Accommodation.objects.create(
            owner=owner_profile,
            title="Habitación Ideal",
            monthly_price=400,
            status=self.status_published
        )

    def test_add_to_favorites_success(self):
        """
        PU004-1: Agregar propiedad a favoritos.
        Resultado esperado: 201 Created.
        """
        self.client.force_authenticate(user=self.student_user)

        url = reverse('favorite-list') # /api/favorites/
        data = {
            'accommodation': self.accommodation.id
        }

        resp = self.client.post(url, data, format='json')

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Favorite.objects.filter(student=self.student_profile, accommodation=self.accommodation).exists())

    def test_add_duplicate_favorite(self):
        """
        PU004-4: Agregar favorito duplicado.
        Nota: El código es 'Idempotente', si ya existe devuelve 200 OK (no error 400).
        Esto es correcto técnicamente.
        """
        self.client.force_authenticate(user=self.student_user)
        
        # Pre-creamos el favorito
        Favorite.objects.create(student=self.student_profile, accommodation=self.accommodation)

        url = reverse('favorite-list')
        data = {'accommodation': self.accommodation.id}

        # Intentamos crearlo de nuevo
        resp = self.client.post(url, data, format='json')

        # la view dice: if existing: return Response(..., status=200)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        
        # Verificar que NO se duplicó el registro (count debe seguir siendo 1)
        count = Favorite.objects.filter(student=self.student_profile, accommodation=self.accommodation).count()
        self.assertEqual(count, 1, "No debe haber duplicados en favoritos")

    def test_remove_favorite(self):
        """
        PU004-2: Remover propiedad de favoritos.
        Resultado esperado: 204 No Content.
        """
        self.client.force_authenticate(user=self.student_user)
        
        # Creamos favorito para borrarlo
        fav = Favorite.objects.create(student=self.student_profile, accommodation=self.accommodation)

        url = reverse('favorite-detail', kwargs={'pk': fav.id})
        
        resp = self.client.delete(url)

        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Favorite.objects.filter(id=fav.id).exists())

    def test_get_favorites_list(self):
        """
        PU004-3: Ver lista de favoritos.
        """
        self.client.force_authenticate(user=self.student_user)
        Favorite.objects.create(student=self.student_profile, accommodation=self.accommodation)

        url = reverse('favorite-list')
        resp = self.client.get(url)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 1)
        self.assertEqual(resp.data[0]['accommodation'], self.accommodation.id)
    
class SearchAndStateTests(APITestCase):
    """
    PU005 y PU006: BÚSQUEDA Y ESTADOS
    -------------------------------------------------------------------
    Objetivo: Verificar filtros públicos y transiciones de estado (ciclo de vida).
    """

    def setUp(self):
        # --- 1. DATOS MAESTROS ---
        self.status_published = AccommodationStatus.objects.create(name="published")
        self.status_draft = AccommodationStatus.objects.create(name="draft")
        self.status_hidden = AccommodationStatus.objects.create(name="hidden")
        self.status_deleted = AccommodationStatus.objects.create(name="deleted")
        
        self.type_apt = AccommodationType.objects.create(name="Departamento")
        self.service_wifi = PredefinedService.objects.create(name="WiFi")

        # --- 2. USUARIOS ---
        self.owner_user = User.objects.create_user(email='propietario@test.com', password='123')
        self.owner_profile = OwnerProfile.objects.create(
            user=self.owner_user, dni='123', status=UserStatus.objects.create(name='active_o')
        )

        # --- 3. UNIVERSIDAD (Para filtros) ---
        self.uni_unsa = University.objects.create(name="UNSA")
        self.campus_ing = UniversityCampus.objects.create(university=self.uni_unsa, name="Ingenierías", latitude=0, longitude=0)

        # --- 4. ALOJAMIENTOS DE PRUEBA ---
        
        # Alojamiento A: Publicado, Barato (300), Cerca a UNSA
        self.acc_cheap = Accommodation.objects.create(
            owner=self.owner_profile,
            title="Cuarto Barato Estudiante",
            description="Ideal para alumnos",
            monthly_price=300,
            status=self.status_published,
            accommodation_type=self.type_apt
        )
        # Asignamos distancia a UNSA (Simulada)
        UniversityDistance.objects.create(
            accommodation=self.acc_cheap, campus=self.campus_ing, distance_km=1.5
        )
        # Asignamos servicio WiFi
        AccommodationService.objects.create(accommodation=self.acc_cheap, service=self.service_wifi)

        # Alojamiento B: Publicado, Caro (800), Lejos o sin universidad registrada
        self.acc_expensive = Accommodation.objects.create(
            owner=self.owner_profile,
            title="Depa de Lujo",
            description="Muy exclusivo",
            monthly_price=800,
            status=self.status_published,
            accommodation_type=self.type_apt
        )

        # Alojamiento C: Borrador (Draft)
        self.acc_draft = Accommodation.objects.create(
            owner=self.owner_profile, title="Borrador", monthly_price=500, status=self.status_draft
        )

        # Alojamiento D: Oculto (Hidden)
        self.acc_hidden = Accommodation.objects.create(
            owner=self.owner_profile, title="Oculto", monthly_price=500, status=self.status_hidden
        )

    # ==========================================
    # PU005: BÚSQUEDA Y FILTROS
    # ==========================================

    def test_search_price_filter(self):
        """PU005-1: Búsqueda con filtro de precio (Rango 200-500)."""
        # Endpoint: /api/public/accommodations/filter/
        url = reverse('public-accommodations-filter-accommodations') 
        
        # Filtramos entre 200 y 500. Debería salir el barato (300) pero no el caro (800)
        resp = self.client.get(url, {'min_price': 200, 'max_price': 500})
        
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data['results']), 1)
        self.assertEqual(resp.data['results'][0]['id'], self.acc_cheap.id)

    def test_search_university_filter(self):
        """PU005-2: Filtro por universidad cercana (UNSA)."""
        url = reverse('public-accommodations-filter-accommodations')
        
        # Filtramos por ID de universidad. Solo acc_cheap tiene distancia registrada a UNSA.
        resp = self.client.get(url, {'university_id': self.uni_unsa.id})
        
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data['results']), 1)
        self.assertEqual(resp.data['results'][0]['id'], self.acc_cheap.id)

    def test_search_natural_language(self):
        """PU005-3: Búsqueda por texto (Título/Descripción)."""
        url = reverse('public-accommodations-filter-accommodations')
        
        # Buscamos "Lujo". Debería traer acc_expensive.
        resp = self.client.get(url, {'q': 'Lujo'})
        
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data['results']), 1)
        self.assertEqual(resp.data['results'][0]['title'], "Depa de Lujo")

    def test_search_multiple_filters(self):
        """PU005-4: Búsqueda combinada (Precio + Servicio + Universidad)."""
        url = reverse('public-accommodations-filter-accommodations')
        
        # Buscamos: Precio < 400, Con WiFi, Cerca a UNSA
        params = {
            'max_price': 400,
            'services': f"{self.service_wifi.id}",
            'university_id': self.uni_unsa.id
        }
        resp = self.client.get(url, params)
        
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data['results']), 1)
        self.assertEqual(resp.data['results'][0]['id'], self.acc_cheap.id)

    # ==========================================
    # PU006: ESTADOS DE PUBLICACIÓN
    # ==========================================

    def test_change_status_to_hidden(self):
        """PU006-1: Ocultar propiedad (Hide)."""
        self.client.force_authenticate(user=self.owner_user)
        
        # Usamos el alojamiento que ya está publicado (cheap)
        url = reverse('accommodation-hide', kwargs={'pk': self.acc_cheap.id})
        
        resp = self.client.post(url)
        
        self.assertEqual(resp.status_code, 200)
        
        self.acc_cheap.refresh_from_db()
        self.assertEqual(self.acc_cheap.status.name, 'hidden')
        
        # Verificación extra: No debe salir en búsqueda pública
        public_url = reverse('public-accommodations-list')
        resp_public = self.client.get(public_url)
        # Iteramos los resultados para asegurar que no esté
        ids = [acc['id'] for acc in resp_public.data['results']]
        self.assertNotIn(self.acc_cheap.id, ids, "Una propiedad oculta no debe ser pública")

    def test_recover_hidden_property(self):
        """PU006-2: Recuperar propiedad hidden (Volver a publicar)."""
        self.client.force_authenticate(user=self.owner_user)
        
        # Usamos el alojamiento oculto (acc_hidden)
        url = reverse('accommodation-publish', kwargs={'pk': self.acc_hidden.id})
        
        resp = self.client.post(url)
        
        self.assertEqual(resp.status_code, 200)
        self.acc_hidden.refresh_from_db()
        self.assertEqual(self.acc_hidden.status.name, 'published')

    def test_logical_delete_property(self):
        """PU006-3: Eliminación lógica de propiedad."""
        self.client.force_authenticate(user=self.owner_user)
        
        url = reverse('accommodation-delete-logical', kwargs={'pk': self.acc_cheap.id})
        
        resp = self.client.post(url)
        
        self.assertEqual(resp.status_code, 200)
        self.acc_cheap.refresh_from_db()
        self.assertEqual(self.acc_cheap.status.name, 'deleted')
        
        # Verificar que el dueño YA NO lo ve en su lista general (la get_queryset excluye deleted)
        list_url = reverse('accommodation-list')
        resp_list = self.client.get(list_url)
        ids = [a['id'] for a in resp_list.data]
        self.assertNotIn(self.acc_cheap.id, ids)

    def test_list_properties_owner_draft(self):
        """PU006-4: Listar propiedades (verificar que el dueño ve sus borradores)."""
        self.client.force_authenticate(user=self.owner_user)
        
        url = reverse('accommodation-list')
        resp = self.client.get(url)
        
        self.assertEqual(resp.status_code, 200)
        
        # El dueño debería ver 'acc_draft', 'acc_hidden', 'acc_cheap', 'acc_expensive'
        # (menos los deleted).
        ids = [a['id'] for a in resp.data]
        
        self.assertIn(self.acc_draft.id, ids, "El propietario debe poder ver sus borradores")
        self.assertIn(self.acc_hidden.id, ids, "El propietario debe poder ver sus ocultos")
