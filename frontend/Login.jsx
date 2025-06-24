import React, { useState } from 'react';
import api from './services/api.js';

const Login = ({ onLogin }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      const res = await api.post('/api/login', { username, password });
      const { token, username: name } = res.data;
      localStorage.setItem('authToken', token);
      onLogin(name);
    } catch (err) {
      setError('Credenciales incorrectas');
    }
  };

  return (
    <div className="flex items-center justify-center h-screen">
      <form onSubmit={handleSubmit} className="space-y-4 p-8 bg-white shadow rounded">
        <h1 className="text-xl font-bold text-center">Iniciar sesión</h1>
        <input
          type="text"
          placeholder="Usuario"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          className="w-64 border px-3 py-2 rounded"
        />
        <input
          type="password"
          placeholder="Clave"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-64 border px-3 py-2 rounded"
        />
        {error && <div className="text-red-600 text-sm">{error}</div>}
        <button type="submit" className="w-full bg-blue-600 text-white py-2 rounded">Entrar</button>
      </form>
    </div>
  );
};

export default Login;
