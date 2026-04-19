import apiClient from './client';
import { Vehicle, FuelRecord, TravelReceipt, EmissionReport, DashboardStats } from '../types';

export const emissionsApi = {
  // Vehicles - mapped to backend
  getVehicles: () => apiClient.get<Vehicle[]>('/api/vehicles'),
  createVehicle: (data: Omit<Vehicle, 'id'>) => apiClient.post<Vehicle>('/api/vehicles', data),
  updateVehicle: (id: string, data: Partial<Vehicle>) => apiClient.put<Vehicle>(`/api/vehicles/${id}`, data),
  deleteVehicle: (id: string) => apiClient.delete(`/api/vehicles/${id}`),

  // Fuel Records - mapped to backend /api/emissions/fuel
  getFuelRecords: () => apiClient.get<FuelRecord[]>('/api/emissions/fuel'),
  createFuelRecord: (data: Omit<FuelRecord, 'id'>) => apiClient.post<FuelRecord>('/api/emissions/fuel', data),
  
  // Travel Receipts - mapped to backend /api/emissions/travel
  getTravelReceipts: () => apiClient.get<TravelReceipt[]>('/api/emissions/travel'),
  createTravelReceipt: (data: Omit<TravelReceipt, 'id'>) => apiClient.post<TravelReceipt>('/api/emissions/travel', data),

  // Reports - mapped to backend /api/reports
  getReports: () => apiClient.get<EmissionReport[]>('/api/reports'),
  generateReport: (data: any) => apiClient.post<EmissionReport>('/api/reports', data),
  downloadReport: (id: string) => apiClient.get(`/api/reports/${id}/download`, { responseType: 'blob' }),

  // Dashboard - mapped to backend /api/emissions/dashboard
  getDashboardStats: () => apiClient.get<DashboardStats>('/api/emissions/dashboard'),

  // Calculate - backend endpoint for emissions calculation
  calculateEmissions: (data: any) => apiClient.post('/api/calculate', data),

  // Upload - backend endpoint for file uploads
  uploadFile: (file: File, type: string) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('type', type);
    return apiClient.post('/api/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },

  // Anomalies - backend endpoint for anomaly detection
  getAnomalies: () => apiClient.get('/api/anomalies'),

  // Jobs - backend endpoint for job management
  getJobs: () => apiClient.get('/api/jobs'),
  getJobStatus: (jobId: string) => apiClient.get(`/api/jobs/${jobId}`),
};
