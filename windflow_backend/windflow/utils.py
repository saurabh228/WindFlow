import os
import requests
from datetime import datetime
from collections import Counter
from django.utils import timezone
from django.db.models import Avg, Max, Min
from .models import WeatherData, City, DailySummary, TemperatureThreshold, HumidityThreshold, WindSpeedThreshold, ConditionThreshold


def kelvin_to_celsius(kelvin):
    return kelvin - 273.15

def fetch_weather_data():
    api_key = os.getenv('OPENWEATHERMAP_API_KEY')
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    
    cities = City.objects.all()

    for city in cities:
        params = {
            'lat': city.latitude,
            'lon': city.longitude,
            'appid': api_key
        }
        response = requests.get(base_url, params=params)
        data = response.json()
        
        try:
            response.raise_for_status()
            weather_data = WeatherData(
            city=city.name,
            dominant_condition=data['weather'][0]['main'],
            temp=kelvin_to_celsius(data['main']['temp']),
            feels_like=kelvin_to_celsius(data['main']['feels_like']),
            dt=timezone.make_aware(datetime.fromtimestamp(data['dt']), timezone.get_current_timezone()),
            humidity=data['main']['humidity'],
            wind_speed=data['wind']['speed'],
            wind_deg=data['wind']['deg'],
            clouds=data['clouds']['all']
            )
            weather_data.save()
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred for {city.name}: {http_err}")
        except Exception as err:
            print(f"An error occurred for {city.name}: {err}")

def update_daily_summary_for_today():
    today = timezone.now().date()
    cities = City.objects.all()

    for city in cities:
        city_data = WeatherData.objects.filter(city=city, dt__date=today)
        try:
            if city_data.exists():
                weather_data = {
                    'avg_temp' : city_data.aggregate(Avg('temp'))['temp__avg'],
                    'max_temp' : city_data.aggregate(Max('temp'))['temp__max'],
                    'min_temp' : city_data.aggregate(Min('temp'))['temp__min'],
                    'avg_feels_like' : city_data.aggregate(Avg('feels_like'))['feels_like__avg'],
                    'max_feels_like' : city_data.aggregate(Max('feels_like'))['feels_like__max'],
                    'min_feels_like' : city_data.aggregate(Min('feels_like'))['feels_like__min'],
                    'avg_humidity' : city_data.aggregate(Avg('humidity'))['humidity__avg'],
                    'avg_wind_speed' : city_data.aggregate(Avg('wind_speed'))['wind_speed__avg'],
                    'avg_wind_deg' : city_data.aggregate(Avg('wind_deg'))['wind_deg__avg'],
                    'avg_clouds' : city_data.aggregate(Avg('clouds'))['clouds__avg'],
                    'dominant_condition' : Counter(city_data.values_list('dominant_condition', flat=True)).most_common(3)[0][0]
                }
                DailySummary.objects.update_or_create(
                    city=city,
                    date=today,
                    defaults=weather_data
                )
                return weather_data

        except Exception as e:
            print(f"An error occurred while updating summary for {city} on {today}: {e}")
            return None

def check_thresholds():
    alerts = []

    # Check temperature thresholds
    temp_thresholds = TemperatureThreshold.objects.all()
    for threshold in temp_thresholds:
        recent_data = WeatherData.objects.filter(city=threshold.city).order_by('-dt')[:threshold.consecutive_updates]
        if recent_data.count() < threshold.consecutive_updates:
            continue

        min_breached = all(data.temp < threshold.min_threshold for data in recent_data)
        if min_breached: breach = 'Minimum'
        else:
            max_breached = all(data.temp > threshold.max_threshold for data in recent_data)
            if max_breached: breach = 'Maximum'
            else: breach = None
        
        if breach:
            alerts.append(
                {
                    'type': 'Temperature',
                    'city': threshold.city,
                    'breach': breach,
                    'threshold': threshold.min_threshold if breach == 'Minimum' else threshold.max_threshold,
                    'consecutive_updates': threshold.consecutive_updates
                }
            )

    # Check humidity thresholds
    humidity_thresholds = HumidityThreshold.objects.all()
    for threshold in humidity_thresholds:
        recent_data = WeatherData.objects.filter(city=threshold.city).order_by('-dt')[:threshold.consecutive_updates]
        if recent_data.count() < threshold.consecutive_updates:
            continue

        min_breached = all(data.humidity < threshold.min_threshold for data in recent_data)
        if min_breached: breach = 'Minimum'
        else:
            max_breached = all(data.humidity > threshold.max_threshold for data in recent_data)
            if max_breached: breach = 'Maximum'
            else: breach = None
        
        if breach:
            alerts.append(
                {
                    'type': 'Humidity',
                    'city': threshold.city,
                    'breach': breach,
                    'threshold': threshold.min_threshold if breach == 'Minimum' else threshold.max_threshold,
                    'consecutive_updates': threshold.consecutive_updates
                }
            )

    # Check wind speed thresholds
    wind_speed_thresholds = WindSpeedThreshold.objects.all()
    for threshold in wind_speed_thresholds:
        recent_data = WeatherData.objects.filter(city=threshold.city).order_by('-dt')[:threshold.consecutive_updates]
        if recent_data.count() < threshold.consecutive_updates:
            continue

        min_breached = all(data.wind_speed < threshold.min_threshold for data in recent_data)
        if min_breached: breach = 'Minimum'
        else:
            max_breached = all(data.wind_speed > threshold.max_threshold for data in recent_data)
            if max_breached: breach = 'Maximum'
            else: breach = None
        
        if breach:
            alerts.append(
                {
                    'type': 'Wind Speed',
                    'city': threshold.city,
                    'breach': breach,
                    'threshold': threshold.min_threshold if breach == 'Minimum' else threshold.max_threshold,
                    'consecutive_updates': threshold.consecutive_updates
                }
            )

    # Check condition thresholds
    condition_thresholds = ConditionThreshold.objects.all()
    for threshold in condition_thresholds:
        recent_data = WeatherData.objects.filter(city=threshold.city).order_by('-dt')[:threshold.consecutive_updates]
        if recent_data.count() < threshold.consecutive_updates:
            continue

        condition_breached = all(data.dominant_condition == threshold.condition for data in recent_data)
        if condition_breached:
            alerts.append(
                {
                    'type': 'Condition',
                    'city': threshold.city,
                    'threshold': threshold.condition,
                    'consecutive_updates': threshold.consecutive_updates
                }
            )

    return alerts





