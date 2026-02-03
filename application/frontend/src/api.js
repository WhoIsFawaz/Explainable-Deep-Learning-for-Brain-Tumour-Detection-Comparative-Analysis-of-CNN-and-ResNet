/**
 * API Service for Brain MRI Classification Backend
 * Handles all HTTP requests to Flask API
 */

// Use environment variable for production, fallback to localhost for development
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5000';

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
 * @param {number} patient_id (for doctors)
 * @param {number} doctor_id (for patients)
 */
export const getPredictionHistory = async (filters = {}) => {
  const params = new URLSearchParams();
  if (filters.patient_id) params.append('patient_id', filters.patient_id);
  if (filters.doctor_id) params.append('doctor_id', filters.doctor_id);
  
  const response = await fetch(`${API_BASE_URL}/api/predictions/history?${params}`, {
    credentials: 'include'
  });
  
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.message || 'Failed to fetch history');
  }
  return data;
};

/**
 * Get list of patients (for doctors)
 */
export const getPatients = async () => {
  const response = await fetch(`${API_BASE_URL}/api/patients`, {
    credentials: 'include'
  });
  
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.message || 'Failed to fetch patients');
  }
  return data;
};

/**
 * Get list of doctors (for patients)
 */
export const getDoctors = async () => {
  const response = await fetch(`${API_BASE_URL}/api/doctors`, {
    credentials: 'include'
  });
  
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.message || 'Failed to fetch doctors');
  }
  return data;
};

/**
 * Admin: Get all users
 */
export const getAllUsers = async () => {
  const response = await fetch(`${API_BASE_URL}/api/admin/users`, {
    credentials: 'include'
  });
  
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.message || 'Failed to fetch users');
  }
  return data;
};

/**
 * Admin: Create doctor
 */
export const createDoctor = async (name, email, password) => {
  const response = await fetch(`${API_BASE_URL}/api/admin/create-doctor`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({ name, email, password })
  });
  
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.message || 'Failed to create doctor');
  }
  return data;
};

/**
 * Admin: Create patient
 */
export const createPatient = async (name, email, password) => {
  const response = await fetch(`${API_BASE_URL}/api/admin/create-patient`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({ name, email, password })
  });
  
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.message || 'Failed to create patient');
  }
  return data;
};

/**
 * Admin: Delete user
 */
export const deleteUser = async (userId) => {
  const response = await fetch(`${API_BASE_URL}/api/admin/delete-user/${userId}`, {
    method: 'DELETE',
    credentials: 'include'
  });
  
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.message || 'Failed to delete user');
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
 * Handles both Azure Blob URLs (already full URLs) and local paths
 * @param {string} path 
 * @returns {string}
 */
export const getImageUrl = (path) => {
  // If it's already a full URL (Azure Blob Storage), return as-is
  if (path && path.startsWith('http')) {
    return path;
  }
  // Otherwise, prepend API base URL for local storage
  return `${API_BASE_URL}/${path}`;
};
