from django.contrib import admin
from .models import WeatherData, DailySummary, City, TemperatureThreshold, HumidityThreshold, WindSpeedThreshold, ConditionThreshold

@admin.register(WeatherData)
class WeatherDataAdmin(admin.ModelAdmin):
    list_display = ('city', 'dominant_condition', 'temp', 'feels_like', 'dt', 'humidity', 'wind_speed', 'wind_deg', 'clouds')
    list_filter = ('city', 'dominant_condition', 'dt')
    search_fields = ('city', 'dominant_condition')

@admin.register(DailySummary)
class DailySummaryAdmin(admin.ModelAdmin):
    list_display = ('city', 'date', 'avg_temp', 'max_temp', 'min_temp', 'dominant_condition')
    list_filter = ('city', 'date', 'dominant_condition')
    search_fields = ('city', 'dominant_condition')

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'latitude', 'longitude')
    search_fields = ('name',)

@admin.register(TemperatureThreshold)
class TemperatureAdmin(admin.ModelAdmin):
    list_display = ('city', 'min_threshold', 'max_threshold', 'consecutive_updates')
    search_fields = ('city',)

@admin.register(HumidityThreshold)
class HumidityAdmin(admin.ModelAdmin):
    list_display = ('city', 'min_threshold', 'max_threshold', 'consecutive_updates')
    search_fields = ('city',)

@admin.register(WindSpeedThreshold)
class WindSpeedAdmin(admin.ModelAdmin):
    list_display = ('city', 'min_threshold', 'max_threshold', 'consecutive_updates')
    search_fields = ('city',)

@admin.register(ConditionThreshold)
class ConditionAdmin(admin.ModelAdmin):
    list_display = ('city', 'condition', 'consecutive_updates')
    search_fields = ('city',)

