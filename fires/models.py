from django.db import models
from django.utils import timezone


class Wildfire(models.Model):
    """Model to store wildfire incident data for Alberta, Canada."""

    # Fire identification
    fire_id = models.CharField(max_length=100, unique=True, db_index=True, help_text="Unique identifier for the wildfire incident.")
    fire_name = models.CharField(max_length=200, blank=True, help_text="Name of the wildfire incident.")

    # Location data
    latitude = models.FloatField(help_text="Latitude of the wildfire incident location.")
    longitude = models.FloatField(help_text="Longitude of the wildfire incident location.")
    location_description = models.TextField(blank=True, help_text="Description of the wildfire incident location.")

    # Fire metrics
    size_hectares = models.FloatField(default=0, help_text="Size of the wildfire incident in hectares.")
    status = models.CharField(
        max_length=50,
        choices=[
            ('ACTIVE', 'Active'),
            ('CONTAINED', 'Contained'),
            ('UNDER_CONTROL', 'Under Control'),
            ('OUT', 'Out')
        ],
        default='ACTIVE',
        help_text="Current status of the wildfire incident."
    )

    # Timestaps
    detected_date = models.DateTimeField(default=timezone.now, help_text="Date and time when the wildfire incident was detected.")
    last_updated = models.DateTimeField(auto_now=True, help_text="Date and time when the wildfire incident was last updated.")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Date and time when the wildfire incident record was created.")

    # Additional Data
    cause = models.CharField(max_length=100, blank=True)
    data_source = models.CharField(max_length=50, default='NASA FIRMS')

    class Meta:
        ordering = ['-detected_date']
        indexes = [
            models.Index(fields=['status', 'detected_date'])
        ]

    def __str__(self):
        return f"{self.fire_id} - {self.fire_name or 'Unnamed'} ({self.status})"


class AbandonedWell(models.Model):
    """Model to store abandoned oil/gas well data for Alberta."""

    # Well identification
    well_id = models.CharField(max_length=100, unique=True, db_index=True)
    license_number = models.CharField(max_length=100, blank=True)
    well_name = models.CharField(max_length=200, blank=True)

    # Location data
    latitude = models.FloatField(db_index=True)
    longitude = models.FloatField(db_index=True)

    # Well details
    well_type = models.CharField(max_length=50, blank=True)
    status = models.CharField(max_length=50, default="ABANDONED")
    abandonment_date = models.DateField(null=True, blank=True)

    # Company info
    licensee = models.CharField(max_length=200, blank=True)

    # Risk factors
    surface_location = models.CharField(max_length=200, blank=True)
    ground_elevation = models.FloatField(null=True, blank=True)
    total_depth = models.FloatField(null=True, blank=True, help_text="Depth in meters")

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    data_source = models.CharField(max_length=50, default="AER")

    class Meta:
        ordering = ["well_id"]
        indexes = [
            models.Index(fields=["latitude", "longitude"]),
            models.Index(fields=["status", "well_type"]),
        ]

    def __str__(self):
        return f"{self.well_id} - {self.well_name or 'Unnamed'}"
