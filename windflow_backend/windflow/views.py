from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.pagination import PageNumberPagination
from django_celery_beat.models import PeriodicTask, IntervalSchedule
from .models import WeatherData, DailySummary, City, ConnectionStatus, TemperatureThreshold, HumidityThreshold, WindSpeedThreshold, ConditionThreshold
from .serializers import WeatherDataSerializer, DailySummarySerializer, CitySerializer, ConnectionStatusSerializer, TemperatureThresholdSerializer, HumidityThresholdSerializer, WindSpeedThresholdSerializer, ConditionThresholdSerializer
from .tasks import fetch_weather_data_task

@swagger_auto_schema(
    method='get',
    responses={
        200: openapi.Response('rollups/aggrigations',
            openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'count': openapi.Schema(type=openapi.TYPE_INTEGER, description='Total number of days'),
                    'next': openapi.Schema(type=openapi.TYPE_STRING, description='URL to the next page of results'),
                    'previous': openapi.Schema(type=openapi.TYPE_STRING, description='URL to the previous page of results'),
                    'results': openapi.Schema(
                        type=openapi.TYPE_OBJECT, description='Dictionary containing the list of rules for each city',
                    )
                }
            )
        ),
        400: openapi.Response('Bad Request', 
            openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
                }
            )
        ),
        500: openapi.Response('Internal server error', 
            openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
                }
            )
        )
    }
)
@api_view(['GET'])
def get_rollups(request):
    paginator = PageNumberPagination()
    paginator.page_size = 6
    cities = City.objects.all()
    padinated_rollups = {}
    try:
        for city in cities:
            rollups = DailySummary.objects.filter(city=city).order_by('-date')
            serialized_rollups = DailySummarySerializer(rollups, many=True).data
            padinated_rollups[city.name] = paginator.paginate_queryset(serialized_rollups, request)

        return paginator.get_paginated_response(padinated_rollups)
    except DailySummary.DoesNotExist as e:
        return Response(
            {'error':str(e)},
            status=status.HTTP_404_NOT_FOUND,
        )
    except Exception as e:
        return Response(
            {'error':str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    
@swagger_auto_schema(
    method='get',
    responses={
        200: openapi.Response('weather data',
            openapi.Schema(
                type=openapi.TYPE_OBJECT, description='Dictionary containing the list of latest weather data for each city',
            )
        ),
        400: openapi.Response('Bad Request', 
            openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
                }
            )
        ),
        404: openapi.Response('Not Found', 
            openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
                }
            )
        ),
        500: openapi.Response('Internal server error', 
            openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
                }
            )
        )
    }
)
@api_view(['GET'])
def get_current_weather(request):
    try:
        connection_status = ConnectionStatus.objects.get(pk=1)
        if connection_status.status == True:
            latest_weather_data = WeatherData.objects.order_by('city', '-dt').distinct('city')
            serialized_weather_data = WeatherDataSerializer(latest_weather_data, many=True)
            return Response(serialized_weather_data.data, status=status.HTTP_200_OK)
        else:
            return Response(
                {'error':f'server is not connected to the weather station {connection_status.status}'},
                status=status.HTTP_400_BAD_REQUEST,
            )
    except ConnectionStatus.DoesNotExist as e:
        return Response(
            {'error':str(e)},
            status=status.HTTP_404_NOT_FOUND,
        )
    except Exception as e:
        return Response(
            {'error':str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

@swagger_auto_schema(
    method='get',
    responses={
        200: openapi.Response('cities',
            openapi.Schema(
                type=openapi.TYPE_ARRAY, description='List of cities',
                items=openapi.Schema(type=openapi.TYPE_OBJECT, properties={
                    'name': openapi.Schema(type=openapi.TYPE_STRING, description='City name'),
                    'latitude': openapi.Schema(type=openapi.TYPE_NUMBER, description='City latitude'),
                    'longitude': openapi.Schema(type=openapi.TYPE_NUMBER, description='City longitude'),
                })
            )
        ),
        404: openapi.Response('Not Found', 
            openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
                }
            )
        ),
        500: openapi.Response('Internal server error', 
            openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
                }
            )
        )
    }
)
@api_view(['GET'])
def get_cities(request):
    try:
        cities = City.objects.all()
        serialized_cities = CitySerializer(cities, many=True)
        return Response(serialized_cities.data, status=status.HTTP_200_OK)
    except City.DoesNotExist as e:
        return Response(
            {'error':str(e)},
            status=status.HTTP_404_NOT_FOUND,
        )
    except Exception as e:
        return Response(
            {'error':str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

@swagger_auto_schema(
    method='get',
    responses={
        200: openapi.Response('connection status',
            openapi.Schema(
                type=openapi.TYPE_OBJECT, description='Connection status',
                properties={
                    'status': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Connection status'),
                    'last_successful_connection': openapi.Schema(type=openapi.TYPE_STRING, description='Last successful connection time'),
                }
            )
        ),
        404: openapi.Response('Not Found', 
            openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
                }
            )
        ),
        500: openapi.Response('Internal server error', 
            openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
                }
            )
        )
    }
)
@api_view(['GET'])
def check_connection_status(request):
    try:
        connection_status = ConnectionStatus.objects.get(pk=1)
        if connection_status.status == False:
            fetch_weather_data_task()
            connection_status = ConnectionStatus.objects.get(pk=1)
        serialized_connection_status = ConnectionStatusSerializer(connection_status)
        return Response(serialized_connection_status.data, status=status.HTTP_200_OK)
    except ConnectionStatus.DoesNotExist as e:
        return Response(
            {'error':str(e)},
            status=status.HTTP_404_NOT_FOUND,
        )
    except Exception as e:
        return Response(
            {'error':str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

@swagger_auto_schema(
    method='get',
    responses={
        200: openapi.Response('interval',
            openapi.Schema(
                type=openapi.TYPE_OBJECT, description='Current interval',
                properties={
                    'interval': openapi.Schema(type=openapi.TYPE_INTEGER, description='Interval in minutes'),
                }
            )
        ),
        404: openapi.Response('Not Found', 
            openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
                }
            )
        ),
        500: openapi.Response('Internal server error', 
            openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
                }
            )
        )
    }
)
@api_view(['GET'])
def get_interval(request):
    try:
        interval = IntervalSchedule.objects.values('period').get(pk=1)
        interval = int(interval)
        return Response({'interval': interval}, status=status.HTTP_200_OK)

    except IntervalSchedule.DoesNotExist as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_404_NOT_FOUND,
        )
    except ValueError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'interval': openapi.Schema(type=openapi.TYPE_INTEGER, description='Interval in minutes'),
        }
    ),
    responses={
        200: openapi.Response('Interval updated',
            openapi.Schema(
                type=openapi.TYPE_OBJECT, description='Updated interval',
                properties={
                    'interval': openapi.Schema(type=openapi.TYPE_INTEGER, description='Interval in minutes'),
                }
            )
        ),
        400: openapi.Response('Bad Request', 
            openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
                }
            )
        ),
        500: openapi.Response('Internal server error', 
            openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
                }
            )
        )
    }
)
@api_view(['POST'])
def set_interval(request):
    try:
        interval_value = request.data.get('interval')
        if interval_value is None:
            return Response(
                {'error': 'Interval value is required'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        interval_value = int(interval_value)
        if interval_value < 1:
            raise ValueError('Interval value must be greater')
        
        schedule, meow = IntervalSchedule.objects.update_or_create(
            id=1,
            defaults={
                'every':interval_value,
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

        return Response({'interval': interval_value}, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response(
            {'error': 'Interval value must be an integer'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

@swagger_auto_schema(
    method='get',
    responses={
        200: openapi.Response('thresholds',
            openapi.Schema(
                type=openapi.TYPE_OBJECT, description='Dictionary containing thresholds for each city')
        ),
        500: openapi.Response('Internal server error', 
            openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
                }
            )
        )
    }
)
@api_view(['GET'])
def get_thresholds(request):
    try:
        cities = City.objects.all()
        thresholds = {}
        for city in cities:
            thresholds[city.name] = {
                'temperature': TemperatureThresholdSerializer(TemperatureThreshold.objects.filter(city=city), many=True).data,
                'humidity': HumidityThresholdSerializer(HumidityThreshold.objects.filter(city=city), many=True).data,
                'wind_speed': WindSpeedThresholdSerializer(WindSpeedThreshold.objects.filter(city=city), many=True).data,
                'condition': ConditionThresholdSerializer(ConditionThreshold.objects.filter(city=city), many=True).data,
            }
        return Response(thresholds, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'city': openapi.Schema(type=openapi.TYPE_STRING, description='City name'),
            'temperature': openapi.Schema(type=openapi.TYPE_OBJECT, description='Temperature thresholds'),
            'humidity': openapi.Schema(type=openapi.TYPE_OBJECT, description='Humidity thresholds'),
            'wind_speed': openapi.Schema(type=openapi.TYPE_OBJECT, description='Wind speed thresholds'),
            'condition': openapi.Schema(type=openapi.TYPE_OBJECT, description='Condition thresholds'),
        }
    ),
    responses={
        200: openapi.Response('Thresholds updated',
            openapi.Schema(
                type=openapi.TYPE_OBJECT, description='Updated thresholds',
                properties={
                    'temperature': openapi.Schema(type=openapi.TYPE_OBJECT, description='Temperature thresholds'),
                    'humidity': openapi.Schema(type=openapi.TYPE_OBJECT, description='Humidity thresholds'),
                    'wind_speed': openapi.Schema(type=openapi.TYPE_OBJECT, description='Wind speed thresholds'),
                    'condition': openapi.Schema(type=openapi.TYPE_OBJECT, description='Condition thresholds'),
                }
            )
        ),
        400: openapi.Response('Bad Request', 
            openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
                }
            )
        ),
        404: openapi.Response('Not Found',
            openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
                }
            )
        ),
        500: openapi.Response('Internal server error', 
            openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
                }
            )
        )
    }
)
@api_view(['POST'])
def set_thresholds(request):
    try:
        city_name = request.data.get('city')
        if not city_name:
            return Response(
                {'error': 'City name is required'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        city = City.objects.get(name=city_name)

        temperature_data = request.data.get('temperature', {})
        humidity_data = request.data.get('humidity', {})
        wind_speed_data = request.data.get('wind_speed', {})
        condition_data = request.data.get('condition', {})

        tt, _ = TemperatureThreshold.objects.update_or_create(city=city, defaults=temperature_data)
        ht, _ = HumidityThreshold.objects.update_or_create(city=city, defaults=humidity_data)
        wt, _ = WindSpeedThreshold.objects.update_or_create(city=city, defaults=wind_speed_data)
        ct, _ = ConditionThreshold.objects.update_or_create(city=city, defaults=condition_data)

        thresholds = {
            'temperature': tt,
            'humidity': ht,
            'wind_speed': wt,
            'condition': ct,
        }

        return Response(thresholds, status=status.HTTP_200_OK)
    
    except ValueError as e:
        return Response(
            {'error': 'Invalid data provided for thresholds'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except City.DoesNotExist as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_404_NOT_FOUND,
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )