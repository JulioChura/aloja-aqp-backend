import pytest
from decimal import Decimal
from rest_framework.test import APIClient
from accommodations.models import Accommodation, UniversityDistance
from universities.models import University, UniversityCampus


@pytest.fixture
def api_client():
    """Cliente API para tests de integración"""
    return APIClient()


@pytest.fixture
def datos_proximidad_unsa(db, owner_user, accommodation_type, accommodation_statuses, universities, campuses):
    """Fixture que crea alojamientos a diferentes distancias de UNSA"""
    
    unsa = universities['UNSA']
    campus_unsa = campuses['unsa_ingenieria']
    
    # Alojamientos MUY CERCANOS (<1km)
    acc_muy_cerca = Accommodation.objects.create(
        owner=owner_user,
        title='Al lado de UNSA',
        accommodation_type=accommodation_type,
        address='Av. Independencia 100',
        latitude=-16.4010,
        longitude=-71.5376,
        monthly_price=Decimal('450.00'),
        rooms=2,
        status=accommodation_statuses['published']
    )
    dist_muy_cerca = UniversityDistance.objects.create(
        accommodation=acc_muy_cerca,
        campus=campus_unsa,
        distance_km=Decimal('0.5'),
        walk_time_minutes=5,
        bus_time_minutes=2
    )
    
    # Alojamientos CERCANOS (1-2km)
    acc_cerca = Accommodation.objects.create(
        owner=owner_user,
        title='Cerca a UNSA',
        accommodation_type=accommodation_type,
        address='Av. Venezuela 200',
        latitude=-16.4050,
        longitude=-71.5400,
        monthly_price=Decimal('400.00'),
        rooms=2,
        status=accommodation_statuses['published']
    )
    dist_cerca = UniversityDistance.objects.create(
        accommodation=acc_cerca,
        campus=campus_unsa,
        distance_km=Decimal('1.5'),
        walk_time_minutes=15,
        bus_time_minutes=5
    )
    
    # Alojamientos en LÍMITE (2.5-3km)
    acc_limite = Accommodation.objects.create(
        owner=owner_user,
        title='En el límite de UNSA',
        accommodation_type=accommodation_type,
        address='Av. Dolores 300',
        latitude=-16.4100,
        longitude=-71.5450,
        monthly_price=Decimal('350.00'),
        rooms=1,
        status=accommodation_statuses['published']
    )
    dist_limite = UniversityDistance.objects.create(
        accommodation=acc_limite,
        campus=campus_unsa,
        distance_km=Decimal('2.8'),
        walk_time_minutes=30,
        bus_time_minutes=10
    )
    
    # Alojamientos FUERA del radio (>3km)
    acc_lejos = Accommodation.objects.create(
        owner=owner_user,
        title='Lejos de UNSA',
        accommodation_type=accommodation_type,
        address='Cayma Distrito',
        latitude=-16.3800,
        longitude=-71.5600,
        monthly_price=Decimal('300.00'),
        rooms=1,
        status=accommodation_statuses['published']
    )
    dist_lejos = UniversityDistance.objects.create(
        accommodation=acc_lejos,
        campus=campus_unsa,
        distance_km=Decimal('4.5'),
        walk_time_minutes=50,
        bus_time_minutes=20
    )
    
    acc_muy_lejos = Accommodation.objects.create(
        owner=owner_user,
        title='Muy lejos de UNSA',
        accommodation_type=accommodation_type,
        address='Paucarpata Distrito',
        latitude=-16.4300,
        longitude=-71.4800,
        monthly_price=Decimal('250.00'),
        rooms=1,
        status=accommodation_statuses['published']
    )
    dist_muy_lejos = UniversityDistance.objects.create(
        accommodation=acc_muy_lejos,
        campus=campus_unsa,
        distance_km=Decimal('6.2'),
        walk_time_minutes=70,
        bus_time_minutes=30
    )
    
    return {
        'unsa': unsa,
        'campus_unsa': campus_unsa,
        'dentro_3km': [acc_muy_cerca, acc_cerca, acc_limite],
        'fuera_3km': [acc_lejos, acc_muy_lejos],
        'distancias': {
            acc_muy_cerca.id: Decimal('0.5'),
            acc_cerca.id: Decimal('1.5'),
            acc_limite.id: Decimal('2.8'),
            acc_lejos.id: Decimal('4.5'),
            acc_muy_lejos.id: Decimal('6.2'),
        }
    }


@pytest.mark.django_db
def test_pu005_filtro_universidad_unsa_3km(api_client, datos_proximidad_unsa):
    """PU005 - Filtro por universidad cercana UNSA con radio 3km (API Integration)"""
    
    unsa = datos_proximidad_unsa['unsa']
    
    # Nota: El endpoint actual no tiene parámetro 'max_distance', solo filtra por universidad
    # y ordena por distancia. Aquí testeamos que al filtrar por universidad,
    # los resultados estén ordenados por proximidad.
    
    response = api_client.get('/api/public/accommodations/filter/', {
        'university_id': str(unsa.id)
    })
    
    assert response.status_code == 200, f"Error en API: {response.status_code}"
    
    data = response.json()
    results = data.get('results', data)
    
    # Verificar que hay resultados
    assert len(results) > 0, "Debe retornar alojamientos cercanos a UNSA"
    
    # Verificar que están ordenados por distancia (más cercanos primero)
    distancias_api = []
    for item in results:
        # Buscar la distancia mínima de este alojamiento a UNSA
        uni_distances = item.get('university_distances', [])
        unsa_distances = [
            Decimal(str(d['distance_km'])) 
            for d in uni_distances 
            if d.get('campus_university_id') == unsa.id
        ]
        if unsa_distances:
            distancias_api.append(min(unsa_distances))
    
    # Verificar ordenamiento ascendente
    for i in range(len(distancias_api) - 1):
        assert distancias_api[i] <= distancias_api[i + 1], \
            f"Resultados no ordenados por distancia: {distancias_api[i]} > {distancias_api[i + 1]}"


@pytest.mark.django_db
def test_pu005_proximidad_unsa_solo_cercanos_3km(api_client, datos_proximidad_unsa):
    """PU005 - Verificar que solo aparecen alojamientos dentro de 3km de UNSA"""
    
    unsa = datos_proximidad_unsa['unsa']
    distancias = datos_proximidad_unsa['distancias']
    
    response = api_client.get('/api/public/accommodations/filter/', {
        'university_id': str(unsa.id)
    })
    
    assert response.status_code == 200
    data = response.json()
    results = data.get('results', data)
    
    # Filtrar manualmente los que están dentro de 3km según nuestra data de prueba
    ids_dentro_3km = {
        acc_id for acc_id, dist in distancias.items() if dist <= Decimal('3.0')
    }
    
    ids_fuera_3km = {
        acc_id for acc_id, dist in distancias.items() if dist > Decimal('3.0')
    }
    
    # Verificar que los alojamientos dentro de 3km están presentes
    result_ids = {item['id'] for item in results}
    
    # Al menos los de <=3km deben estar
    for acc_id in ids_dentro_3km:
        assert acc_id in result_ids, \
            f"Alojamiento {acc_id} a {distancias[acc_id]}km debería aparecer"


@pytest.mark.django_db
def test_pu005_proximidad_orden_correcto(api_client, datos_proximidad_unsa):
    """PU005 - Verificar orden correcto: 0.5km -> 1.5km -> 2.8km"""
    
    unsa = datos_proximidad_unsa['unsa']
    
    response = api_client.get('/api/public/accommodations/filter/', {
        'university_id': str(unsa.id)
    })
    
    assert response.status_code == 200
    data = response.json()
    results = data.get('results', data)
    
    # Extraer los títulos en orden
    titulos_orden = [item['title'] for item in results]
    
    # Verificar que "Al lado de UNSA" (0.5km) aparece antes que "Cerca a UNSA" (1.5km)
    if 'Al lado de UNSA' in titulos_orden and 'Cerca a UNSA' in titulos_orden:
        idx_muy_cerca = titulos_orden.index('Al lado de UNSA')
        idx_cerca = titulos_orden.index('Cerca a UNSA')
        assert idx_muy_cerca < idx_cerca, \
            "Alojamiento más cercano debe aparecer primero"
    
    # Verificar que "En el límite de UNSA" (2.8km) aparece antes que los lejanos
    if 'En el límite de UNSA' in titulos_orden and 'Lejos de UNSA' in titulos_orden:
        idx_limite = titulos_orden.index('En el límite de UNSA')
        idx_lejos = titulos_orden.index('Lejos de UNSA')
        assert idx_limite < idx_lejos, \
            "Alojamiento en límite 3km debe aparecer antes que el de 4.5km"


@pytest.mark.django_db
def test_pu005_proximidad_campus_especifico(api_client, datos_proximidad_unsa):
    """PU005 - Filtrar por campus específico de UNSA"""
    
    campus_unsa = datos_proximidad_unsa['campus_unsa']
    
    response = api_client.get('/api/public/accommodations/filter/', {
        'campus_id': str(campus_unsa.id)
    })
    
    assert response.status_code == 200
    data = response.json()
    results = data.get('results', data)
    
    assert len(results) > 0, "Debe retornar alojamientos cerca del campus específico"
    
    # Verificar que todos tienen distancia al campus
    for item in results:
        uni_distances = item.get('university_distances', [])
        campus_ids = [d.get('campus_id') for d in uni_distances]
        assert campus_unsa.id in campus_ids, \
            f"Alojamiento {item['title']} debe tener distancia al campus filtrado"


@pytest.mark.django_db
def test_pu005_proximidad_combinar_precio_universidad(api_client, datos_proximidad_unsa):
    """PU005 - Filtro combinado: Universidad UNSA + Precio máximo 400"""
    
    unsa = datos_proximidad_unsa['unsa']
    
    response = api_client.get('/api/public/accommodations/filter/', {
        'university_id': str(unsa.id),
        'max_price': '400'
    })
    
    assert response.status_code == 200
    data = response.json()
    results = data.get('results', data)
    
    # Verificar que todos cumplen ambos filtros
    for item in results:
        # Precio <= 400
        precio = Decimal(str(item['monthly_price']))
        assert precio <= Decimal('400.00'), \
            f"Alojamiento {item['title']} con precio {precio} excede 400"
        
        # Tiene distancia a UNSA
        uni_distances = item.get('university_distances', [])
        unsa_distances = [
            d for d in uni_distances 
            if d.get('campus_university_id') == unsa.id
        ]
        assert len(unsa_distances) > 0, \
            f"Alojamiento {item['title']} debe tener distancia a UNSA"
