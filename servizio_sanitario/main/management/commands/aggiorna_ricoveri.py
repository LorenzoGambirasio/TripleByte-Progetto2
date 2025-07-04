from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from main.models import Ricovero  # Usa il tuo modello

class Command(BaseCommand):
    help = 'Aggiorna lo stato dei ricoveri attivi'

    def handle(self, *args, **options):
        oggi = timezone.now().date()
        ricoveri = Ricovero.objects.filter(stato=0)
        aggiornati = 0

        for ricovero in ricoveri:
            data_fine = ricovero.data_ingresso + timedelta(days=ricovero.durata)
            if data_fine < oggi:
                ricovero.stato = 2  # dimesso
                ricovero.save()
                aggiornati += 1

        self.stdout.write(self.style.SUCCESS(f'Ricoveri aggiornati: {aggiornati}'))
