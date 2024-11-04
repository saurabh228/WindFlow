#!/bin/bash

# Wait for the database to be ready
while !</dev/tcp/windflow_db/5432; do
  sleep 0.5
done

# Apply migrations
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput

# Create superuser if it doesn't already exist
python manage.py shell -c "
from django.contrib.auth import get_user_model;
User = get_user_model();
if not User.objects.filter(username='${DJANGO_SUPERUSER_USERNAME}').exists():
    User.objects.create_superuser('${DJANGO_SUPERUSER_USERNAME}', '${DJANGO_SUPERUSER_EMAIL}', '${DJANGO_SUPERUSER_PASSWORD}');
"

python manage.py setup_defaults
python manage.py backfill_daily_summary

# Start Celery worker and beat in the background
celery -A windflow_backend worker --loglevel=info &
celery -A windflow_backend beat --loglevel=info &

# Start the Daphne ASGI server
exec daphne -b 0.0.0.0 -p 8000 windflow_backend.asgi:application

