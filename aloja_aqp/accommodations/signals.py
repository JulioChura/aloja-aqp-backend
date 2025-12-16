from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.conf import settings
import math
import logging

from .models import Accommodation, UniversityDistance
from universities.models import UniversityCampus
from .utils.routing import mapbox_route

logger = logging.getLogger(__name__)




# Guardar coordenadas antiguas antes de guardar
@receiver(pre_save, sender=Accommodation)
def guardar_coordenadas_anteriores(sender, instance, **kwargs):
    if instance.pk:
        try:
            old = Accommodation.objects.get(pk=instance.pk)
            instance._old_latitude = old.latitude
            instance._old_longitude = old.longitude
        except Accommodation.DoesNotExist:
            instance._old_latitude = None
            instance._old_longitude = None
    else:
        instance._old_latitude = None
        instance._old_longitude = None

@receiver(post_save, sender=Accommodation)
def calcular_distancias_universidad_al_guardar(sender, instance, created, **kwargs):
    """
    Calcular distancias/tiempos hacia cada UniversityCampus solo cuando:
    - Se crea una nueva propiedad (created=True)
    - O cuando cambian las coordenadas (latitude/longitude)
    """
    logger.info('Signal: post_save Accommodation id=%s created=%s', getattr(instance, 'id', None), created)

    recalcular = False
    if created:
        recalcular = True
    else:
        old_lat = getattr(instance, '_old_latitude', None)
        old_lon = getattr(instance, '_old_longitude', None)
        if old_lat != instance.latitude or old_lon != instance.longitude:
            recalcular = True

    if not recalcular:
        logger.info('Accommodation id=%s sin cambio de coordenadas, omitiendo cálculo de distancias', getattr(instance, 'id', None))
        return

    if instance.latitude is None or instance.longitude is None:
        logger.info('Accommodation id=%s sin coordenadas, omitiendo cálculo de distancias', getattr(instance, 'id', None))
        return

    campuses_con_coordenadas = UniversityCampus.objects.filter(latitude__isnull=False, longitude__isnull=False)

    for campus in campuses_con_coordenadas:
        try:
            logger.info('Calculando ruta server-side para accommodation=%s -> campus=%s', instance.id, getattr(campus, 'id', None))
            logger.debug('Coords accommodation=(%s,%s) campus=(%s,%s)', instance.latitude, instance.longitude, campus.latitude, campus.longitude)
            resultado_ruta = mapbox_route(
                float(instance.latitude), float(instance.longitude),
                float(campus.latitude), float(campus.longitude),
                profile='walking'
            )
        except Exception as e:
            logger.warning('Error calculando ruta para accommodation=%s campus=%s: %s', instance.id, getattr(campus, 'id', None), str(e))
            continue

        if not resultado_ruta:
            logger.info('Proveedor no devolvió ruta para accommodation=%s campus=%s', instance.id, getattr(campus, 'id', None))
            continue

        distancia_km = resultado_ruta.get('distance_km')
        duracion_minutos = resultado_ruta.get('duration_min')
        minutos_a_pie = math.ceil(duracion_minutos) if duracion_minutos is not None else None

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
