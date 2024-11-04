from django.db import models
from django.core.exceptions import ValidationError

def validate_dominant_condition(value):
    if not isinstance(value, list) or len(value) != 3:
        raise ValidationError('dominant_condition must be a list of three elements.')
    for item in value:
        if not isinstance(item, list) or len(item) != 2:
            raise ValidationError('Each element in dominant_condition must be a pair (list of two elements).')
        
class WeatherData(models.Model):
    city = models.CharField(max_length=100)
    dominant_condition = models.CharField(max_length=100)
    temp = models.FloatField()
    feels_like = models.FloatField()
    dt = models.DateTimeField()
    humidity = models.FloatField()
    wind_speed = models.FloatField()
    wind_deg = models.FloatField()
    clouds = models.FloatField()

    def __str__(self):
        return f"{self.city} - {self.dominant_condition} at {self.dt}"

class DailySummary(models.Model):
    city = models.CharField(max_length=100)
    date = models.DateField()
    avg_temp = models.FloatField()
    max_temp = models.FloatField()
    min_temp = models.FloatField()
    avg_feels_like = models.FloatField()
    max_feels_like = models.FloatField()
    min_feels_like = models.FloatField()
    avg_humidity = models.FloatField()
    avg_wind_speed = models.FloatField()
    avg_wind_deg = models.FloatField()
    avg_clouds = models.FloatField()
    dominant_condition = models.JSONField(validators=[validate_dominant_condition], null=True, blank=True)

    def __str__(self):
        return f"{self.city} - {self.date}"
    
class City(models.Model):
    name = models.CharField(max_length=100, unique=True)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return self.name

class ConnectionStatus(models.Model):
    status = models.BooleanField(default=False)
    last_successful_connection = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Connection Status: {'Connected' if self.status else 'Disconnected'}"

class TemperatureThreshold(models.Model):
    city = models.CharField(max_length=100)
    min_threshold = models.FloatField(null=True, blank=True)
    max_threshold = models.FloatField(null=True, blank=True)
    consecutive_updates = models.IntegerField(default=3)

    def __str__(self):
        return f"Temperature Threshold for {self.city}: Min {self.min_threshold}°C, Max {self.max_threshold}°C"

class HumidityThreshold(models.Model):
    city = models.CharField(max_length=100)
    min_threshold = models.FloatField(null=True, blank=True)
    max_threshold = models.FloatField(null=True, blank=True)
    consecutive_updates = models.IntegerField(default=3)

    def __str__(self):
        return f"Humidity Threshold for {self.city}: Min {self.min_threshold}%, Max {self.max_threshold}%"

class WindSpeedThreshold(models.Model):
    city = models.CharField(max_length=100)
    min_threshold = models.FloatField(null=True, blank=True)
    max_threshold = models.FloatField(null=True, blank=True)
    consecutive_updates = models.IntegerField(default=3)

    def __str__(self):
        return f"Wind Speed Threshold for {self.city}: Wind Speed > Min {self.min_threshold} m/s, Max {self.max_threshold} m/s"

class ConditionThreshold(models.Model):
    city = models.CharField(max_length=100)
    condition = models.CharField(max_length=100)
    consecutive_updates = models.IntegerField(default=3)

    def __str__(self):
        return f"Condition Threshold for {self.city}: Condition = {self.condition}"



