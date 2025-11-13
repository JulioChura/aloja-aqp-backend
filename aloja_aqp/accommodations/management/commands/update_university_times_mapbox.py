from django.core.management.base import BaseCommand
from accommodations.models import UniversityDistance, Accommodation
from universities.models import UniversityCampus
from accommodations.utils.routing import mapbox_route
from decimal import Decimal
from django.db import transaction
import time


class Command(BaseCommand):
    help = 'Update UniversityDistance entries using Mapbox Directions API (fills distance_km and walk_time_minutes by default)'

    def add_arguments(self, parser):
        parser.add_argument('--profile', default='walking', help='Routing profile: driving|walking|cycling')
        parser.add_argument('--limit', type=int, default=0, help='Limit number of UniversityDistance rows to process (0 = all)')
        parser.add_argument('--sleep', type=float, default=0.5, help='Seconds to sleep between requests (rate limiting)')

    def handle(self, *args, **options):
        profile = options['profile']
        limit = options['limit']
        sleep = options['sleep']

        qs = UniversityDistance.objects.select_related('accommodation', 'campus')
        # optional: only process those without walk_time_minutes
        qs = qs.filter(accommodation__latitude__isnull=False, accommodation__longitude__isnull=False,
                       campus__latitude__isnull=False, campus__longitude__isnull=False)
        if limit and limit > 0:
            qs = qs[:limit]

        total = qs.count()
        self.stdout.write(f'Processing {total} UniversityDistance rows (profile={profile})')

        processed = 0
        for ud in qs:
            acc = ud.accommodation
            campus = ud.campus
            try:
                result = mapbox_route(acc.latitude, acc.longitude, campus.latitude, campus.longitude, profile=profile)
            except Exception as e:
                self.stderr.write(f'Error fetching route for UD id={ud.id}: {e}')
                result = None

            if result:
                ud.distance_km = result['distance_km']
                # store duration as integer minutes
                ud.walk_time_minutes = int(round(result['duration_min'])) if profile == 'walking' else ud.walk_time_minutes
                # if driving/cycling profile, store in bus_time_minutes as an example
                if profile == 'driving':
                    ud.bus_time_minutes = int(round(result['duration_min']))
                ud.save(update_fields=['distance_km', 'walk_time_minutes', 'bus_time_minutes'])
                processed += 1

            time.sleep(sleep)

        self.stdout.write(self.style.SUCCESS(f'Done. Processed {processed} routes.'))
