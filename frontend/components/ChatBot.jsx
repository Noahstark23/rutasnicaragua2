import React, { useState } from 'react';
import axios from 'axios';

const knownCities = [
  'Managua',
  'Estelí',
  'León',
  'Matagalpa',
  'Chinandega',
  'Masaya',
  'Jinotega',
  'Rivas',
  'Granada'
];

const ChatBot = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');

  const addMessage = (text, sender) => {
    setMessages(prev => [...prev, { text, sender }]);
  };

  const sendMessage = async () => {
    const text = input.trim();
    if (!text) return;

    addMessage(text, 'user');
    setInput('');
    const reply = await interpretMessage(text);
    addMessage(reply, 'bot');
  };

  const interpretMessage = async (text) => {
    const words = text.toLowerCase().split(/\s+/);
    let origin = null;
    let destination = null;
    for (const city of knownCities) {
      const c = city.toLowerCase();
      if (words.includes(c)) {
        if (!origin) origin = city;
        else if (!destination && city !== origin) destination = city;
      }
    }

    let intent = null;
    if (words.some(w => ['ruta', 'ir'].includes(w))) intent = 'ruta';
    if (words.some(w => ['horario', 'salida'].includes(w))) intent = 'horario';
    if (words.includes('parada')) intent = 'parada';

    try {
      if (intent === 'ruta' || intent === 'horario') {
        const region = origin || destination;
        const routeRes = await axios.get('/api/rutas', { params: { region } });
        const rutas = routeRes.data || [];
        if (rutas.length) {
          const ruta = rutas[0];
          if (intent === 'horario') {
            const stopRes = await axios.get('/api/paradas', { params: { ruta: ruta.id } });
            const paradas = stopRes.data || [];
            if (paradas.length) {
              const horas = paradas.map(p => p.hora).filter(Boolean).join(' y ');
              return `Podés tomar la ruta ${ruta.long_name} desde ${paradas[0].name}. Sale a las ${horas}.`;
            }
          }
          return `Podés tomar la ruta ${ruta.long_name}.`;
        }
      } else if (intent === 'parada') {
        const region = origin;
        const routeRes = await axios.get('/api/rutas', { params: { region } });
        const rutas = routeRes.data || [];
        if (rutas.length) {
          const stopRes = await axios.get('/api/paradas', { params: { ruta: rutas[0].id } });
          const paradas = stopRes.data || [];
          if (paradas.length) {
            return `La parada más cercana es ${paradas[0].name}.`;
          }
        }
      }
    } catch (err) {
      console.error(err);
    }
    return 'Lo siento, no tengo datos suficientes para esa consulta.';
  };

  return (
    <div className="p-4 max-w-md mx-auto">
      <div className="h-80 overflow-y-auto space-y-2 mb-4 bg-gray-50 p-2 rounded">
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`px-3 py-2 rounded-lg max-w-xs ${msg.sender === 'user' ? 'bg-green-500 text-white' : 'bg-gray-200'}`}>{msg.text}</div>
          </div>
        ))}
      </div>
      <div className="flex">
        <input
          className="flex-grow border p-2 rounded-l"
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
        />
        <button className="bg-green-500 text-white px-4 rounded-r" onClick={sendMessage}>Enviar</button>
      </div>
    </div>
  );
};

export default ChatBot;
