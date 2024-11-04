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
    paginated_rollups = {}
    try:
        for city in cities:
            rollups = DailySummary.objects.filter(city=city).order_by('-date')
            serialized_rollups = DailySummarySerializer(rollups, many=True).data
            paginated_rollups[city.name] = paginator.paginate_queryset(serialized_rollups, request)

        return paginator.get_paginated_response(paginated_rollups)
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
        if connection_status.status == False:
            fetch_weather_data_task()
            connection_status = ConnectionStatus.objects.get(pk=1)
        if connection_status.status == True:
            latest_weather_data = WeatherData.objects.order_by('city', '-dt').distinct('city')

            if not latest_weather_data.exists():
                fetch_weather_data_task()
                connection_status = ConnectionStatus.objects.get(pk=1)
                if connection_status.status == True:
                    latest_weather_data = WeatherData.objects.order_by('city', '-dt').distinct('city')
                else:
                    return Response(
                        {'error':f'server is not connected to the weather station {connection_status.status}'},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
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
        interval = IntervalSchedule.objects.values('every', 'period').get(pk=1)
        # every = int(interval['every'])
        return Response(interval, status=status.HTTP_200_OK)

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
    print("incoming request", request.data, flush=True)
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

        thresholds = {}

        if temperature_data:
            tt, _ = TemperatureThreshold.objects.update_or_create(city=city, defaults={"min_threshold": temperature_data.get('min_threshold') if temperature_data.get('min_threshold') else None, "max_threshold": temperature_data.get('max_threshold') if temperature_data.get('max_threshold') else None, "consecutive_updates": temperature_data.get('consecutive_updates') if temperature_data.get('consecutive_updates') else 3})
            thresholds['temperature'] = TemperatureThresholdSerializer(tt).data
        if humidity_data:
            ht, _ = HumidityThreshold.objects.update_or_create(city=city, defaults={"min_threshold": humidity_data.get('min_threshold') if humidity_data.get('min_threshold') else None, "max_threshold": humidity_data.get('max_threshold') if humidity_data.get('max_threshold') else None, "consecutive_updates": humidity_data.get('consecutive_updates') if humidity_data.get('consecutive_updates') else 3})
            thresholds['humidity'] = HumidityThresholdSerializer(ht).data
        if wind_speed_data:
            wt, _ = WindSpeedThreshold.objects.update_or_create(city=city, defaults={"min_threshold": wind_speed_data.get('min_threshold') if wind_speed_data.get('min_threshold') else None, "max_threshold": wind_speed_data.get('max_threshold') if wind_speed_data.get('max_threshold') else None, "consecutive_updates": wind_speed_data.get('consecutive_updates') if wind_speed_data.get('consecutive_updates') else 3})
            thresholds['wind_speed'] = WindSpeedThresholdSerializer(wt).data
        if condition_data:
            ct, _ = ConditionThreshold.objects.update_or_create(city=city, defaults={"condition": condition_data.get('condition') if condition_data.get('condition') else None, "consecutive_updates": condition_data.get('consecutive_updates') if condition_data.get('consecutive_updates') else 3})
            thresholds['condition'] = ConditionThresholdSerializer(ct).data
    

        return Response(thresholds, status=status.HTTP_200_OK)
    
    except ValueError as e:
        print("error aa gya oye", flush=True)
        print(e, flush=True)
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
        print("error aa gya oye", flush=True)
        print(e, flush=True)
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@swagger_auto_schema(
    method='delete',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'type': openapi.Schema(type=openapi.TYPE_STRING, description='Threshold type'),
            'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Threshold ID'),
        }
    ),
    responses={
        200: openapi.Response('Threshold deleted',
            openapi.Schema(
                type=openapi.TYPE_OBJECT, description='Threshold deleted successfully'
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
@api_view(['DELETE'])
def delete_threshold(request):
    print("incoming request", request.data, flush=True)
    threshold_type = request.data.get('type')
    threshold_id = request.data.get('id')

    if not threshold_type or not threshold_id:
        return Response(
            {'error': 'Type and ID are required', 'data': request.data},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        if threshold_type == 'temperature':
            threshold = TemperatureThreshold.objects.get(id=threshold_id)
        elif threshold_type == 'humidity':
            threshold = HumidityThreshold.objects.get(id=threshold_id)
        elif threshold_type == 'wind_speed':
            threshold = WindSpeedThreshold.objects.get(id=threshold_id)
        elif threshold_type == 'condition':
            threshold = ConditionThreshold.objects.get(id=threshold_id)
        else:
            return Response(
                {'error': 'Invalid threshold type'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        threshold.delete()
        return Response(
            {'message': 'Threshold deleted successfully'},
            status=status.HTTP_200_OK,
        )
    except TemperatureThreshold.DoesNotExist:
        return Response(
            {'error': 'Temperature threshold not found'},
            status=status.HTTP_404_NOT_FOUND,
        )
    except HumidityThreshold.DoesNotExist:
        return Response(
            {'error': 'Humidity threshold not found'},
            status=status.HTTP_404_NOT_FOUND,
        )
    except WindSpeedThreshold.DoesNotExist:
        return Response(
            {'error': 'Wind speed threshold not found'},
            status=status.HTTP_404_NOT_FOUND,
        )
    except ConditionThreshold.DoesNotExist:
        return Response(
            {'error': 'Condition threshold not found'},
            status=status.HTTP_404_NOT_FOUND,
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )