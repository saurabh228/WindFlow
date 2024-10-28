# WindFlow Weather Application

## Overview

WindFlow is a weather application that provides real-time weather updates, daily averages, and visualizations for multiple cities. The application includes features such as setting update intervals to fetch current weather details peroidically and set custom thresholds and get alerts when any threshold is crossed.

## Features

- Real-time weather updates.
- Daily averages with visualizations.
- Set update intervals for weather data.
- Set custom weather alerts for different weather weather conditions.


## Setup Instructions

### Docker Setup

1. **Clone the repository:**
   ```sh
   git clone https://github.com/saurabh228/windflow.git
   cd windflow
   ```

2. **Build and run the Docker containers:**
   ```sh
   docker-compose up --build
   ```

3. **Access the application:**
   - Frontend: [http://localhost:3000](http://localhost:3000)
   - Backend: [http://localhost:8000](http://localhost:8000)
   - Swagger Documentation: [http://localhost:8000/swagger/](http://localhost:8000/swagger/)


## Design Choices

### Backend

- **Django**: The backend is built using Django for its robust and scalable architecture. Django provides a powerful ORM, admin interface that provides a many usefull of features out of the box.
- **Django REST Framework**: DRF provides a flexible toolkit for building APIs and is well-suited for building web applications.
- **drf-yasg**: Used for generating Swagger and Redoc documentation for the API endpoints. it provides a clean and elegant way to document the API. can be accessed at `/swagger/` and `/redoc/` respectively.
- **PostgreSQL**: PostgreSQL is a powerful and scalable database that provides support for complex queries and data processing. It is used to store weather data, cities, and user settings.
- **Celery**: Celery is used for scheduling tasks to fetch weather data periodically and process the data. It provides a distributed task queue that can be used to run tasks in the background.
- **Redis**: Redis is used as a message broker for Celery to store task results and manage task queues.

### Frontend Demo

- **React**: React provides a fast and efficient way to build interactive user interfaces.
- **Chart.js**:  For displaying weather data in the form of charts.
- **React-Toastify**: For displaying alerts and notifications. alerts are fetched from the backend and displayed in real-time using WebSockets.
- **CSS**: Custom CSS for styling the application with a dark and elegant theme.


## Working

### Data Models

Django models are used to store weather data, cities, and user settings. The models are defined as follows:
- **City**: Stores information about cities to fetch from openweathermap API.
 It includes fields such as `name`, `latitude`, and `longitude`.
- **WeatherData**: Stores the current weather data fetched from the openweathermap API. It includes fields such as `city`, `temperature (°C)`, `humidity`, `wind speed`, `weather condition`, and `timestamp` etc.
- **DailySummary**: Stores the daily average weather data for each city. It includes fields such as `city`, `average temperature`, `average humidity`, `average wind speed`, `weather condition`, and `date` etc.
- **Thresholds**: These are 4 different models to store user-defined thresholds for temperature, humidity, wind speed, and weather condition. Each model includes fields such as `city`, `min_value`, `max_value`, and `consicutive counts`.
- **ConnectionStatus**: Stores the connection status of the backend server with the openweathermap API. It includes fields such as `status` and `last_updated`.

### Data Fetching
- **Current Weather Data**: Celery periodic tasks are used to fetch current weather data for each city on a user defined interval (default: 10 minutes) from the openweathermap API and stored in the `WeatherData` model. The `IntervalSchedule` & `PeriodicTask` models from celery are used to schedule the tasks, and are updated each time when user changes the interval.
- **Daily Averages/Rollups**: Since the openweathermap API does not provide historic data without a paid subscription, we are fetching 5 days forecast and using that data as past 5 days data and calculating daily avarages. If the historic data API is available that can be used to replace the forecast api in `windflow/management/commands/backfill_daily_summary.py` command.

### Setting Defaults
- **Default Cities**: Upon first run, the application adds the list of default cities to the empty database. The default cities are defined in the `windflow/management/commands/setup_defaults.py` file.
- **Default Weather Fetch Interval**: Celery IntervalSchedule and PeriodicTask are created with a default interval of 10 minutes to fetch weather data for each city. The interval can be changed by the user later through the `set-interval` API endpoint or the admin interface.

### Alerts & Peroiodic Weather Updates
- **Periodic Weather Updates**: The client registers a WebSocket connection with the backend to receive real-time updates for weather data. The backend sends updates to the client whenever new weather data is fetched.
- **Weather Alerts**: Users can set custom weather alerts for different weather conditions such as temperature, humidity, wind speed, and weather condition. Each time new weather data is fetched, the backend checks if any of the thresholds are crossed and sends an alert to the client if a threshold is crossed using the WebSocket connection.

### API Endpoints
- **/check-connection-status/**: Returns the connection status of the backend server with the openweathermap API.
- **/get-rollups/**: Returns the daily averages for each city with pagination. Each page contains the daily averages for a 6 days.
- **/current-weather/**: Returns the latest weather data for each city if the backend server is connected to the openweathermap API.
- **/get-cities/**: Returns the list of cities for which weather data is being fetched.
- **/get-interval/**: Returns the current interval for weather updates.
- **/set-interval/**: Sets the interval for weather updates.
- **/get-thresholds/**: Returns the current active user-defined thresholds for each city.
- **/set-thresholds/**: Sets the user-defined thresholds for each city.

All the API endpoints are documented using Swagger and can be accessed at `/swagger/` and `/redoc/`.
And the models can be managed using the Django admin interface at `/admin/`. Ther user can login using the default credentials mentioned in `docker-compose.yml` file.