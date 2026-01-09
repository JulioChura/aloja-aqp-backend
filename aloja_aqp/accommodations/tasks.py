def recalculate_accommodations_for_campus(campus_id):
	"""
	Recalcula distancia, tiempo y geometría de todos los alojamientos asociados a un campus/universidad.
	Llama a la API de Mapbox y actualiza UniversityDistance.
	"""
	from universities.models import UniversityCampus
	from .models import Accommodation, UniversityDistance
	from .utils.routing import mapbox_route
	import math

	try:
		campus = UniversityCampus.objects.get(id=campus_id)
	except UniversityCampus.DoesNotExist:
		return

	accommodations = Accommodation.objects.filter(latitude__isnull=False, longitude__isnull=False)
	for acc in accommodations:
		resultado_ruta = mapbox_route(
			float(acc.latitude), float(acc.longitude),
			float(campus.latitude), float(campus.longitude),
			profile='walking'
		)
		if not resultado_ruta:
			continue

		distancia_km = resultado_ruta.get('distance_km')
		duracion_minutos = resultado_ruta.get('duration_min')
		minutos_a_pie = math.ceil(duracion_minutos) if duracion_minutos is not None else None
		geometry = resultado_ruta.get('geometry')

		UniversityDistance.objects.update_or_create(
			accommodation=acc,
			campus=campus,
			defaults={
				'distance_km': distancia_km,
				'walk_time_minutes': minutos_a_pie,
				'route': geometry,
			}
		)
