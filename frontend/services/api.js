import axios from 'axios';

const apiClient = axios.create();

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('authToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const fetchRoutes = (region) =>
  apiClient.get('/api/rutas', { params: { region } });

export const fetchStops = (routeId) =>
  apiClient.get('/api/paradas', { params: { ruta: routeId } });

export default apiClient;
