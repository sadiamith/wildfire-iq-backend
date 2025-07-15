from django.urls import path
from api.v1.views import (
    ActiveFiresListView,
    WildFireStatsView,
    PredictRiskView
)

app_name = 'api'

urlpatterns = [
    # v1 API endpoints
    path('v1/fires/active/', ActiveFiresListView.as_view(), name='active-fires'),
    path('v1/stats/today/', WildFireStatsView.as_view(), name='wildfire-stats'),
    path('v1/predict-risk/', PredictRiskView.as_view(), name='predict-risk'),
]

