from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random

from fires.models import Wildfire


class Command(BaseCommand):
    help = "Creates test wildfire data for development"

    def handle(self, *args, **kwargs):
        # Clear existing data
        Wildfire.objects.all().delete()

        # Alberta boundary approximation
        alberta_bounds = {
            "lat_min": 49.0,
            "lat_max": 60.0,
            "lon_min": -120.0,
            "lon_max": -110.0,
        }

        # Test fire data
        test_fires = [
            {
                "fire_id": "AB-2025-001",
                "fire_name": "Jasper Complex",
                "latitude": 52.8737,
                "longitude": -118.0814,
                "size_hectares": 1250.5,
                "status": "ACTIVE",
                "cause": "Lightning",
            },
            {
                "fire_id": "AB-2025-002",
                "fire_name": "Bow Valley Fire",
                "latitude": 51.1784,
                "longitude": -115.5708,
                "size_hectares": 85.3,
                "status": "CONTAINED",
                "cause": "Human",
            },
            {
                "fire_id": "AB-2025-003",
                "fire_name": "Peace River Incident",
                "latitude": 56.2317,
                "longitude": -117.2917,
                "size_hectares": 542.8,
                "status": "ACTIVE",
                "cause": "Unknown",
            },
            {
                "fire_id": "AB-2025-004",
                "fire_name": "Red Deer Forest Fire",
                "latitude": 52.2681,
                "longitude": -113.8112,
                "size_hectares": 22.1,
                "status": "UNDER_CONTROL",
                "cause": "Human",
            },
            {
                "fire_id": "AB-2025-005",
                "fire_name": "Fort McMurray North",
                "latitude": 56.7265,
                "longitude": -111.3790,
                "size_hectares": 3200.0,
                "status": "ACTIVE",
                "cause": "Lightning",
                "detected_date": timezone.now(),  # Today's fire
            },
        ]

        # Create fires with varied detection dates
        for i, fire_data in enumerate(test_fires):
            if "detected_date" not in fire_data:
                # Random date within last 7 days
                days_ago = random.randint(1, 7)
                fire_data["detected_date"] = timezone.now() - timedelta(days=days_ago)

            fire = Wildfire.objects.create(**fire_data)
            self.stdout.write(
                self.style.SUCCESS(f"Created fire: {fire.fire_id} - {fire.fire_name}")
            )

        # Summary
        total = Wildfire.objects.count()
        active = Wildfire.objects.filter(status="ACTIVE").count()

        self.stdout.write(
            self.style.SUCCESS(
                f"\nSuccessfully created {total} test fires ({active} active)"
            )
        )
