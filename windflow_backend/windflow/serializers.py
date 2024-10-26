from rest_framework import serializers
from .models import WeatherData, DailySummary, City, ConnectionStatus, TemperatureThreshold, HumidityThreshold, WindSpeedThreshold, ConditionThreshold

class WeatherDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeatherData
        fields = '__all__'

class DailySummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = DailySummary
        fields = '__all__'

class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = '__all__'

class ConnectionStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConnectionStatus
        fields = '__all__'

class TemperatureThresholdSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemperatureThreshold
        fields = '__all__'

class HumidityThresholdSerializer(serializers.ModelSerializer):
    class Meta:
        model = HumidityThreshold
        fields = '__all__'

class WindSpeedThresholdSerializer(serializers.ModelSerializer):
    class Meta:
        model = WindSpeedThreshold
        fields = '__all__'

class ConditionThresholdSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConditionThreshold
        fields = '__all__'