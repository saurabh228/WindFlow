from django.core.management.base import BaseCommand
from django.utils import timezone
from windflow.models import DailySummary, City
from collections import Counter

from datetime import timedelta, datetime
import requests
import os



def kelvin_to_celsius(kelvin):
    return kelvin - 273.15

class Command(BaseCommand):
    help = 'Using 5 days forecast as previous 5 days data as archive api is not available for free'

    def handle(self, *args, **kwargs):

        DailySummary.objects.all().delete()

        api_key = os.getenv('OPENWEATHERMAP_API_KEY')
        base_url = "http://api.openweathermap.org/data/2.5/forecast"



        cities = City.objects.all()
        weather_data = {}
        for city in cities:

            weather_data[city] = {}
            
            params = {
                'lat': city.latitude,
                'lon': city.longitude,
                'appid': api_key
            }
            response = requests.get(base_url, params=params)
            data = response.json()

            try:
                response.raise_for_status()
                for item in data['list']:
                    date = timezone.make_aware(datetime.fromtimestamp(item['dt']), timezone.get_current_timezone()).date()
                    if date not in weather_data:
                        weather_data[city][date] = {
                            'temp': [],
                            'feels_like': [],
                            'humidity': [],
                            'wind_speed': [],
                            'wind_deg': [],
                            'clouds': [],
                            'dominant_condition': []
                        }

                    weather_data[city][date]['temp'].append(kelvin_to_celsius(item['main']['temp']))
                    weather_data[city][date]['feels_like'].append(kelvin_to_celsius(item['main']['feels_like']))
                    weather_data[city][date]['humidity'].append(item['main']['humidity'])
                    weather_data[city][date]['wind_speed'].append(item['wind']['speed'])
                    weather_data[city][date]['wind_deg'].append(item['wind']['deg'])
                    weather_data[city][date]['clouds'].append(item['clouds']['all'])
                    weather_data[city][date]['dominant_condition'].append(item['weather'][0]['main'])

            except requests.exceptions.HTTPError as http_err:
                print(f"HTTP error occurred for {city.name}: {http_err}")
                return
            except Exception as err:
                print(f"An error occurred for {city.name}: {err}")
                return

        avarege_data = {}
        for city, data in weather_data.items():
            avarege_data[city] = {}
            for date, values in data.items():
                avarege_data[city][date] = {
                    'avg_temp': sum(values['temp']) / len(values['temp']),
                    'max_temp': max(values['temp']),
                    'min_temp': min(values['temp']),
                    'avg_feels_like': sum(values['feels_like']) / len(values['feels_like']),
                    'max_feels_like': max(values['feels_like']),
                    'min_feels_like': min(values['feels_like']),
                    'avg_humidity': sum(values['humidity']) / len(values['humidity']),
                    'avg_wind_speed': sum(values['wind_speed']) / len(values['wind_speed']),
                    'avg_wind_deg': sum(values['wind_deg']) / len(values['wind_deg']),
                    'avg_clouds': sum(values['clouds']) / len(values['clouds']),
                    'dominant_condition': Counter(values['dominant_condition']).most_common(3)[0][0]
                }
        
        for city, data in avarege_data.items():
            for date, values in data.items():
                today = timezone.now().date()
                days_diff = (date - today).days
                fill_date = today - timedelta(days=days_diff)
                DailySummary.objects.update_or_create(
                    city=city,
                    date=fill_date,
                    defaults={
                        'avg_temp': values['avg_temp'],
                        'max_temp': values['max_temp'],
                        'min_temp': values['min_temp'],
                        'avg_feels_like': values['avg_feels_like'],
                        'max_feels_like': values['max_feels_like'],
                        'min_feels_like': values['min_feels_like'],
                        'avg_humidity': values['avg_humidity'],
                        'avg_wind_speed': values['avg_wind_speed'],
                        'avg_wind_deg': values['avg_wind_deg'],
                        'avg_clouds': values['avg_clouds'],
                        'dominant_condition': values['dominant_condition']
                    }
                )
        print(self.style.SUCCESS('Successfully backfilled daily summaries'))

    
            
        



