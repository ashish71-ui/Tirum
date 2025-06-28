import type { LoginFormData, LoginResponse } from '../types/auth';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

class ApiService {
  private baseURL: string;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    
    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    // Add auth token if available
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers = {
        ...config.headers,
        Authorization: `Token ${token}`,
      };
    }

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.message || errorData.error || `HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Network error occurred');
    }
  }

  // Authentication endpoints - matching Django backend
  async login(credentials: LoginFormData): Promise<LoginResponse> {
    const response = await this.request<any>('/login/', {
      method: 'POST',
      body: JSON.stringify(credentials),
    });

    // Django now returns both token and user data
    return {
      user: {
        id: response.user.id,
        email: response.user.email,
        name: response.user.name,
        avatar: response.user.avatar || undefined,
      },
      token: response.token,
    };
  }

  async logout(): Promise<void> {
    return this.request<void>('/logout/', {
      method: 'POST',
    });
  }

  async getCurrentUser(): Promise<any> {
    return this.request<any>('/user/', {
      method: 'GET',
    });
  }

  // Additional endpoints for your Django backend
  async register(userData: any): Promise<any> {
    return this.request<any>('/register/', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  }
}

export const apiService = new ApiService(API_BASE_URL); 