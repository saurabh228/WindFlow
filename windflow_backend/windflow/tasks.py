from .utils import fetch_weather_data, update_daily_summary_for_today, check_thresholds
from .models import ConnectionStatus
from django.utils import timezone
from celery.utils.log import get_task_logger
from celery import shared_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json

logger = get_task_logger(__name__)

@shared_task
def fetch_weather_data_task():
    try:
        fetch_weather_data()
        weather_data = update_daily_summary_for_today()
        update_connection_status(True)
        logger.info('Successfully fetched weather data')
        send_weather(weather_data)
        alerts = check_thresholds()
        if alerts:
            send_alert(alerts)
            
    except Exception as e:
        update_connection_status(False)
        logger.error(f'Error fetching weather data: {e}')


def update_connection_status(success):
    status, created = ConnectionStatus.objects.get_or_create(id=1)
    if success:
        status.status = True
        status.last_successful_connection = timezone.now()
    else:
        status.status = False
    status.save()


def send_alert(alert):
    channel_layer = get_channel_layer()
    alert = json.dumps(alert)
    async_to_sync(channel_layer.group_send)(
        "notifications",
        {
            "type": "alert",
            "message": alert,
        }
    )

def send_weather(weather):
    channel_layer = get_channel_layer()
    weather = json.dumps(weather)
    async_to_sync(channel_layer.group_send)(
        "notifications",
        {
            "type": "weather",
            "message": weather,
        }
    )
