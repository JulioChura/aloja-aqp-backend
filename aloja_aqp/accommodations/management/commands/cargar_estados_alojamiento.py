from django.core.management.base import BaseCommand
from accommodations.models import AccommodationStatus

class Command(BaseCommand):
    help = 'Carga los estados iniciales de publicación de alojamientos (draft, published, hidden, deleted)'

    def handle(self, *args, **options):
        estados = ['draft', 'published', 'hidden', 'deleted']
        creados = 0
        for estado in estados:
            obj, created = AccommodationStatus.objects.get_or_create(name=estado)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Estado creado: {estado}"))
                creados += 1
            else:
                self.stdout.write(f"Estado ya existe: {estado}")
        if creados == 0:
            self.stdout.write(self.style.WARNING('No se crearon nuevos estados. Todos ya existen.'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Se crearon {creados} estados.'))
