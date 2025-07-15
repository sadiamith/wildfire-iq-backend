from django.core.management.base import BaseCommand
from django_celery_beat.models import PeriodicTask, IntervalSchedule, CrontabSchedule
import json


class Command(BaseCommand):
    help = "Set up periodic tasks for fire data fetching"

    def handle(self, *args, **kwargs):
        # Create schedules

        # Every 3 hours
        three_hour_schedule, _ = IntervalSchedule.objects.get_or_create(
            every=3,
            period=IntervalSchedule.HOURS,
        )

        # Daily at 2 AM Mountain Time
        daily_schedule, _ = CrontabSchedule.objects.get_or_create(
            minute=0,
            hour=2,
            day_of_week="*",
            day_of_month="*",
            month_of_year="*",
            timezone="America/Edmonton",
        )

        # Daily at 8 AM Mountain Time for reports
        report_schedule, _ = CrontabSchedule.objects.get_or_create(
            minute=0,
            hour=8,
            day_of_week="*",
            day_of_month="*",
            month_of_year="*",
            timezone="America/Edmonton",
        )

        # Create or update periodic tasks

        # Fetch fires every 3 hours
        fetch_task, created = PeriodicTask.objects.update_or_create(
            name="Fetch latest fires",
            defaults={
                "task": "fetch_latest_fires",
                "interval": three_hour_schedule,
                "enabled": True,
                "kwargs": json.dumps({}),
            },
        )

        # Cleanup old fires daily
        cleanup_task, created = PeriodicTask.objects.update_or_create(
            name="Cleanup old fires",
            defaults={
                "task": "cleanup_old_fires",
                "crontab": daily_schedule,
                "enabled": True,
                "kwargs": json.dumps({}),
            },
        )

        # Generate daily report
        report_task, created = PeriodicTask.objects.update_or_create(
            name="Generate daily report",
            defaults={
                "task": "generate_daily_report",
                "crontab": report_schedule,
                "enabled": True,
                "kwargs": json.dumps({}),
            },
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully set up periodic tasks:\n"
                f"- Fetch fires: every 3 hours\n"
                f"- Cleanup old fires: daily at 2 AM MT\n"
                f"- Generate report: daily at 8 AM MT"
            )
        )
