from django.core.management.base import BaseCommand
from windflow.models import City
from django_celery_beat.models import PeriodicTask, IntervalSchedule

class Command(BaseCommand):
    help = 'Set up cities and periodic weather data fetching '

    def handle(self, *args, **kwargs):

        schedule, meow = IntervalSchedule.objects.update_or_create(
            id=1,
            defaults={
                'every':10,
                'period':IntervalSchedule.MINUTES
            }
        )
        PeriodicTask.objects.update_or_create(
            name='fetch_weather_data_periodicly',
            defaults={
                'task': 'windflow.tasks.fetch_weather_data_task',
                'interval': schedule
            }
        )

        all_cities = City.objects.values_list('name', flat=True)
        cities = [
            {'name': 'Delhi', 'latitude': 28.6667, 'longitude': 77.2167},
            {'name': 'Mumbai', 'latitude': 19.0144, 'longitude': 72.8479},
            {'name': 'Chennai', 'latitude': 13.0878, 'longitude': 80.2785},
            {'name': 'Bangalore', 'latitude': 12.9762, 'longitude': 77.6033},
            {'name': 'Kolkata', 'latitude': 22.5697, 'longitude': 88.3697},
            {'name': 'Hyderabad', 'latitude': 17.3753, 'longitude': 78.4744},
        ]
        
        cities = [city for city in cities if city['name'] not in all_cities]

        for city in cities:
            City.objects.create(**city)
        self.stdout.write(self.style.SUCCESS('Successfully added cities'))