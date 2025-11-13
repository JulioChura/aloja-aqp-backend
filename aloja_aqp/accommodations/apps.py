from django.apps import AppConfig


class AccommodationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "accommodations"
    
    def ready(self):
        # Importar señales para asegurar que los handlers (post_save) se registren
        # al iniciar la app. Mantener en español para claridad de mantenimiento.
        try:
            from . import signals  # noqa: F401
        except Exception:
            # No queremos que un error en signals impida que la app arranque;
            # los problemas se deben investigar en desarrollo/CI.
            pass
