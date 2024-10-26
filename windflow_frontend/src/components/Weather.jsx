import React, { useState, useEffect, useRef } from 'react';
import { 
  getRollUps, 
  getCurrentWeather, 
  getCities, 
  getThresholds, 
  setThresholds, 
  getWeatherFetchInterval, 
  setWeatherFetchInterval, 
  checkWeatherAPIConnection 
} from '../services/api';
import { ClipLoader } from 'react-spinners';
import Select from 'react-select';
import { Line, Bar } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, BarElement } from 'chart.js';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import './Weather.css';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, BarElement, Title, Tooltip, Legend);

const Weather = () => {
  const [loading, setLoading] = useState(true);
  const [connectionError, setConnectionError] = useState(false);
  const [apiConnected, setApiConnected] = useState(true);
  const [cities, setCities] = useState([]);
  const [selectedCity, setSelectedCity] = useState(null);
  const [currentWeather, setCurrentWeather] = useState(null);
  const [rollUps, setRollUps] = useState([]);
  const [interval, setInterval] = useState(10);
  const [temperatureUnit, setTemperatureUnit] = useState('C');
  const [userAlerts, setUserAlerts] = useState([]); // User-defined alerts
  const [alerts, setAlerts] = useState([]); // Alerts from the server
  const chartRef1 = useRef(null);
  const chartRef2 = useRef(null);
  const chartRef3 = useRef(null);
  const chartRef4 = useRef(null);
  const [chartData, setChartData] = useState(null);

  useEffect(() => {

    const fetchRollUps = async () => {
      try {
        const response = await getRollUps();
        const new_rollups = {};
        for (const [city, entries] of Object.entries(response.results)) {
          const rollUp = {
            date: [],
            avg_temp: [],
            max_temp: [],
            min_temp: [],
            avg_feels_like: [],
            max_feels_like: [],
            min_feels_like: [],
            avg_humidity: [],
            avg_wind_speed: [],
            avg_wind_deg: [],
            dominant_condition: [],
          };
          for(const entry of entries){
            rollUp.date.push(entry.date);
            rollUp.avg_temp.push(entry.avg_temp);
            rollUp.max_temp.push(entry.max_temp);
            rollUp.min_temp.push(entry.min_temp);
            rollUp.avg_feels_like.push(entry.avg_feels_like);
            rollUp.max_feels_like.push(entry.max_feels_like);
            rollUp.min_feels_like.push(entry.min_feels_like);
            rollUp.avg_humidity.push(entry.avg_humidity);
            rollUp.avg_wind_speed.push(entry.avg_wind_speed);
            rollUp.avg_wind_deg.push(entry.avg_wind_deg);
            rollUp.dominant_condition.push(entry.dominant_condition);
          }
          new_rollups[city] = rollUp;
        }
        setRollUps(new_rollups);

      } catch (error) {
        console.error('Error fetching daily summaries:', error);
        setConnectionError(true);
      }
    }
    const fetchCurrentWeather = async () => {
      try {
        const response = await getCurrentWeather();
        const new_weather = {};
        for(const data of response){
          new_weather[data.city]={
            date:data.dt,
            temp:data.temp,
            feels_like:data.feels_like,
            humidity:data.humidity,
            wind_speed:data.wind_speed,
            wind_deg:data.wind_deg,
            condition:data.dominant_condition
          }
          
        }
        setCurrentWeather(new_weather);
      } catch (error) {
        console.error('Error fetching current weather:', error);
        setConnectionError(true);
      }
    }
    const fetchCities = async () => {
      try {
        const response = await getCities();
        const all_cities = [];
        for(const data of response){
          all_cities.push(data.name);
        }
        setCities(all_cities);
        setSelectedCity({value:all_cities[0], label:all_cities[0]});
      } catch (error) {
        console.error('Error fetching cities:', error);
      }
    }

    fetchRollUps();
    fetchCurrentWeather();
    fetchCities();
  }, []);

  const handleSetInterval = async (e) => {
    if(e.key !== 'Enter') return;
    if (e.value < 1) {
      toast.error('Interval must be greater than 0');
      e.value = interval;
      return;
    }
    
    try {
      await setWeatherFetchInterval(e.value);
      setInterval(e.value);
      toast.success('Interval updated successfully');
    } catch (error) {
      toast.error('Error updating interval');
    }
  };

  const handleTemperatureUnitChange = (unit) => {
    setTemperatureUnit(unit);
  };

  if (rollUps.length === 0 || !currentWeather || cities.length === 0) {
    return (
      <div className="loading">
        <ClipLoader size={250} />
      </div>
    );
  }

  const getWindDirection = (degree) => {
    const directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW'];
    const index = Math.round(degree / 22.5) % 16;
    return directions[index];
  };

  return (
    <div className="container">
      <h1 style={{ color: '#ceceeb', fontFamily: 'cursive' }}>Windflow Weather App</h1>
      <div className="select-container">
        <h2>Select City</h2>
        <Select
          className='select-element'
          value={selectedCity}
          onChange={(selected) => setSelectedCity(selected)}
          options={cities.map(city => ({ value: city, label: city }))}
        />
      </div>
        <h2>Current Weather</h2>
      <div className="current-weather-container">
        <div className="current-weather-box">
          {currentWeather ? (
            <>
              <p><strong>Temperature:</strong> {temperatureUnit === 'C' ? currentWeather[selectedCity.value].temp.toFixed(2) : temperatureUnit === 'F' ? (currentWeather[selectedCity.value].temp * 9/5 + 32).toFixed(2) : (currentWeather[selectedCity.value].temp + 273.15).toFixed(2)} °{temperatureUnit}</p>
              <p><strong>Feels Like:</strong> {temperatureUnit === 'C' ? currentWeather[selectedCity.value].feels_like.toFixed(2) : temperatureUnit === 'F' ? (currentWeather[selectedCity.value].feels_like * 9/5 + 32).toFixed(2) : (currentWeather[selectedCity.value].feels_like + 273.15).toFixed(2)} °{temperatureUnit}</p>
              <p><strong>Humidity:</strong> {currentWeather[selectedCity.value].humidity.toFixed(2)} %</p>
              <p><strong>Wind Speed:</strong> {currentWeather[selectedCity.value].wind_speed.toFixed(2)} m/s</p>
              <p><strong>Wind Direction:</strong> {getWindDirection(currentWeather[selectedCity.value].wind_deg)}</p>
              <p><strong>Condition:</strong> {currentWeather[selectedCity.value].condition}</p>
            </>
          ) : 'Loading...'}
        </div>
        <div className="temperature-buttons">
          <button 
            onClick={() => handleTemperatureUnitChange('C')} 
            className={temperatureUnit === 'C' ? 'active' : ''}
          >
            C
          </button>
          <button 
            onClick={() => handleTemperatureUnitChange('F')} 
            className={temperatureUnit === 'F' ? 'active' : ''}
          >
            F
          </button>
          <button 
            onClick={() => handleTemperatureUnitChange('K')} 
            className={temperatureUnit === 'K' ? 'active' : ''}
          >
            K
          </button>
        </div>
        <div className='weather-update'>
        <h2>Weather Update Interval : </h2>
        <div className='interval-input'>
          <input
            type="number"
            defaultValue={interval}
            onKeyDown={(e) => handleSetInterval(e)}
            onBlur={(e) => handleSetInterval(e)}
            />
        </div>
      </div>
      </div>
      <div>
        <h2>Daily Averages</h2>
        <div className='chart-container'>
          <Line 
            ref={chartRef1}
            data={{
            labels: rollUps[selectedCity.value]?.date || [],
            datasets: [{
              label: 'Temperature',
              data: rollUps[selectedCity.value]?.avg_temp.map(temp => temp.toFixed(2)) || [],
              borderColor: 'rgba(75,192,192,1)',
              borderWidth: 2,
            },
            {
              label: 'Feels Like',
              data: rollUps[selectedCity.value]?.avg_feels_like.map(temp => temp.toFixed(2)) || [],
              borderColor: 'rgba(192,75,192,1)',
              borderWidth: 2,
            }
          ]
          }}
          options={{
            maintainAspectRatio: false,
          }}
          height={400}
          width={600}
          />
        </div>

        <div className="chart-container">
        <div className="chart">
          <h2>Humidity</h2>
          <Bar 
            ref={chartRef2}
            data={{
              labels: rollUps[selectedCity.value]?.date || [],
              datasets: [{
                label: 'Humidity',
                data: rollUps[selectedCity.value]?.avg_humidity.map(humidity => humidity.toFixed(2)) || [],
                backgroundColor: 'rgba(192,192,75,1)',
                borderWidth: 2,
              }]
            }}
          />
        </div>
        <div className="chart">
          <h2>Wind Speed</h2>
          <Bar 
            ref={chartRef3}
            data={{
              labels: rollUps[selectedCity.value]?.date || [],
              datasets: [{
                label: 'Wind Speed',
                data: rollUps[selectedCity.value]?.avg_wind_speed.map(speed => speed.toFixed(2)) || [],
                backgroundColor: 'rgba(192,75,75,1)',
                borderWidth: 2,
              }]
            }}
          />
        </div>
      </div>

      </div>
      <div>
        <h2>Thresholds</h2>
        {/* Add form to add thresholds */}
      </div>
      <div className="alerts-container">
        <h2>Alerts</h2>
        {alerts.map((alert, index) => (
          <div key={index} className="alert">
            <p>{alert.message}</p>
          </div>
        ))}
      </div>
      <ToastContainer />
    </div>
  );
};

export default Weather;