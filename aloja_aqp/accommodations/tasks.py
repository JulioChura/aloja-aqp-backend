from celery import shared_task
from .utils.routing import mapbox_route
from .models import UniversityDistance, Accommodation, UniversityCampus

def update_university_distance(accommodation_id, campus_id, lat, lon):
    campus = UniversityCampus.objects.get(pk=campus_id)
    route_data = mapbox_route(lat, lon, campus.latitude, campus.longitude)
    if route_data:
        UniversityDistance.objects.update_or_create(
            accommodation_id=accommodation_id,
            campus_id=campus_id,
            defaults={
                'distance_km': route_data['distance_km'],
                'walk_time_minutes': None,  # Set if needed
                'bus_time_minutes': None,   # Set if needed
                'route': route_data['geometry'],
            }
        )

@shared_task
def async_update_university_distances(accommodation_id, lat, lon):
    campuses = UniversityCampus.objects.all()
    for campus in campuses:
        update_university_distance(accommodation_id, campus.id, lat, lon)
