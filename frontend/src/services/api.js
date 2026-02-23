import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const api = axios.create({
    baseURL: `${BACKEND_URL}/api`,
    headers: {
        'Content-Type': 'application/json'
    }
});

// Request interceptor to add auth token
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Response interceptor for error handling
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response) {
            // Handle 401 Unauthorized - token expired or invalid
            if (error.response.status === 401) {
                localStorage.removeItem('token');
                // Redirect to login if not already there
                if (window.location.pathname !== '/login') {
                    window.location.href = '/login';
                }
            }
            
            // Extract error message
            const message = error.response.data?.detail || error.response.data?.message || 'An error occurred';
            error.message = message;
        } else if (error.request) {
            error.message = 'Network error. Please check your connection.';
        }
        
        return Promise.reject(error);
    }
);

export default api;

// Course API
export const courseApi = {
    getAll: (params) => api.get('/courses/', { params }),
    getById: (id) => api.get(`/courses/${id}`),
    create: (data) => api.post('/courses/', data),
    update: (id, data) => api.put(`/courses/${id}`, data),
    delete: (id) => api.delete(`/courses/${id}`),
    addLesson: (courseId, data) => api.post(`/courses/${courseId}/lessons`, data, {
        headers: { 'Content-Type': 'multipart/form-data' }
    }),
    uploadPdf: (courseId, file) => {
        const formData = new FormData();
        formData.append('file', file);
        return api.post(`/courses/${courseId}/pdf`, formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        });
    },
    getAllAdmin: () => api.get('/courses/admin/all')
};

// Payment API
export const paymentApi = {
    createCheckout: (courseId) => api.post(`/payments/checkout/${courseId}`),
    getStatus: (sessionId) => api.get(`/payments/status/${sessionId}`),
    getHistory: () => api.get('/payments/history')
};

// Dashboard API
export const dashboardApi = {
    getMyCourses: () => api.get('/dashboard/my-courses'),
    getCourseContent: (courseId) => api.get(`/dashboard/course/${courseId}`),
    updateProgress: (courseId, data) => api.post(`/dashboard/course/${courseId}/progress`, data),
    downloadPdf: (courseId, pdfIndex) => api.get(`/dashboard/course/${courseId}/pdf/${pdfIndex}`, {
        responseType: 'blob'
    })
};

// Admin API
export const adminApi = {
    getUsers: () => api.get('/admin/users'),
    getStats: () => api.get('/admin/stats'),
    updateUserRole: (userId, role) => api.put(`/admin/users/${userId}/role?role=${role}`),
    deleteUser: (userId) => api.delete(`/admin/users/${userId}`)
};
