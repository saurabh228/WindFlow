import React, { useEffect } from 'react';

const Notifications = ({ handleAlert, handleWeatherUpdate }) => {
  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/ws/notifications/');

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'alert') {
        handleAlert(data.message);
      } else if (data.type === 'weather') {
        handleWeatherUpdate(data.message);
      }
    };

    ws.onclose = () => {
      console.log('WebSocket closed');
    };

    return () => {
      ws.close();
    };
  }, [handleAlert, handleWeatherUpdate]);

  return null;
};

export default Notifications;