from django.apps import AppConfig


class EchantillonnagesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "echantillonnages"

    def ready(self):
        # Import des signaux
        import echantillonnages.signals
