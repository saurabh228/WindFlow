import { useEffect } from 'react';

const Notifications = ({ handleAlert, handleWeatherUpdate, handleRollups }) => {
  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/ws/notifications/');
    ws.onopen = () => {
      console.log('WebSocket connected');
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
    
        if (data.type === 'weather') {
          const message = JSON.parse(data.message);
          const new_weather = (message.weather);
          const alerts = (message.alerts);
          const roll_ups = (message.roll_ups);

          const updated_weather = {};

          for(const dataa of new_weather){
            updated_weather[dataa.city]={
              date:dataa.dt,
              temp:dataa.temp,
              feels_like:dataa.feels_like,
              humidity:dataa.humidity,
              wind_speed:dataa.wind_speed,
              wind_deg:dataa.wind_deg,
              condition:dataa.dominant_condition
            }
          }
          handleWeatherUpdate(updated_weather);
          handleAlert(alerts);
          console.log('rollups1: ', roll_ups);
          handleRollups(roll_ups);
        }else{  
          console.log('Unknown message type:', data.type);
        }
      } catch (error) {
        console.error('Error fetching current weather:', error);
      }
    };

    ws.onclose = () => {
      console.log('WebSocket closed');
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    return () => {
      ws.close();
    };
  }, []);

  return null;
};

export default Notifications;