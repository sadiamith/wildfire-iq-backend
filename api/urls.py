from django.urls import path
from api.v1.views import (
    ActiveFiresListView,
    WildFireStatsView,
    PredictRiskView,
    AbandonedWellsListView,
    WellStatsView,
    WellClustersView
)

app_name = 'api'

urlpatterns = [
    # v1 API endpoints
    path("v1/fires/active/", ActiveFiresListView.as_view(), name="active-fires"),
    path("v1/stats/today/", WildFireStatsView.as_view(), name="wildfire-stats"),
    path("v1/predict-risk/", PredictRiskView.as_view(), name="predict-risk"),
    path("v1/energy-wells/", AbandonedWellsListView.as_view(), name="abandoned-wells"),
    path("v1/energy-wells/stats/", WellStatsView.as_view(), name="well-stats"),
    path("v1/energy-wells/clusters/", WellClustersView.as_view(), name="well-clusters"),
]
