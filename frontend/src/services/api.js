import axios from 'axios'
import { useAuthStore } from '@/stores/auth'
import { useNotificationStore } from '@/stores/notifications'

// Create axios instance
const api = axios.create({
  baseURL: '/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  }
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor to handle errors and token refresh
api.interceptors.response.use(
  (response) => {
    return response
  },
  async (error) => {
    const originalRequest = error.config
    
    // If error is 401 and we haven't already tried to refresh
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      
      const authStore = useAuthStore()
      const refreshToken = localStorage.getItem('refresh_token')
      
      if (refreshToken) {
        try {
          // Try to refresh the token
          const response = await axios.post('/api/v1/auth/token/refresh/', {
            refresh: refreshToken
          })
          
          const newAccessToken = response.data.access
          localStorage.setItem('access_token', newAccessToken)
          
          // Retry the original request with new token
          originalRequest.headers.Authorization = `Bearer ${newAccessToken}`
          return api(originalRequest)
        } catch (refreshError) {
          // Refresh failed, logout user
          authStore.logout()
          window.location.href = '/login'
          return Promise.reject(refreshError)
        }
      } else {
        // No refresh token, logout user
        authStore.logout()
        window.location.href = '/login'
      }
    }
    
    // Handle other errors
    if (error.response?.status >= 500) {
      const notificationStore = useNotificationStore()
      notificationStore.error('Server error occurred. Please try again later.')
    }
    
    return Promise.reject(error)
  }
)

export default api