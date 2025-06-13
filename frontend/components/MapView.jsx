import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Polyline, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import { fetchStops } from '../services/api.js';

const center = [12.8654, -85.2072];

const icon = new L.Icon({
  iconUrl: 'https://unpkg.com/leaflet@1.9.3/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.3/dist/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});

const MapView = ({ route }) => {
  const [stops, setStops] = useState([]);

  useEffect(() => {
    if (!route) {
      setStops([]);
      return;
    }
    fetchStops(route.id)
      .then(res => setStops(res.data || []))
      .catch(err => console.error(err));
  }, [route]);

  const positions = stops.map(s => [s.lat, s.lon]);

  return (
    <MapContainer center={center} zoom={7} className="h-96 w-full">
      <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
      {positions.length > 1 && <Polyline positions={positions} color="blue" />}
      {stops.map(stop => (
        <Marker key={stop.id} position={[stop.lat, stop.lon]} icon={icon}>
          <Popup>{stop.name}</Popup>
        </Marker>
      ))}
    </MapContainer>
  );
};

export default MapView;
