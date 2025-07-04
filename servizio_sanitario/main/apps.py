from django.apps import AppConfig
from django.core.management import call_command



class MainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'

    def ready(self):
        try:
            call_command('aggiorna_ricoveri')
        except Exception as e:
            print(f'Errore aggiornamento ricoveri: {e}')