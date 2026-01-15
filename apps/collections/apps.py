from django.apps import AppConfig


class CollectionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.collections'
    verbose_name = 'User Collections'

    def ready(self):
        import apps.collections.signals  # noqa
