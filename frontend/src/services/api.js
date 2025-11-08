import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

// Configure axios
const api = axios.create({
  baseURL: API_URL,
  withCredentials: true, // Important for session cookies
  headers: {
    'Content-Type': 'application/json',
  },
});

// Authentication API
export const authAPI = {
  login: async (username, password) => {
    const response = await api.post('/api/login', { username, password });
    return response.data;
  },

  logout: async () => {
    const response = await api.post('/api/logout');
    return response.data;
  },

  checkSession: async () => {
    try {
      const response = await api.get('/api/session');
      return response.data;
    } catch (error) {
      return { authenticated: false };
    }
  },
};

// Data API
export const dataAPI = {
  getColumns: async () => {
    const response = await api.get('/api/columns');
    return response.data.columns;
  },

  getData: async (columns) => {
    const response = await api.post('/api/data', { columns });
    return response.data;
  },

  getUniqueValues: async (column) => {
    const response = await api.post('/api/unique-values', { column });
    return response.data;
  },
};

// Error interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Redirect to login on 401
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
