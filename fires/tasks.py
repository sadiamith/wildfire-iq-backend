from celery import shared_task
from django.core.management import call_command
from django.utils import timezone
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)


@shared_task(name="fetch_latest_fires")
def fetch_latest_fires():
    """
    Fetch latest fire data from FIRMS API.
    This task should run every 2-4 hours.
    """
    try:
        # Prevent multiple simultaneous fetches
        lock_key = "fetch_fires_lock"
        if cache.get(lock_key):
            logger.info("Fire fetch already in progress, skipping...")
            return "Skipped - already running"

        # Set lock for 10 minutes
        cache.set(lock_key, True, 600)

        logger.info("Starting scheduled fire data fetch...")

        # Fetch last 2 days of data to ensure we don't miss anything
        call_command("fetch_firms_data", days=2)

        # Clear the lock
        cache.delete(lock_key)

        logger.info("Scheduled fire data fetch completed")
        return f"Success - fetched at {timezone.now()}"

    except Exception as e:
        logger.error(f"Error in scheduled fire fetch: {e}")
        cache.delete(lock_key)
        raise


@shared_task(name="cleanup_old_fires")
def cleanup_old_fires():
    """
    Clean up fires older than 30 days that are marked as 'OUT'.
    This task should run daily.
    """
    from fires.models import Wildfire
    from datetime import timedelta

    try:
        cutoff_date = timezone.now() - timedelta(days=30)

        # Delete old fires that are out
        deleted_count = Wildfire.objects.filter(
            status="OUT", last_updated__lt=cutoff_date
        ).delete()[0]

        logger.info(f"Cleaned up {deleted_count} old fire records")
        return f"Deleted {deleted_count} old fires"

    except Exception as e:
        logger.error(f"Error in fire cleanup: {e}")
        raise


@shared_task(name="generate_daily_report")
def generate_daily_report():
    """
    Generate daily statistics report.
    This task should run once per day.
    """
    from fires.models import Wildfire
    from django.db.models import Count, Sum

    try:
        stats = {
            "date": timezone.now().date(),
            "active_fires": Wildfire.objects.filter(status="ACTIVE").count(),
            "total_hectares": Wildfire.objects.filter(status="ACTIVE").aggregate(
                Sum("size_hectares")
            )["size_hectares__sum"]
            or 0,
            "new_fires_today": Wildfire.objects.filter(
                detected_date__date=timezone.now().date()
            ).count(),
            "fires_by_status": dict(
                Wildfire.objects.values("status")
                .annotate(count=Count("id"))
                .values_list("status", "count")
            ),
        }

        logger.info(f"Daily report: {stats}")

        # You could email this, save to a model, or send to a monitoring service
        return stats

    except Exception as e:
        logger.error(f"Error generating daily report: {e}")
        raise
