/**
 * API utility functions for making requests to the backend
 */

const getApiBaseUrl = (): string => {
  // In development, use local Flask server via Next.js proxy
  if (process.env.NODE_ENV === 'development') {
    return '';
  }
  
  // In production, use the backend App Runner URL
  return process.env.NEXT_PUBLIC_API_URL || '';
};

export const apiCall = async (endpoint: string, options: RequestInit = {}) => {
  const baseUrl = getApiBaseUrl();
  const url = `${baseUrl}${endpoint}`;
  
  return fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });
};

export default apiCall;