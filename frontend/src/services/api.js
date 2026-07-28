import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

// Create axios instance
const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Add token to requests
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// Handle token refresh on 401
api.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;
        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;
            try {
                const refreshToken = localStorage.getItem('refresh_token');
                const response = await axios.post(`${API_URL}/auth/refresh`, {}, {
                    headers: { Authorization: `Bearer ${refreshToken}` }
                });
                localStorage.setItem('access_token', response.data.access_token);
                originalRequest.headers.Authorization = `Bearer ${response.data.access_token}`;
                return api(originalRequest);
            } catch (refreshError) {
                localStorage.clear();
                window.location.href = '/login';
                return Promise.reject(refreshError);
            }
        }
        return Promise.reject(error);
    }
);

// Auth services
export const authService = {
    register: (userData) => api.post('/auth/register', userData),
    login: (credentials) => api.post('/auth/login', credentials),
    logout: () => {
        localStorage.clear();
        window.location.href = '/login';
    },
    getProfile: () => api.get('/auth/me'),
    updateProfile: (data) => api.put('/auth/me', data),
};

// Car services
export const carService = {
    getAll: (params) => api.get('/cars/', { params }),
    getById: (id) => api.get(`/cars/${id}`),
    getAvailable: () => api.get('/cars/available'),
    getTypes: () => api.get('/cars/types'),
    create: (data) => api.post('/cars/', data),
    update: (id, data) => api.put(`/cars/${id}`, data),
    delete: (id) => api.delete(`/cars/${id}`),
};

// Rental services
export const rentalService = {
    getAll: (params) => api.get('/rentals/', { params }),
    getById: (id) => api.get(`/rentals/${id}`),
    create: (data) => api.post('/rentals/', data),
    returnCar: (id) => api.put(`/rentals/${id}/return`),
    cancel: (id) => api.put(`/rentals/${id}/cancel`),
    adminGetAll: (params) => api.get('/rentals/admin/all', { params }),
    adminGetStats: () => api.get('/rentals/admin/stats'),
};

export default api;