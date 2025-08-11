import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { fetchLogin } from '../services/api';

const LoginPage = () => {
  const navigate = useNavigate();
  const [login, setLogin] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleLoginSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    try {
      await fetchLogin({ login, senha: password });
      navigate('/'); 
    } catch (err) {
      setError('Falha no login. Verifique suas credenciais.');
      console.error(err);
    }
  };

  return (
    <div className="flex items-center justify-center h-screen bg-gray-200">
      <div className="p-8 bg-white rounded shadow-md w-full max-w-sm">
        <h2 className="text-2xl font-bold mb-6 text-center">Login - TMS Global</h2>
        <form onSubmit={handleLoginSubmit}>
          <div className="mb-4">
            <label className="block text-gray-700">Usuário</label>
            <input
              type="text"
              value={login}
              onChange={(e) => setLogin(e.target.value)}
              className="w-full px-3 py-2 border rounded"
              required
            />
          </div>
          <div className="mb-6">
            <label className="block text-gray-700">Senha</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-3 py-2 border rounded"
              required
            />
          </div>
          {error && <p className="text-red-500 text-sm mb-4">{error}</p>}
          <button type="submit" className="w-full bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded">
            Entrar
          </button>
        </form>
      </div>
    </div>
  );
};

export default LoginPage;