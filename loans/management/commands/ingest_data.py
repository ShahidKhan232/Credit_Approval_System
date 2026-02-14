from django.core.management.base import BaseCommand
from loans.tasks import ingest_all_data


class Command(BaseCommand):
    help = 'Ingest customer and loan data from Excel files'

    def handle(self, *args, **options):
        self.stdout.write('Starting data ingestion...')
        
        # Trigger background task
        result = ingest_all_data.delay()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Data ingestion task queued with ID: {result.id}'
            )
        )
        self.stdout.write(
            'Check Celery worker logs for progress'
        )
