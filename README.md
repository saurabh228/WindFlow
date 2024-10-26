# WindFlow Weather Application

## Overview

WindFlow is a weather application that provides real-time weather updates, daily averages, and visualizations for multiple cities. The application includes features such as temperature unit conversion, setting update intervals, and displaying alerts.

## Features

- Real-time weather updates
- Daily averages with visualizations
- Temperature unit conversion (Celsius, Fahrenheit, Kelvin)
- Set update intervals for weather data
- Display alerts for weather conditions


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

- **Django**: The backend is built using Django for its robust and scalable architecture.
- **Django REST Framework**: For creating RESTful APIs.
- **drf-yasg**: For generating Swagger and Redoc documentation.
- **PostgreSQL**: Used as the database for storing weather data and user information.
- **Celery**: Used to schedule and run periodic tasks.
- **Redis**: Used to provie help to celery.

### Frontend

- **React**: The frontend is built using React for its component-based architecture and efficient rendering.
- **Chart.js**: Used for creating interactive and responsive charts.
- **React-Select**: For the city selection dropdown.
- **React-Toastify**: For displaying notifications and alerts.
- **CSS**: Custom CSS for styling the application with a dark and elegant theme.


### Workflow

#### Backend Workflow

1. **API Endpoints**: The backend exposes several API endpoints for fetching weather data, cities, and rollups. These endpoints are defined in `windflow_backend/windflow/urls.py` and handled by views in `windflow_backend/windflow/views.py`.

2. **Data Fetching**: The backend periodically fetches weather data from the OpenWeatherMap API using a scheduled task. This data is then processed and stored in the PostgreSQL database.

3. **Data Processing**: The data is processed to calculate daily averages and other relevant metrics. This processed data is then exposed through the API endpoints.

4. **WebSocket Notifications**: The backend uses WebSockets to send real-time notifications to the frontend. This is handled by the `Notifications` component in the frontend.

5. **Swagger and Redoc Documentation**: The backend provides API documentation using Swagger and Redoc, which can be accessed at `/swagger/` and `/redoc/` respectively.

#### Frontend Workflow

1. **City Selection**: The user selects a city from the dropdown menu. The selected city is stored in the state and used to fetch weather data for that city.

2. **Weather Data Display**: The current weather data and daily averages are displayed using charts and other UI components. The data is fetched from the backend API and processed in the frontend.

3. **Temperature Unit Conversion**: The user can switch between Celsius, Fahrenheit, and Kelvin. The temperature values are converted using the appropriate formulas and displayed accordingly.

4. **Alerts and Notifications**: The frontend displays alerts and notifications using React-Toastify. These alerts are fetched from the backend and displayed in real-time using WebSockets.
