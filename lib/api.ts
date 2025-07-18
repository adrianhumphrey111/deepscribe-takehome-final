/**
 * API utility functions for making requests to the backend
 */

export const apiCall = async (endpoint: string, options: RequestInit = {}) => {
  const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'https://ue93wnfzm6.us-east-1.awsapprunner.com';
  const url = `${baseUrl}${endpoint}`;
  
  console.log(`API call: ${url}`); // Debug logging
  
  return fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });
};

export default apiCall;