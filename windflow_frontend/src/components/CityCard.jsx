import React, {useState} from 'react';
import { Line, Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import './CityCard.css';

// Register the required components and scales
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend
);

const CityCard = ({ city, weather, rollUps, interval, handleSetInterval }) => {
  const [temperatureUnit, setTemperatureUnit] = useState('C');
  if (!weather || !rollUps) return null;


  const getWindDirection = (degree) => {
    const directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW'];
    const index = Math.round(degree / 22.5) % 16;
    return directions[index];
  };

  return (
    <div className="city-card">
      <div className="city-card-header">
        <h2>{city}</h2>
        <p><strong>Temperature:</strong> {temperatureUnit === 'C' ? weather.temp.toFixed(2) : temperatureUnit === 'F' ? (weather.temp * 9/5 + 32).toFixed(2) : (weather.temp + 273.15).toFixed(2)} °{temperatureUnit}</p>
        <p><strong>Feels Like:</strong> {temperatureUnit === 'C' ? weather.feels_like.toFixed(2) : temperatureUnit === 'F' ? (weather.feels_like * 9/5 + 32).toFixed(2) : (weather.feels_like + 273.15).toFixed(2)} °{temperatureUnit}</p>
        <p><strong>Humidity:</strong> {weather.humidity.toFixed(2)} %</p>
        <p><strong>Wind Speed:</strong> {weather.wind_speed.toFixed(2)} m/s</p>
        <p><strong>Wind Direction:</strong> {getWindDirection(weather.wind_deg)}</p>
        <p><strong>Condition:</strong> {weather.condition}</p>
        <div className="temperature-buttons">
          <button onClick={() => setTemperatureUnit('C')} className={temperatureUnit === 'C' ? 'active' : ''}>C</button>
          <button onClick={() => setTemperatureUnit('F')} className={temperatureUnit === 'F' ? 'active' : ''}>F</button>
          <button onClick={() => setTemperatureUnit('K')} className={temperatureUnit === 'K' ? 'active' : ''}>K</button>
        </div>
        <div className="weather-container">
          <div className="weather-box">
            <div className="weather-top">
              <h2>Updating current weather:</h2>
              <h2>Every {interval.every} {interval.period}</h2>
            </div>
            <div className="weather-bottom">
              <h2>Set new interval:</h2>
              <input
                type="number"
                defaultValue={null}
                onKeyDown={handleSetInterval}
                onBlur={handleSetInterval}
              />
            </div>
          </div>
        </div>
      </div>
      <div className="city-card-body">
        <div className="chart-container">
          <Line
            data={{
              labels: rollUps.date,
              datasets: [
                {
                  label: 'Temperature',
                  data: rollUps.avg_temp.map(temp => temp.toFixed(2)),
                  borderColor: 'rgba(75,192,192,1)',
                  borderWidth: 2,
                },
                {
                  label: 'Feels Like',
                  data: rollUps.avg_feels_like.map(temp => temp.toFixed(2)),
                  borderColor: 'rgba(192,75,192,1)',
                  borderWidth: 2,
                }
              ]
            }}
            options={{ maintainAspectRatio: true }}

          />
          <div className='bar-container'>
            <div className='bar-chart'>
              <Bar
                data={{
                  labels: rollUps.date.map(dateString => dateString.split('-')[2]),
                  datasets: [
                    {
                      label: 'Humidity',
                      data: rollUps.avg_humidity.map(humidity => humidity.toFixed(2)),
                      backgroundColor: 'rgba(192,192,75,1)',
                      borderWidth: 2,
                    }
                  ]
                }}
                options={{ maintainAspectRatio: true }}
              />
            </div>
            <div className='bar-chart'>
              <Bar
                data={{
                  labels: rollUps.date.map(dateString => dateString.split('-')[2]),
                  datasets: [
                    {
                      label: 'Wind Speed',
                      data: rollUps.avg_wind_speed.map(speed => speed.toFixed(2)),
                      backgroundColor: 'rgba(192,75,75,1)',
                      borderWidth: 2,
                    }
                  ]
                }}
                options={{ maintainAspectRatio: true }}
              />
            </div>
          </div>
          <div className='label-description'>Day of the month</div>
        </div>
      </div>
    </div>
  );
};

export default CityCard;