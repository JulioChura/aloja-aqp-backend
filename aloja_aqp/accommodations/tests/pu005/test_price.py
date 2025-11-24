import pytest
from decimal import Decimal
from rest_framework.test import APIClient

from accommodations.models import Accommodation, AccommodationStatus, AccommodationType
from users.models import User, OwnerProfile


def _results_from_response(resp):
    data = resp.data
    if isinstance(data, dict) and 'results' in data:
        return data['results']
    return data


@pytest.mark.django_db
def test_price_filter_returns_properties_in_range():
    client = APIClient()

    status = AccommodationStatus.objects.create(name='published')
    atype = AccommodationType.objects.create(name='Departamento')

    user = User.objects.create_user(email='owner_price@example.com', password='pass')
    owner = OwnerProfile.objects.create(user=user, dni='90000000')

    Accommodation.objects.create(owner=owner, title='A1', address='C1', latitude=-16.4, longitude=-71.5, monthly_price=Decimal('150'), accommodation_type=atype, status=status)
    Accommodation.objects.create(owner=owner, title='A2', address='C2', latitude=-16.4, longitude=-71.5, monthly_price=Decimal('300'), accommodation_type=atype, status=status)
    Accommodation.objects.create(owner=owner, title='A3', address='C3', latitude=-16.4, longitude=-71.5, monthly_price=Decimal('600'), accommodation_type=atype, status=status)

    resp = client.get('/api/public/accommodations/filter', {'min_price': '200', 'max_price': '500'})
    assert resp.status_code == 200
    results = _results_from_response(resp)
    returned_titles = [r.get('title') for r in results]
    assert 'A2' in returned_titles
    assert 'A1' not in returned_titles
    assert 'A3' not in returned_titles
