import { create } from 'zustand';
import type { AuthState, LoginFormData, User, LoginResponse } from '../types/auth';
import { apiService } from '../services/api';

interface AuthStore extends AuthState {
  login: (credentials: LoginFormData) => Promise<void>;
  logout: () => void;
  clearError: () => void;
  setLoading: (loading: boolean) => void;
  checkAuth: () => Promise<void>;
}

export const useAuthStore = create<AuthStore>((set, get) => ({
  user: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,

  login: async (credentials: LoginFormData) => {
    set({ isLoading: true, error: null });
    
    try {
      console.log('Attempting login with credentials:', credentials);
      // Call Django backend login endpoint
      const response = await apiService.login(credentials);
      console.log('Login response received:', response);
      
      // Store token in localStorage
      localStorage.setItem('authToken', response.token);
      
      set({
        user: response.user,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      });

      console.log('Auth state updated:', { user: response.user, isAuthenticated: true });

      // Note: Navigation will be handled by the LoginPage component
      // which watches the isAuthenticated state
    } catch (error) {
      console.error('Login error:', error);
      set({
        isLoading: false,
        error: error instanceof Error ? error.message : 'Login failed',
      });
    }
  },

  logout: async () => {
    try {
      // Call Django backend logout endpoint
      await apiService.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Clear local storage and state regardless of API call success
      localStorage.removeItem('authToken');
      set({
        user: null,
        isAuthenticated: false,
        isLoading: false,
        error: null,
      });
    }
  },

  clearError: () => {
    set({ error: null });
  },

  setLoading: (loading: boolean) => {
    set({ isLoading: loading });
  },

  checkAuth: async () => {
    const token = localStorage.getItem('authToken');
    if (!token) {
      set({ isAuthenticated: false, user: null });
      return;
    }

    try {
      set({ isLoading: true });
      const user = await apiService.getCurrentUser();
      set({
        user,
        isAuthenticated: true,
        isLoading: false,
      });
    } catch (error) {
      // Token is invalid, clear it
      localStorage.removeItem('authToken');
      set({
        user: null,
        isAuthenticated: false,
        isLoading: false,
      });
    }
  },
})); 