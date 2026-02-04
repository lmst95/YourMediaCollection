import apiClient from './client';
import type { User, AuthTokens } from '../types';

interface LoginCredentials {
  username: string;
  password: string;
}

interface RegisterData {
  username: string;
  email: string;
  password: string;
  password_confirm: string;
}

export const authApi = {
  // Login
  login: async (credentials: LoginCredentials) => {
    const response = await apiClient.post<AuthTokens>('/api/auth/login/', credentials);
    const { access, refresh } = response.data;
    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);
    return response.data;
  },

  // Register
  register: async (data: RegisterData) => {
    const response = await apiClient.post('/api/auth/register/', data);
    return response.data;
  },

  // Logout
  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  },

  // Get current user
  getCurrentUser: async () => {
    const response = await apiClient.get<User>('/api/users/me/');
    return response.data;
  },

  // Check if user is authenticated
  isAuthenticated: () => {
    return !!localStorage.getItem('access_token');
  },
};
