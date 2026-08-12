import { apiClient } from './client';

export const healthApi = {
  getHealth: () => apiClient('/health'),
  getReady: () => apiClient('/ready'),
};
