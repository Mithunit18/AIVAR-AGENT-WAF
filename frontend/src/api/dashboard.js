import { apiClient } from './client';

export const dashboardApi = {
  getSummary: () => apiClient('/api/v1/dashboard/summary'),
  
  getEvents: (params = {}) => {
    const query = new URLSearchParams();
    if (params.skip !== undefined) query.append('skip', params.skip);
    if (params.limit !== undefined) query.append('limit', params.limit);
    if (params.decision) query.append('decision', params.decision);
    if (params.agent_id) query.append('agent_id', params.agent_id);
    if (params.tool_name) query.append('tool_name', params.tool_name);
    
    const queryString = query.toString();
    return apiClient(`/api/v1/dashboard/events${queryString ? '?' + queryString : ''}`);
  },

  getEvent: (eventId) => apiClient(`/api/v1/dashboard/events/${eventId}`),
};
