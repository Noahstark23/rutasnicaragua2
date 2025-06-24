import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import RouteSearch from './components/RouteSearch.jsx';
import MapView from './components/MapView.jsx';
import ChatBot from './components/ChatBot.jsx';
import Login from './Login.jsx';

const App = () => {
  const [route, setRoute] = useState(null);
  const [user, setUser] = useState(localStorage.getItem('username'));

  const handleLogin = (name) => {
    setUser(name);
    localStorage.setItem('username', name);
  };

  const Home = () => (
    <div className="p-4 space-y-4">
      <RouteSearch onSelectRoute={setRoute} />
      <MapView route={route} />
      <ChatBot />
    </div>
  );

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login onLogin={handleLogin} />} />
        <Route
          path="/*"
          element={user ? <Home /> : <Navigate to="/login" replace />}
        />
      </Routes>
    </BrowserRouter>
  );
};

export default App;
