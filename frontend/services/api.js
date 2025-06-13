import axios from 'axios';

const apiClient = axios.create();

export const fetchRoutes = (region) =>
  apiClient.get('/api/rutas', { params: { region } });

export const fetchStops = (routeId) =>
  apiClient.get('/api/paradas', { params: { ruta: routeId } });

export default apiClient;
