import { apiClient } from './client';

export const policiesApi = {
  getAll: () => apiClient('/api/v1/policies/'),
  
  getOne: (agentId) => apiClient(`/api/v1/policies/${agentId}`),
  
  create: (policyData) => apiClient('/api/v1/policies/', {
    method: 'POST',
    body: policyData
  }),
  
  update: (agentId, policyData) => apiClient(`/api/v1/policies/${agentId}`, {
    method: 'PUT',
    body: policyData
  }),
  
  delete: (agentId) => apiClient(`/api/v1/policies/${agentId}`, {
    method: 'DELETE'
  }),
};
