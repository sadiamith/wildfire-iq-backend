from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from django.db.models import Sum, Count, Q
from datetime import datetime, timedelta

from fires.models import Wildfire
from fires.api.serializers import (
    WildfireSerializer,
    WildfireListSerializer,
    WildfireStatsSerializer
)

class ActiveFiresListView(generics.ListAPIView):
    """API endpoints to get all active wildfires in Alberta"""

    serializer_class = WildfireListSerializer

    def get_queryset(self):
        return Wildfire.objects.filter(status='ACTIVE')

class WildFireStatsView(APIView):
    """API endpoints for wildfire statistics"""

    def get(self, request):
        today = timezone.now().date()

        # calculate statistics
        stats = {
            "total_active_fires": Wildfire.objects.filter(status="ACTIVE").count(),
            "total_hectares_burned": Wildfire.objects.aggregate(
                total=Sum("size_hectares")
            )["total"]
            or 0,
            "fires_today": Wildfire.objects.filter(detected_date__date=today).count(),
            "fires_by_status": dict(
                Wildfire.objects.values("status")
                .annotate(count=Count("id"))
                .values_list("status", "count")
            ),
            "last_updated": timezone.now(),
        }

        serializer = WildfireStatsSerializer(stats)
        return Response(serializer.data)


class PredictRiskView(APIView):
    """API endpoint for AI-powered wildfire risk prediction"""

    def get(self, request):
        # placeholder for AI integration
        # for now, return mock data
        mock_prediction = {
            "risk_level": "MODERATE",
            "risk_score": 65,
            "factors": {
                "temperature": "High",
                "humidity": "Low",
                "wind_speed": "Moderate",
                "recent_precipitation": "Minimal",
            },
            "recommendation": "Exercise caution in forested areas. Fire ban in effect.",
            "predicted_at": timezone.now(),
        }

        return Response(mock_prediction)