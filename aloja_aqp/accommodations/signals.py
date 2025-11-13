from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
import math
import logging

from .models import Accommodation, UniversityDistance
from universities.models import UniversityCampus
from .utils.routing import mapbox_route

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Accommodation)
def calcular_distancias_universidad_al_guardar(sender, instance, created, **kwargs):
    """
    Al guardar una `Accommodation` (creación o actualización), calcular y guardar
    las distancias/tiempos hacia cada `UniversityCampus` que tenga coordenadas.

    Esta implementación es intencionalmente simple y sin background jobs: realiza
    llamadas síncronas al proveedor (Mapbox) vía `mapbox_route`. Para producción,
    considerar mover esto a un worker/Celery y añadir cache.
    """

    # Registrar inicio del proceso para depuración
    logger.info('Signal: post_save Accommodation id=%s created=%s - iniciando cálculo de distancias', getattr(instance, 'id', None), created)

    # Si no hay coordenadas en el alojamiento, no intentamos calcular rutas
    if instance.latitude is None or instance.longitude is None:
        logger.info('Accommodation id=%s sin coordenadas, omitiendo cálculo de distancias', getattr(instance, 'id', None))
        return

    # Recolectar campuses que tengan coordenadas válidas
    campuses_con_coordenadas = UniversityCampus.objects.filter(latitude__isnull=False, longitude__isnull=False)

    for campus in campuses_con_coordenadas:
        try:
            logger.info('Calculando ruta server-side para accommodation=%s -> campus=%s', instance.id, getattr(campus, 'id', None))
            logger.debug('Coords accommodation=(%s,%s) campus=(%s,%s)', instance.latitude, instance.longitude, campus.latitude, campus.longitude)
            # Llamada al proveedor de rutas (Mapbox) - perfil 'walking' por defecto
            resultado_ruta = mapbox_route(
                float(instance.latitude), float(instance.longitude),
                float(campus.latitude), float(campus.longitude),
                profile='walking'
            )
        except Exception as e:
            # Registrar el error y continuar con el siguiente campus
            logger.warning('Error calculando ruta para accommodation=%s campus=%s: %s', instance.id, getattr(campus, 'id', None), str(e))
            continue

        if not resultado_ruta:
            # Si el proveedor no devolvió ruta, no creamos/actualizamos el registro
            logger.info('Proveedor no devolvió ruta para accommodation=%s campus=%s', instance.id, getattr(campus, 'id', None))
            continue

        distancia_km = resultado_ruta.get('distance_km')
        duracion_minutos = resultado_ruta.get('duration_min')
        minutos_a_pie = math.ceil(duracion_minutos) if duracion_minutos is not None else None

        # Crear o actualizar el objeto UniversityDistance
        try:
            UniversityDistance.objects.update_or_create(
                accommodation=instance,
                campus=campus,
                defaults={
                    'distance_km': distancia_km,
                    'walk_time_minutes': minutos_a_pie,
                    'route': resultado_ruta.get('geometry'),
                }
            )
            logger.info('UniversityDistance guardado para accommodation=%s campus=%s distance_km=%s walk_min=%s', instance.id, getattr(campus, 'id', None), distancia_km, minutos_a_pie)
        except Exception as e:
            logger.error('Fallo al guardar UniversityDistance para accommodation=%s campus=%s: %s', instance.id, getattr(campus, 'id', None), str(e))
