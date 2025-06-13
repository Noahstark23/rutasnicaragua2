import React, { useState } from 'react';
import RouteSearch from './components/RouteSearch.jsx';
import MapView from './components/MapView.jsx';
import ChatBot from './components/ChatBot.jsx';

const App = () => {
  const [route, setRoute] = useState(null);

  return (
    <div className="p-4 space-y-4">
      <RouteSearch onSelectRoute={setRoute} />
      <MapView route={route} />
      <ChatBot />
    </div>
  );
};

export default App;
