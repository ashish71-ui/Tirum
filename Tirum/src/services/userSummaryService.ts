import type { UserSummary } from '../types/userSummary';
import { API_CONFIG } from '../config/api';

class UserSummaryService {
  private getAuthHeaders() {
    const token = localStorage.getItem('authToken');
    console.log('Token from localStorage:', token);
    
    if (!token) {
      throw new Error('No authentication token found');
    }
    
    return {
      'Content-Type': 'application/json',
      'Authorization': `Token ${token}`, // Django uses 'Token' not 'Bearer'
    };
  }

  async getUserSummary(): Promise<UserSummary> {
    try {
      const headers = this.getAuthHeaders();
      console.log('Making request to:', `${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.USER_SUMMARY}`);
      console.log('Headers:', headers);
      
      const response = await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.USER_SUMMARY}`, {
        headers,
      });
      
      console.log('Response status:', response.status);
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('Error response:', errorText);
        throw new Error(`Failed to fetch user summary: ${response.status} ${errorText}`);
      }
      
      const data = await response.json();
      console.log('User summary data:', data);
      return data;
    } catch (error) {
      console.error('Error in getUserSummary:', error);
      throw error;
    }
  }

  async refreshUserSummary(): Promise<UserSummary> {
    try {
      const headers = this.getAuthHeaders();
      // Force refresh by adding timestamp
      const response = await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.USER_SUMMARY}?t=${Date.now()}`, {
        headers,
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Failed to refresh user summary: ${response.status} ${errorText}`);
      }
      
      return response.json();
    } catch (error) {
      console.error('Error in refreshUserSummary:', error);
      throw error;
    }
  }
}

export const userSummaryService = new UserSummaryService(); 