// src/services/apiClient.js

import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'http://localhost:8000/api',
});

// Get daily rollups/aggregated data
export const getRollUps = async () => {
  try {
    const response = await apiClient.get('/get-rollups/');
    return response.data;
  } catch (error) {
    console.error('Error fetching rollups:', error);
    throw error;
  }
};

// Get current weather details
export const getCurrentWeather = async () => {
  try {
    const response = await apiClient.get('/current-weather/');
    return response.data;
  } catch (error) {
    console.error('Error fetching current weather details:', error);
    throw error;
  }
};

// Get all cities
export const getCities = async () => {
  try {
    const response = await apiClient.get('/get-cities/');
    return response.data;
  } catch (error) {
    console.error('Error fetching cities:', error);
    throw error;
  }
};

// Check connection to weather API
export const checkWeatherAPIConnection = async () => {
  try {
    const response = await apiClient.get('/check-connection-status/');
    return response.data;
  } catch (error) {
    console.error('Error checking connection to weather API:', error);
    throw error;
  }
};

// get weather fetch interval
export const getWeatherFetchInterval = async () => {
  try {
    const response = await apiClient.get('/get-interval/');
    return response.data;
  } catch (error) {
    console.error('Error fetching weather fetch interval:', error);
    throw error;
  }
};

// Set weather fetch interval
export const setWeatherFetchInterval = async (interval) => {
  try {
    const response = await apiClient.post('/set-interval/', { interval });
    return response.data;
  } catch (error) {
    console.error('Error setting weather fetch interval:', error);
    throw error;
  }
};

// Get thresholds
export const getThresholds = async () => {
  try {
    const response = await apiClient.get('/get-thresholds/');
    return response.data;
  } catch (error) {
    console.error('Error fetching thresholds:', error);
    throw error;
  }
};

// Set thresholds
export const setThresholds = async (thresholds) => {
  try {
    const response = await apiClient.post('/set-thresholds/', thresholds);
    return response.data;
  } catch (error) {
    console.error('Error setting thresholds:', error);
    throw error;
  }
};

export default apiClient;