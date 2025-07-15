from django.core.management.base import BaseCommand
from django.utils import timezone
from fires.services.firms_services import FIRMSService
from fires.models import Wildfire
import logging


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Fetch active fire data from NASA FIRMS API'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=1,
            help='Number of days of historical data to fetch (max 10)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing FIRMS data before importing'
        )

    def handle(self, *args, **options):
        days_back = options['days']
        clear_existing = options['clear']

        self.stdout.write(f"Fetching FIRMS data for the last {days_back} days(s).....")

        # Initialize the service
        service = FIRMSService()

        # Clear existing FIRMS data if requested
        if clear_existing:
            deleted_count = Wildfire.objects.filter(data_source="NASA_FIRMS").delete()[
                0
            ]
            self.stdout.write(
                self.style.WARNING(f"Cleared {deleted_count} existing FIRMS records")
            )

        
        # Fetch data
        firms_data = service.fetch_active_fires(days_back=days_back)

        if not firms_data:
            self.stdout.write(self.style.ERROR("No fire data retrieved from FIRMS"))
            return

        self.stdout.write(
            self.style.SUCCESS(f"Retrieved {len(firms_data)} fire detections")
        )

        # Transform and save data
        created_count = 0
        updated_count = 0
        error_count = 0

        for fire_data in firms_data:
            transformed = service.transform_to_wildfire_model(fire_data)

            if not transformed:
                error_count += 1
                continue

            try:
                # Use update_or_create to avoid duplicates
                wildfire, created = Wildfire.objects.update_or_create(
                    fire_id=transformed["fire_id"], defaults=transformed
                )

                if created:
                    created_count += 1
                    self.stdout.write(f"Created: {wildfire.fire_id}")
                else:
                    updated_count += 1
                    self.stdout.write(f"Updated: {wildfire.fire_id}")

            except Exception as e:
                error_count += 1
                logger.error(f"Error saving fire {transformed.get('fire_id')}: {e}")

        # Summary
        self.stdout.write(
            self.style.SUCCESS(
                f"\nSummary:\n"
                f"- Created: {created_count} new fires\n"
                f"- Updated: {updated_count} existing fires\n"
                f"- Errors: {error_count}\n"
                f"- Total active fires in DB: {Wildfire.objects.filter(status='ACTIVE').count()}"
            )
        )
