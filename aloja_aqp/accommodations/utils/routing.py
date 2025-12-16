from django.conf import settings
import requests
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


def mapbox_route(lat1, lon1, lat2, lon2, profile='driving'):

    token = getattr(settings, 'MAPBOX_ACCESS_TOKEN', None)
    if not token:
        raise RuntimeError('MAPBOX_ACCESS_TOKEN is not configured in settings')

    base = 'https://api.mapbox.com/directions/v5/mapbox'
    coords = f"{lon1},{lat1};{lon2},{lat2}"
    url = f"{base}/{profile}/{coords}"
    params = {
        'access_token': token,
        'overview': 'full',
        'geometries': 'geojson',
        'annotations': 'distance,duration'
    }
    try:
        safe_params = {k: v for k, v in params.items() if k != 'access_token'}
        logger.info('Mapbox request prepared - profile=%s coords=%s params=%s', profile, coords, safe_params)
    except Exception:
        pass

    try:
        resp = requests.get(url, params=params, timeout=12)
    except Exception as e:
        logger.exception('Error realizando request a Mapbox: %s', str(e))
        raise
    resp.raise_for_status()
    try:
        logger.info('Mapbox response status: %s for profile=%s coords=%s', resp.status_code, profile, coords)
    except Exception:
        pass

    data = resp.json()
    if not data or data.get('code') != 'Ok' or not data.get('routes'):
        return None

    route = data['routes'][0]
    distance_km = Decimal(route.get('distance', 0.0) / 1000.0).quantize(Decimal('0.01'))
    duration_min = float(route.get('duration', 0.0) / 60.0)
    geometry = route.get('geometry')
    return {
        'distance_km': distance_km,
        'duration_min': duration_min,
        'geometry': geometry,
    }
