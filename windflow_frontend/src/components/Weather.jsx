import React, { useState, useEffect, useRef } from 'react';
import { 
  getRollUps, 
  getCurrentWeather, 
  getCities, 
  getThresholds, 
  setThresholds, 
  getWeatherFetchInterval, 
  setWeatherFetchInterval, 
  checkWeatherAPIConnection,
  deleteThreshold
} from '../services/api';
import { ClipLoader } from 'react-spinners';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import './Weather.css';
import Carousel from './Carousel';
import Notifications from '../services/notification';

const Weather = () => {
  const [loading, setLoading] = useState(true);
  const [connectionError, setConnectionError] = useState(false);
  const [apiConnected, setApiConnected] = useState(true);
  const [cities, setCities] = useState([]);
  const [selectedCity, setSelectedCity] = useState(null);
  const [currentWeather, setCurrentWeather] = useState(null);
  const [rollUps, setRollUps] = useState([]);
  const [interval, setInterval] = useState({'every':10, 'period':'minutes'});
  const [temperatureUnit, setTemperatureUnit] = useState('C');
  const [userThresholds, setUserThresholds] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const alertsRef = useRef(alerts);
  const [thresholdForm, setThresholdForm] = useState({
    city: '',
    temperature: { min_threshold: '', max_threshold: '', consecutive_updates: '' },
    humidity: { min_threshold: '', max_threshold: '', consecutive_updates: '' },
    wind_speed: { min_threshold: '', max_threshold: '', consecutive_updates: '' },
    condition: { condition: '', consecutive_updates: '' },
  });
  const [showFields, setShowFields] = useState({
    temperature: false,
    humidity: false,
    wind_speed: false,
    condition: false,
  });

  useEffect(() => {
    console.log('rollUps:', rollUps);
  }, [rollUps]);

  useEffect(() => {
    alertsRef.current = alerts;
  }, [alerts]);


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
    };

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
    };

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
    };

    const fetchThresholds = async () => {
      try {
        const response = await getThresholds();
        setUserThresholds(response);
        // console.log("thresholds", response);
      } catch (error) {
        console.error('Error fetching thresholds:', error);
      }
    };

    const fetchWeatherFetchInterval = async () => {
      try {
        const response = await getWeatherFetchInterval();
        setInterval(response);
      } catch (error) {
        console.error('Error fetching weather fetch interval:', error);
      }
    };

    fetchRollUps();
    fetchCurrentWeather();
    fetchCities();
    fetchThresholds();
    fetchWeatherFetchInterval();
  }, []);

  const handleSetInterval = async (e) => {
    if((e.key !== 'Enter' && e.type !== 'blur') || (e.type ==='blur' && !e.target.value)) return;


    const newInterval = parseInt(e.target.value);
    if (isNaN(newInterval) || newInterval < 1) {
      toast.error('Please enter a valid number greater than 0');
      e.target.value = null;
      return
    }
    
    try {
      await setWeatherFetchInterval(newInterval);
      setInterval({'every':e.target.value, 'period':'minutes'});
      toast.success('Interval updated successfully');
      e.target.value = null;
      // const onBlurFunction = e.target.onblur;
      // e.target.onblur = null;
      e.target.blur();
      // e.target.onblur = onBlurFunction;
    } catch (error) {
      toast.error('Error updating interval');
    }
  };

  const handleAlertsNotification = (newAlerts) => {
      const alertMessages = [];
  
      newAlerts.forEach((alert) => {
        let alertMessage = '';
        const { breach, city, threshold, consecutive_updates, difference } = alert;
        const diff = Math.abs(difference).toFixed(2);
  
        switch (alert.type) {
          case 'Temperature':
            alertMessage = `Temperature in ${city} has been ${breach} the threshold of ${threshold}°C by ${diff}°C for the last ${consecutive_updates} readings.`;
            break;
          case 'Humidity':
            alertMessage = `Humidity in ${city} has been ${breach} the threshold of ${threshold}% by ${diff}% for the last ${consecutive_updates} readings.`;
            break;
          case 'Wind Speed':
            alertMessage = `Wind speed in ${city} has been ${breach} the threshold of ${threshold} m/s by ${diff} m/s for the last ${consecutive_updates} readings.`;
            break;
          case 'Condition':
            alertMessage = `Condition in ${city} has remained '${threshold}' for the last ${consecutive_updates} readings.`;
            break;
          default:
            alertMessage = `Alert for ${city}: ${breach} threshold of ${threshold}.`;
        }
        alertMessages.push(alertMessage);
        
        if(!alertsRef.current.includes(alertMessage)){
          toast.warning(alertMessage);
        }
      });
  
      setAlerts(alertMessages);
  };

  const handleRollupsNotification = (newRollUps) => {
    const updatedRollUps = { ...rollUps };
  
    for (const [city, entries] of Object.entries(newRollUps)) {
      const {date, avg_temp, max_temp, min_temp, avg_feels_like, max_feels_like, min_feels_like, avg_humidity, avg_wind_speed, avg_wind_deg, dominant_condition } = entries;
      const index = updatedRollUps[city].date.indexOf(date);

      if (!updatedRollUps[city]) {
        updatedRollUps[city] = {
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
      }

      if (index === -1) {
        updatedRollUps[city].date.push(date);
        updatedRollUps[city].avg_temp.push(avg_temp);
        updatedRollUps[city].max_temp.push(max_temp);
        updatedRollUps[city].min_temp.push(min_temp);
        updatedRollUps[city].avg_feels_like.push(avg_feels_like);
        updatedRollUps[city].max_feels_like.push(max_feels_like);
        updatedRollUps[city].min_feels_like.push(min_feels_like);
        updatedRollUps[city].avg_humidity.push(avg_humidity);
        updatedRollUps[city].avg_wind_speed.push(avg_wind_speed);
        updatedRollUps[city].avg_wind_deg.push(avg_wind_deg);
        updatedRollUps[city].dominant_condition.push(dominant_condition);
      }else {
        // Date found in the array, replace the existing values
        updatedRollUps[city].date[index] = date;
        updatedRollUps[city].avg_temp[index] = avg_temp;
        updatedRollUps[city].max_temp[index] = max_temp;
        updatedRollUps[city].min_temp[index] = min_temp;
        updatedRollUps[city].avg_feels_like[index] = avg_feels_like;
        updatedRollUps[city].max_feels_like[index] = max_feels_like;
        updatedRollUps[city].min_feels_like[index] = min_feels_like;
        updatedRollUps[city].avg_humidity[index] = avg_humidity;
        updatedRollUps[city].avg_wind_speed[index] = avg_wind_speed;
        updatedRollUps[city].avg_wind_deg[index] = avg_wind_deg;
        updatedRollUps[city].dominant_condition[index] = dominant_condition;
      }
    }
  
    setRollUps(updatedRollUps);
  };


  const handleThresholdChange = (e) => {
    const { name, value } = e.target;
    const [category, field] = name.split('-');
    setThresholdForm((prevForm) => ({
      ...prevForm,
      [category]: {
        ...prevForm[category],
        [field]: value,
      },
    }));
  };

  const handleCityChange = (e) => {
    setThresholdForm((prevForm) => ({
      ...prevForm,
      city: e.target.value,
    }));
  };

  const handleThresholdSubmit = async (e) => {
    e.preventDefault();
    const { city, temperature, humidity, wind_speed, condition } = thresholdForm;
    
    if (!city) {
      toast.error('Please select a city');
      return;
    }

    const isTemperatureValid = (temperature.min_threshold || temperature.max_threshold) && (!temperature.min_threshold || !temperature.max_threshold || parseFloat(temperature.min_threshold) < parseFloat(temperature.max_threshold)) && parseInt(temperature.consecutive_updates) > 0;
    const isHumidityValid = (humidity.min_threshold || humidity.max_threshold) && (!humidity.min_threshold || !humidity.max_threshold || parseFloat(humidity.min_threshold) < parseFloat(humidity.max_threshold)) && parseInt(humidity.consecutive_updates) > 0;
    const isWindSpeedValid = (wind_speed.min_threshold || wind_speed.max_threshold) && (!wind_speed.min_threshold || !wind_speed.max_threshold || parseFloat(wind_speed.min_threshold) < parseFloat(wind_speed.max_threshold)) && parseInt(wind_speed.consecutive_updates) > 0;
    const isConditionValid = condition.condition && parseInt(condition.consecutive_updates) > 0;

    if (!isTemperatureValid && !isHumidityValid && !isWindSpeedValid && !isConditionValid) {
      toast.error('Please provide valid thresholds');
      return;
    }

    try {
      const request = {}
      request["city"] = city;
      if(isTemperatureValid){
        request["temperature"] = temperature;
      }
      if(isHumidityValid){
        request["humidity"] = humidity;
      }
      if(isWindSpeedValid){
        request["wind_speed"] = wind_speed;
      }
      if(isConditionValid){
        request["condition"] = condition;
      }
      // console.log("request", request);

      await setThresholds(request);
      toast.success('Thresholds updated successfully');

      const response = await getThresholds();
      setThresholdForm({
        city: '',
        temperature: { min_threshold: '', max_threshold: '', consecutive_updates: '' },
        humidity: { min_threshold: '', max_threshold: '', consecutive_updates: '' },
        wind_speed: { min_threshold: '', max_threshold: '', consecutive_updates: '' },
        condition: { condition: '', consecutive_updates: '' },
      });
      setShowFields({
        temperature: false,
        humidity: false,
        wind_speed: false,
        condition: false,
      });

      setUserThresholds(response);
    } catch (error) {
      toast.error('Error updating thresholds');
    }
  };

  const handleShowFields = (field) => {
    if (field === 'temperature' && showFields.temperature || field === 'humidity' && showFields.humidity || field === 'wind_speed' && showFields.wind_speed ) {
      setThresholdForm((prevForm) => ({
        ...prevForm,
        [field]: { min_threshold: '', max_threshold: '', consecutive_updates: ''},
      }));
    } else if (field === 'condition' && showFields.condition) {
      setThresholdForm((prevForm) => ({
        ...prevForm,
        [field]: {condition: '', consecutive_updates: ''}
      }));
    }
    setShowFields((prevFields) => ({
      ...prevFields,
      [field]: !prevFields[field],
    }));
  };

  const handleDeleteThreshold = async (type, id) => {
    try {
      await deleteThreshold( type, id);
      toast.success('Threshold deleted successfully');
      // refetch thresholds to update the UI
      const response = await getThresholds();
      setUserThresholds(response);
    } catch (error) {
      toast.error('Error deleting threshold');
    }
  };



  if (rollUps.length === 0 || !currentWeather || cities.length === 0) {
    return (
      <div className="loading">
        <ClipLoader size={250} />
      </div>
    );
  }

  return (
    <div className="container">
      <h1 style={{ color: '#ceceeb', fontFamily: 'cursive' }}>Windflow Weather App</h1>
      <div className='main-container'>
        <Carousel
          cities={cities}
          currentWeather={currentWeather}
          rollUps={rollUps}
          interval={interval}
          handleSetInterval={handleSetInterval}
        />
      </div>
      <div className="alerts-container">
        <h2>Alerts</h2>
        {alerts.map((alert, index) => (
            <div key={index} className="alert">
              <p>{alert}</p>
            </div>
          ))}
      </div>
      <div >
        <h2>Thresholds</h2>
        {Object.entries(userThresholds).map(([city, thresholds]) => (
          <div key={city} className="thresholds-container">
            {Object.entries(thresholds).map(([type, values]) => (
              values.length > 0 && (
                <div key={type}>
                  <h3>{city}</h3>
                  <h4>{type.charAt(0).toUpperCase() + type.slice(1)}</h4>
                  <ul>
                    {values.map((threshold) => (
                      <li key={threshold.id}>
                        {type === 'temperature' && (
                          <>
                            {threshold.min_threshold !== null && `Min: ${threshold.min_threshold}°C`}
                            {threshold.max_threshold !== null && `, Max: ${threshold.max_threshold}°C`}
                            {`, Consecutive Updates: ${threshold.consecutive_updates}`}
                          </>
                        )}
                        {type === 'humidity' && (
                          <>
                            {threshold.min_threshold !== null && `Min: ${threshold.min_threshold}%`}
                            {threshold.max_threshold !== null && `, Max: ${threshold.max_threshold}%`}
                            {`, Consecutive Updates: ${threshold.consecutive_updates}`}
                          </>
                        )}
                        {type === 'wind_speed' && (
                          <>
                            {threshold.min_threshold !== null && `Min: ${threshold.min_threshold} m/s`}
                            {threshold.max_threshold !== null && `, Max: ${threshold.max_threshold} m/s`}
                            {`, Consecutive Updates: ${threshold.consecutive_updates}`}
                          </>
                        )}
                        {type === 'condition' && `Condition: ${threshold.condition}, Consecutive Updates: ${threshold.consecutive_updates}`}
                        <button onClick={() => handleDeleteThreshold(type, threshold.id)}>Delete</button>
                      </li>
                    ))}
                  </ul>
                </div>
              )
            ))}
            </div>
        ))}        
      </div>
      <div className='form-container'>
        <h2>Add/Update Thresholds</h2>
        <form onSubmit={handleThresholdSubmit}>
          <div>
            <label>City:</label>
            <select name="city" value={thresholdForm.city} onChange={handleCityChange}>
              <option value="">Select a city</option>
              {cities.map((city) => (
                <option key={city} value={city}>{city}</option>
              ))}
            </select>
          </div>
          <div>
            <button type="button" onClick={() => handleShowFields('temperature')}>{showFields.temperature ? "Cancel" : "Add Temperature"}</button>
            {showFields.temperature && (
              <div>
                <h3>Temperature (°C)</h3>
                <label>Min Threshold:</label>
                <input
                  type="number"
                  name="temperature-min_threshold"
                  value={thresholdForm.temperature.min_threshold}
                  onChange={handleThresholdChange}
                />
                <label>Max Threshold:</label>
                <input
                  type="number"
                  name="temperature-max_threshold"
                  value={thresholdForm.temperature.max_threshold}
                  onChange={handleThresholdChange}
                />
                <label>Consecutive Updates:</label>
                <input
                  type="number"
                  name="temperature-consecutive_updates"
                  value={thresholdForm.temperature.consecutive_updates}
                  onChange={handleThresholdChange}
                />
              </div>
            )}
          </div>
          <div>
            <button type="button" onClick={() => handleShowFields('humidity')}>{showFields.humidity ? "Cancel" : "Add Humidity"}</button>
            {showFields.humidity && (
              <div>
                <h3>Humidity (%)</h3>
                <label>Min Threshold:</label>
                <input
                  type="number"
                  name="humidity-min_threshold"
                  value={thresholdForm.humidity.min_threshold}
                  onChange={handleThresholdChange}
                />
                <label>Max Threshold:</label>
                <input
                  type="number"
                  name="humidity-max_threshold"
                  value={thresholdForm.humidity.max_threshold}
                  onChange={handleThresholdChange}
                />
                <label>Consecutive Updates:</label>
                <input
                  type="number"
                  name="humidity-consecutive_updates"
                  value={thresholdForm.humidity.consecutive_updates}
                  onChange={handleThresholdChange}
                />
              </div>
            )}
          </div>
          <div>
            <button type="button" onClick={() => handleShowFields('wind_speed')}>{showFields.wind_speed ? "Cancel" : "Add Wind Speed"}</button>
            {showFields.wind_speed && (
              <div>
                <h3>Wind Speed (m/s)</h3>
                <label>Min Threshold:</label>
                <input
                  type="number"
                  name="wind_speed-min_threshold"
                  value={thresholdForm.wind_speed.min_threshold}
                  onChange={handleThresholdChange}
                />
                <label>Max Threshold:</label>
                <input
                  type="number"
                  name="wind_speed-max_threshold"
                  value={thresholdForm.wind_speed.max_threshold}
                  onChange={handleThresholdChange}
                />
                <label>Consecutive Updates:</label>
                <input
                  type="number"
                  name="wind_speed-consecutive_updates"
                  value={thresholdForm.wind_speed.consecutive_updates}
                  onChange={handleThresholdChange}
                />
              </div>
            )}
          </div>
          <div>
            <button type="button" onClick={() => handleShowFields('condition')}>{showFields.condition ? "Cancel" : "Add Condition"}</button>
            {showFields.condition && (
              <div>
                <h3>Condition</h3>
                <label>Condition:</label>
                <input
                  type="text"
                  name="condition-condition"
                  value={thresholdForm.condition.condition}
                  onChange={handleThresholdChange}
                />
                <label>Consecutive Updates:</label>
                <input
                  type="number"
                  name="condition-consecutive_updates"
                  value={thresholdForm.condition.consecutive_updates}
                  onChange={handleThresholdChange}
                />
              </div>
            )}
          </div>
          <button type="submit">Submit</button>
        </form>
          
      </div>
      <ToastContainer />
      <Notifications handleAlert={handleAlertsNotification} handleWeatherUpdate={setCurrentWeather} handleRollups={handleRollupsNotification}/>
    </div>
  );
};

export default Weather;