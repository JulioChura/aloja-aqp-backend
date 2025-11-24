import pytest
from decimal import Decimal
from rest_framework.test import APIClient
from accommodations.models import Accommodation, UniversityDistance


@pytest.fixture
def api_client():
    """Cliente API para tests de integración"""
    return APIClient()


@pytest.fixture
def datos_para_filtros(db, owner_user, accommodation_type, accommodation_statuses, campus):
    """Fixture que crea alojamientos con precios variados para probar filtros"""
    
    # Alojamientos FUERA del rango [200, 500]
    acc_150 = Accommodation.objects.create(
        owner=owner_user,
        title='Muy económico',
        accommodation_type=accommodation_type,
        address='Calle Barata 1',
        monthly_price=Decimal('150.00'),
        rooms=1,
        status=accommodation_statuses['published']
    )
    acc_550 = Accommodation.objects.create(
        owner=owner_user,
        title='Caro',
        accommodation_type=accommodation_type,
        address='Calle Cara 2',
        monthly_price=Decimal('550.00'),
        rooms=2,
        status=accommodation_statuses['published']
    )
    acc_650 = Accommodation.objects.create(
        owner=owner_user,
        title='Muy caro',
        accommodation_type=accommodation_type,
        address='Calle Lujosa 3',
        monthly_price=Decimal('650.00'),
        rooms=3,
        status=accommodation_statuses['published']
    )
    
    # Alojamientos DENTRO del rango [200, 500]
    acc_250 = Accommodation.objects.create(
        owner=owner_user,
        title='Económico en rango',
        accommodation_type=accommodation_type,
        address='Calle Media 4',
        monthly_price=Decimal('250.00'),
        rooms=1,
        status=accommodation_statuses['published']
    )
    acc_350 = Accommodation.objects.create(
        owner=owner_user,
        title='Moderado',
        accommodation_type=accommodation_type,
        address='Calle Normal 5',
        monthly_price=Decimal('350.00'),
        rooms=2,
        status=accommodation_statuses['published']
    )
    acc_450 = Accommodation.objects.create(
        owner=owner_user,
        title='Estándar alto',
        accommodation_type=accommodation_type,
        address='Calle Buena 6',
        monthly_price=Decimal('450.00'),
        rooms=2,
        status=accommodation_statuses['published']
    )
    
    # En los límites exactos
    acc_200 = Accommodation.objects.create(
        owner=owner_user,
        title='Límite inferior',
        accommodation_type=accommodation_type,
        address='Calle Min 7',
        monthly_price=Decimal('200.00'),
        rooms=1,
        status=accommodation_statuses['published']
    )
    acc_500 = Accommodation.objects.create(
        owner=owner_user,
        title='Límite superior',
        accommodation_type=accommodation_type,
        address='Calle Max 8',
        monthly_price=Decimal('500.00'),
        rooms=3,
        status=accommodation_statuses['published']
    )
    
    # Crear distancias para todos
    for acc in [acc_150, acc_550, acc_650, acc_250, acc_350, acc_450, acc_200, acc_500]:
        UniversityDistance.objects.create(
            accommodation=acc,
            campus=campus,
            distance_km=Decimal('1.0'),
            walk_time_minutes=15,
            bus_time_minutes=7
        )
    
    return {
        'fuera_rango': [acc_150, acc_550, acc_650],
        'dentro_rango': [acc_250, acc_350, acc_450],
        'limites': [acc_200, acc_500],
        'todos': [acc_150, acc_200, acc_250, acc_350, acc_450, acc_500, acc_550, acc_650]
    }


@pytest.mark.django_db
def test_pu005_filtro_precio_200_500(api_client, datos_para_filtros):
    """PU005 - Búsqueda con filtro de precio [200, 500] soles (API Integration)"""
    
    response = api_client.get('/api/public/accommodations/filter/', {
        'min_price': '200',
        'max_price': '500'
    })
    
    assert response.status_code == 200, f"Error en API: {response.status_code}"
    
    data = response.json()
    results = data.get('results', data)  # Manejar paginación
    
    # Verificar count: deben ser exactamente 5 (200, 250, 350, 450, 500)
    assert len(results) == 5, f"Esperaba 5 resultados, obtuvo {len(results)}"
    
    # Verificar que todos los precios están en rango [200, 500]
    for item in results:
        precio = Decimal(str(item['monthly_price']))
        assert Decimal('200.00') <= precio <= Decimal('500.00'), \
            f"Alojamiento '{item['title']}' con precio {precio} fuera de rango"
    
    # Verificar precios específicos esperados
    precios = [Decimal(str(item['monthly_price'])) for item in results]
    assert Decimal('200.00') in precios, "Falta precio 200"
    assert Decimal('250.00') in precios, "Falta precio 250"
    assert Decimal('350.00') in precios, "Falta precio 350"
    assert Decimal('450.00') in precios, "Falta precio 450"
    assert Decimal('500.00') in precios, "Falta precio 500"
    
    # Verificar que NO están los fuera de rango
    assert Decimal('150.00') not in precios, "No debería incluir precio 150"
    assert Decimal('550.00') not in precios, "No debería incluir precio 550"
    assert Decimal('650.00') not in precios, "No debería incluir precio 650"


@pytest.mark.django_db
def test_pu005_filtro_precio_solo_min(api_client, datos_para_filtros):
    """PU005 - Filtro con solo precio mínimo"""
    
    response = api_client.get('/api/public/accommodations/filter/', {
        'min_price': '450'
    })
    
    assert response.status_code == 200
    data = response.json()
    results = data.get('results', data)
    
    # Debe retornar: 450, 500, 550, 650
    assert len(results) >= 4
    for item in results:
        precio = Decimal(str(item['monthly_price']))
        assert precio >= Decimal('450.00'), f"Precio {precio} menor a 450"


@pytest.mark.django_db
def test_pu005_filtro_precio_solo_max(api_client, datos_para_filtros):
    """PU005 - Filtro con solo precio máximo"""
    
    response = api_client.get('/api/public/accommodations/filter/', {
        'max_price': '350'
    })
    
    assert response.status_code == 200
    data = response.json()
    results = data.get('results', data)
    
    # Debe retornar: 150, 200, 250, 350
    assert len(results) >= 4
    for item in results:
        precio = Decimal(str(item['monthly_price']))
        assert precio <= Decimal('350.00'), f"Precio {precio} mayor a 350"


@pytest.mark.django_db
def test_pu005_filtro_precio_limites_inclusivos(api_client, datos_para_filtros):
    """PU005 - Verificar que los límites son inclusivos (>=, <=)"""
    
    # Límite exacto inferior
    response = api_client.get('/api/public/accommodations/filter/', {
        'min_price': '200',
        'max_price': '200'
    })
    
    assert response.status_code == 200
    data = response.json()
    results = data.get('results', data)
    
    assert len(results) == 1, "Debe encontrar exactamente el alojamiento de 200"
    assert Decimal(str(results[0]['monthly_price'])) == Decimal('200.00')
    
    # Límite exacto superior
    response = api_client.get('/api/public/accommodations/filter/', {
        'min_price': '500',
        'max_price': '500'
    })
    
    assert response.status_code == 200
    data = response.json()
    results = data.get('results', data)
    
    assert len(results) == 1, "Debe encontrar exactamente el alojamiento de 500"
    assert Decimal(str(results[0]['monthly_price'])) == Decimal('500.00')