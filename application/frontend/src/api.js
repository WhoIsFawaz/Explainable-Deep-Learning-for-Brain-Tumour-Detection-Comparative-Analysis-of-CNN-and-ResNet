/**
 * API Service for Brain MRI Classification Backend
 * Handles all HTTP requests to Flask API
 */

const API_BASE_URL = 'http://localhost:5000';

/**
 * Login user
 * @param {string} email 
 * @param {string} password 
 * @returns {Promise<Object>} User data
 */
export const login = async (email, password) => {
  const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({ email, password })
  });
  
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.message || 'Login failed');
  }
  return data;
};

/**
 * Logout user
 */
export const logout = async () => {
  const response = await fetch(`${API_BASE_URL}/api/auth/logout`, {
    method: 'POST',
    credentials: 'include'
  });
  
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.message || 'Logout failed');
  }
  return data;
};

/**
 * Get current user
 */
export const getCurrentUser = async () => {
  const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
    credentials: 'include'
  });
  
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.message || 'Failed to get user');
  }
  return data;
};

/**
 * Upload MRI image and get prediction
 * @param {File} imageFile 
 * @param {number} patientId (optional)
 * @returns {Promise<Object>} Prediction result with Grad-CAM
 */
export const predictImage = async (imageFile, patientId = null) => {
  const formData = new FormData();
  formData.append('image', imageFile);
  if (patientId) {
    formData.append('patient_id', patientId);
  }
  
  const response = await fetch(`${API_BASE_URL}/api/predict`, {
    method: 'POST',
    credentials: 'include',
    body: formData
  });
  
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.message || 'Prediction failed');
  }
  return data;
};

/**
 * Get prediction history
 */
export const getPredictionHistory = async () => {
  const response = await fetch(`${API_BASE_URL}/api/predictions/history`, {
    credentials: 'include'
  });
  
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.message || 'Failed to fetch history');
  }
  return data;
};

/**
 * Get single prediction by ID
 * @param {number} id 
 */
export const getPrediction = async (id) => {
  const response = await fetch(`${API_BASE_URL}/api/predictions/${id}`, {
    credentials: 'include'
  });
  
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.message || 'Failed to fetch prediction');
  }
  return data;
};

/**
 * Build full URL for image/gradcam paths
 * @param {string} path 
 * @returns {string}
 */
export const getImageUrl = (path) => {
  return `${API_BASE_URL}/${path}`;
};
