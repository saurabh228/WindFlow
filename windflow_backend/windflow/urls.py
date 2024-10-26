from django.urls import path
from .views import get_rollups, get_current_weather, get_cities, get_interval, set_interval, check_connection_status, get_thresholds, set_thresholds

urlpatterns = [
    path('get-rollups/', get_rollups),
    path('current-weather/', get_current_weather),
    path('get-cities/', get_cities),
    path('check-connection-status/', check_connection_status),
    path('get-interval/', get_interval),
    path('set-interval/', set_interval),
    path('get-thresholds/', get_thresholds),
    path('set-thresholds/', set_thresholds),
]