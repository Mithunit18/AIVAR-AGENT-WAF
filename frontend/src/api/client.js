// Use relative path in production (Nginx proxy) to avoid CORS issues.
// Use localhost:8000 in local dev unless explicitly overridden.
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? (import.meta.env.DEV ? 'http://localhost:8000' : '');

export async function apiClient(endpoint, { method = 'GET', body, ...customConfig } = {}) {
  const headers = { 'Content-Type': 'application/json' };
  const config = {
    method,
    headers,
    ...customConfig,
  };

  if (body) {
    config.body = JSON.stringify(body);
  }

  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
    if (!response.ok) {
      let errorMessage = `HTTP Error: ${response.status}`;
      try {
        const errorData = await response.json();
        errorMessage = errorData.detail?.message || errorData.detail || errorMessage;
      } catch (e) {
        // Fallback if not JSON
      }
      throw new Error(errorMessage);
    }
    
    // For 204 No Content
    if (response.status === 204) return null;
    return await response.json();
  } catch (error) {
    console.error(`API Client Error (${method} ${endpoint}):`, error);
    throw error;
  }
}
