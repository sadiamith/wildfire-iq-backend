from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from django.db.models import Sum, Count, Avg, Q
from datetime import datetime, timedelta
from rest_framework.decorators import action

from fires.models import Wildfire
from fires.api.serializers import (
    WildfireSerializer,
    WildfireListSerializer,
    WildfireStatsSerializer
)
from fires.models import AbandonedWell
from fires.api.serializers import AbandonedWellListSerializer

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
        mock_prediction = [{
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
        }]

        return Response(mock_prediction)


class AbandonedWellsListView(generics.ListAPIView):
    """API endpoint to get abandoned wells in Alberta."""

    serializer_class = AbandonedWellListSerializer

    def get_queryset(self):
        queryset = AbandonedWell.objects.all()

        # Get query parameters
        north = self.request.query_params.get("north")
        south = self.request.query_params.get("south")
        east = self.request.query_params.get("east")
        west = self.request.query_params.get("west")
        limit = self.request.query_params.get("limit", 1000)

        # Filter by bounding box (required for large dataset)
        if all([north, south, east, west]):
            try:
                queryset = queryset.filter(
                    latitude__gte=float(south),
                    latitude__lte=float(north),
                    longitude__gte=float(west),
                    longitude__lte=float(east),
                )
            except ValueError:
                pass
        else:
            # If no bounds specified, return a sample around Calgary
            queryset = queryset.filter(
                latitude__gte=50.8,
                latitude__lte=51.3,
                longitude__gte=-114.3,
                longitude__lte=-113.8,
            )

        # Limit results
        try:
            limit = min(int(limit), 5000)  # Max 5000 wells
        except ValueError:
            limit = 1000

        return queryset[:limit]


class WellStatsView(APIView):
    """API endpoint for abandoned well statistics."""

    def get(self, request):
        # Get query parameters for filtering
        north = request.query_params.get("north")
        south = request.query_params.get("south")
        east = request.query_params.get("east")
        west = request.query_params.get("west")

        queryset = AbandonedWell.objects.all()

        # Apply bounding box filter if provided
        if all([north, south, east, west]):
            try:
                queryset = queryset.filter(
                    latitude__gte=float(south),
                    latitude__lte=float(north),
                    longitude__gte=float(west),
                    longitude__lte=float(east),
                )
            except ValueError:
                pass

        # Calculate stats
        stats = {
            "total_wells": queryset.count(),
            "wells_in_view": queryset.count() if all([north, south, east, west]) else 0,
            "top_licensees": list(
                queryset.values("licensee")
                .annotate(count=Count("id"))
                .order_by("-count")[:5]
                .values("licensee", "count")
            ),
            "wells_by_type": dict(
                queryset.values("well_type")
                .annotate(count=Count("id"))
                .values_list("well_type", "count")
            ),
            "last_updated": timezone.now(),
        }

        return Response(stats)


class WellClustersView(APIView):
    """API endpoint for clustered well data for map display."""

    def get(self, request):
        # This would return clustered data for better map performance
        # Implementation depends on your frontend mapping library
        north = float(request.query_params.get("north", 60))
        south = float(request.query_params.get("south", 49))
        east = float(request.query_params.get("east", -110))
        west = float(request.query_params.get("west", -120))
        zoom = int(request.query_params.get("zoom", 8))

        # For now, return a grid-based aggregation
        # In production, you might use PostGIS or a clustering algorithm

        # Simple grid clustering
        grid_size = 0.5 if zoom < 10 else 0.1  # Degrees

        clusters = []
        lat = south
        while lat < north:
            lon = west
            while lon < east:
                count = AbandonedWell.objects.filter(
                    latitude__gte=lat,
                    latitude__lt=lat + grid_size,
                    longitude__gte=lon,
                    longitude__lt=lon + grid_size,
                ).count()

                if count > 0:
                    clusters.append(
                        {
                            "center": {
                                "lat": lat + grid_size / 2,
                                "lng": lon + grid_size / 2,
                            },
                            "count": count,
                        }
                    )

                lon += grid_size
            lat += grid_size

        return Response(
            {"clusters": clusters, "total_clusters": len(clusters), "zoom": zoom}
        )
