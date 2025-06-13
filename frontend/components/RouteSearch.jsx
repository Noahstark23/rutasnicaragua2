import React, { useState } from 'react';
import { fetchRoutes } from '../services/api.js';

const cities = [
  'Managua',
  'Estelí',
  'León',
  'Matagalpa',
  'Chinandega',
  'Masaya',
  'Jinotega',
  'Rivas',
  'Granada',
];

const RouteSearch = ({ onSelectRoute }) => {
  const [origin, setOrigin] = useState('');
  const [destination, setDestination] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    const city = origin || destination;
    if (!city) return;
    try {
      const res = await fetchRoutes(city);
      if (res.data && res.data.length) {
        onSelectRoute(res.data[0]);
      }
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex gap-2 mb-4">
      <select value={origin} onChange={(e) => setOrigin(e.target.value)} className="border p-2 rounded">
        <option value="">Origen</option>
        {cities.map((city) => (
          <option key={city} value={city}>{city}</option>
        ))}
      </select>
      <select value={destination} onChange={(e) => setDestination(e.target.value)} className="border p-2 rounded">
        <option value="">Destino</option>
        {cities.map((city) => (
          <option key={city} value={city}>{city}</option>
        ))}
      </select>
      <button type="submit" className="bg-blue-600 text-white px-4 rounded">Buscar rutas</button>
    </form>
  );
};

export default RouteSearch;
