from django.apps import AppConfig


class DataSyncConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.data_sync'
    verbose_name = 'Data Synchronization'
