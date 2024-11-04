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
        weather_data = fetch_weather_data()
        updated_data = update_daily_summary_for_today()
        update_connection_status(True)
        logger.info('Successfully fetched weather data')
        alerts = check_thresholds()

        notification_data = {
            'weather': weather_data,
            'roll_ups': updated_data,
            'alerts': alerts
        }
        send_weather(notification_data)
            
    except Exception as e:
        update_connection_status(False)
        print("error",e)
        logger.error(f'Error fetching weather data: {e}')


def update_connection_status(success):
    status, created = ConnectionStatus.objects.get_or_create(id=1)
    if success:
        status.status = True
        status.last_successful_connection = timezone.now()
    else:
        status.status = False
    status.save()


def send_weather(data):
    channel_layer = get_channel_layer()
    data = json.dumps(data)
    async_to_sync(channel_layer.group_send)(
        "notifications",
        {
            "type": "weather",
            "message": data,
        }
    )
