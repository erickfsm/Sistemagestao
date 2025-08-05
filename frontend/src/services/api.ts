const API_BASE_URL = 'http://127.0.0.1:5000/api';

const fetchApi = async (endpoint: string, options: RequestInit = {}) => {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const headers = new Headers(options.headers);
  
  if (!headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }

  const token = localStorage.getItem('accessToken');
  
  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  const finalOptions: RequestInit = {
    ...options,
    headers,
  };

  const response = await fetch(url, finalOptions);
  
  if (response.status === 401 || response.status === 403) {
    localStorage.removeItem('accessToken');
     window.location.href = '/login'; 
    throw new Error('Sessão expirada. Redirecionando para o login.');
  }

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Erro ${response.status}: ${response.statusText} - ${errorText}`);
  }
  
  return response.json();
};

export const patchApi = async (endpoint: string, data: any) => {
  const options = {
    method: 'PATCH',
    body: JSON.stringify(data),
    headers: { 'Content-Type': 'application/json' },
  };
  return fetchApi(endpoint, options);
};

export const fetchDeliveries = async (filters: Record<string, any> = {}) => {
  const params = new URLSearchParams(filters).toString();
  const endpoint = `/entregas/?${params}`;
  return fetchApi(endpoint);
};

export const fetchLogin = async (credentials: any) => {
   const data = await fetchApi('/login', { 
    method: 'POST',
    body: JSON.stringify(credentials),
  });

  if (data && data.access_token) {
    localStorage.setItem('accessToken', data.access_token);

    if (data.refresh_token) {
      localStorage.setItem('refreshToken', data.refresh_token);
    }
  }

  return data;
};

export const finalizeDelivery = async (deliveryId: string) => {
  const today = new Date().toISOString().slice(0, 19).replace('T', ' ');
  const endpoint = `/entregas/finalizar/${deliveryId}`;
  return patchApi(endpoint, { data_finalizacao: today });
};

export const fetchComprovantesPorEntrega = async (entregaId: string) => {
  const endpoint = `/entregas/${entregaId}/comprovantes`;
  return fetchApi(endpoint);
};

export const fetchDevolucoesPorEntrega = async (entregaId: string) => {
  const endpoint = `/entregas/${entregaId}/devolucoes`;
  return fetchApi(endpoint);
};

export const fetchRastreamentoPorEntrega = async (entregaId: string) => {
  const endpoint = `/entregas/${entregaId}/rastreamento`;
  return fetchApi(endpoint);
};

export const atualizarRastreamentoEntrega = async (entregaId: string) => {
  const endpoint = `/entregas/${entregaId}/atualizar-rastreamento`;
  return fetchApi(endpoint, { method: 'POST' });
};

export const uploadComprovante = async (entregaId: string, file: File) => {
  const formData = new FormData();
  formData.append('entrega_id', entregaId);
  formData.append('file', file);

  const token = localStorage.getItem('accessToken');
  if (!token) {
    throw new Error('Não autorizado. Por favor, faça login novamente.');
  }

  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

  const response = await fetch(`${API_BASE_URL}/comprovantes/upload`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
    body: formData,
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.erro || 'Falha no upload do comprovante.');
  }

  return response.json();
};