import apiClient from './client';
import { User } from '../types';

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  full_name?: string;
  institution_name?: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  user: User;
}

export const authApi = {
  login: (credentials: LoginCredentials) => 
    apiClient.post<AuthResponse>('/api/auth/login', credentials),
  
  register: (data: RegisterData) => 
    apiClient.post<AuthResponse>('/api/auth/register', data),
  
  logout: () => 
    apiClient.post('/api/auth/logout'),
  
  getCurrentUser: () => 
    apiClient.get<User>('/api/auth/me'),
  
  refreshToken: (refreshToken: string) => 
    apiClient.post<AuthResponse>('/api/auth/refresh', { refresh_token: refreshToken }),
};
