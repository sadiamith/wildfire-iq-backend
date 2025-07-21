from rest_framework import serializers
from fires.models import Wildfire, AbandonedWell


class WildfireSerializer(serializers.ModelSerializer):
    """Serializer for the Wildfire model with all fields."""

    class Meta:
        model = Wildfire
        fields = '__all__'
        read_only_fields = ('created_at', 'last_updated')


class WildfireListSerializer(serializers.ModelSerializer):
    """Serializer for listing wildfires with selected fields."""

    class Meta:
        model = Wildfire
        fields = [
            'fire_id',
            'fire_name',
            'latitude',
            'longitude',
            'size_hectares',
            'status',
            'detected_date',
            'last_updated'
        ]

class WildfireStatsSerializer(serializers.Serializer):
    """Serializer for wildfire statistics."""

    total_active_fires = serializers.IntegerField()
    total_hectares_burned = serializers.FloatField()
    fires_today = serializers.IntegerField()
    fires_by_status = serializers.DictField(child=serializers.IntegerField())
    last_updated = serializers.DateTimeField()


class AbandonedWellSerializer(serializers.ModelSerializer):
    """Serializer for abandoned well data."""

    class Meta:
        model = AbandonedWell
        fields = [
            "well_id",
            "license_number",
            "well_name",
            "latitude",
            "longitude",
            "well_type",
            "status",
            "licensee",
            "surface_location",
            "total_depth",
        ]


class AbandonedWellListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing wells on map."""

    class Meta:
        model = AbandonedWell
        fields = [
            "well_id",
            "latitude",
            "longitude",
            "well_type",
            "licensee",
        ]
