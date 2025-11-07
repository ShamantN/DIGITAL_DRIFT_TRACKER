// dashboard/src/services/api.js
import axios from 'axios';

const API_URL = 'http://127.0.0.1:8000'; // Your FastAPI backend

// Create axios instance with auth interceptor
const apiClient = axios.create({
  baseURL: API_URL,
});

// Add request interceptor to include auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor to handle auth errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear auth data and redirect to login
      localStorage.removeItem('auth_token');
      window.location.reload();
    }
    return Promise.reject(error);
  }
);

export const getAnalytics = (days = 7) => {
  return apiClient.get('/api/dashboard/analytics', {
    params: {
      period_days: days
    }
  });
};

// Whitelist management functions
export const getWhitelist = () => {
  return apiClient.get('/api/whitelist');
};

export const addToWhitelist = (domainName, userReason = '') => {
  return apiClient.post('/api/whitelist', {
    domain_name: domainName,
    user_reason: userReason
  });
};

export const removeFromWhitelist = (domainId) => {
  return apiClient.delete(`/api/whitelist/${domainId}`);
};

// Insights
export const getInsights = () => {
  return apiClient.get('/api/dashboard/insights');
};

// Admin functions
export const getAdminStats = () => {
  return apiClient.get('/api/admin/stats');
};

export const getAdminUsers = () => {
  return apiClient.get('/api/admin/users');
};

export const deleteUser = (userId) => {
  return apiClient.delete(`/api/admin/users/${userId}`);
};

// Authentication functions
export const login = (email, password) => {
  return axios.post(`${API_URL}/api/auth/login`, {
    email: email,
    password: password
  });
};