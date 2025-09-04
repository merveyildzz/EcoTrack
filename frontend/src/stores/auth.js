import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref(null)
  const tokens = ref({
    access: localStorage.getItem('access_token'),
    refresh: localStorage.getItem('refresh_token')
  })
  const isLoading = ref(false)

  // Getters
  const isAuthenticated = computed(() => {
    return !!(tokens.value.access && user.value)
  })

  // Actions
  const login = async (credentials) => {
    isLoading.value = true
    try {
      const response = await api.post('/auth/login/', credentials)
      const { user: userData, tokens: tokenData } = response.data
      
      user.value = userData
      tokens.value = tokenData
      
      // Store tokens in localStorage
      localStorage.setItem('access_token', tokenData.access)
      localStorage.setItem('refresh_token', tokenData.refresh)
      
      // Set default authorization header
      api.defaults.headers.common['Authorization'] = `Bearer ${tokenData.access}`
      
      return userData
    } catch (error) {
      throw error
    } finally {
      isLoading.value = false
    }
  }

  const register = async (userData) => {
    isLoading.value = true
    try {
      const response = await api.post('/auth/register/', userData)
      const { user: newUser, tokens: tokenData } = response.data
      
      user.value = newUser
      tokens.value = tokenData
      
      // Store tokens in localStorage
      localStorage.setItem('access_token', tokenData.access)
      localStorage.setItem('refresh_token', tokenData.refresh)
      
      // Set default authorization header
      api.defaults.headers.common['Authorization'] = `Bearer ${tokenData.access}`
      
      return newUser
    } catch (error) {
      throw error
    } finally {
      isLoading.value = false
    }
  }

  const logout = async () => {
    user.value = null
    tokens.value = { access: null, refresh: null }
    
    // Remove tokens from localStorage
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    
    // Remove authorization header
    delete api.defaults.headers.common['Authorization']
  }

  const refreshToken = async () => {
    try {
      const response = await api.post('/auth/token/refresh/', {
        refresh: tokens.value.refresh
      })
      
      tokens.value.access = response.data.access
      localStorage.setItem('access_token', response.data.access)
      api.defaults.headers.common['Authorization'] = `Bearer ${response.data.access}`
      
      return response.data.access
    } catch (error) {
      // Refresh failed, logout user
      logout()
      throw error
    }
  }

  const fetchCurrentUser = async () => {
    try {
      const response = await api.get('/auth/me/')
      user.value = response.data
      return response.data
    } catch (error) {
      logout()
      throw error
    }
  }

  const updateProfile = async (profileData) => {
    try {
      const response = await api.put('/auth/profile/', profileData)
      // Update user data with profile info
      if (user.value) {
        user.value.profile = response.data
      }
      return response.data
    } catch (error) {
      throw error
    }
  }

  const updateSettings = async (settingsData) => {
    try {
      const response = await api.put('/auth/settings/', settingsData)
      // Update user data with settings info
      if (user.value) {
        user.value.settings = response.data
      }
      return response.data
    } catch (error) {
      throw error
    }
  }

  // Initialize auth state
  const initialize = async () => {
    if (tokens.value.access) {
      try {
        api.defaults.headers.common['Authorization'] = `Bearer ${tokens.value.access}`
        await fetchCurrentUser()
      } catch (error) {
        // Token might be expired, try to refresh
        if (tokens.value.refresh) {
          try {
            await refreshToken()
            await fetchCurrentUser()
          } catch (refreshError) {
            logout()
          }
        } else {
          logout()
        }
      }
    }
  }

  return {
    // State
    user,
    tokens,
    isLoading,
    
    // Getters
    isAuthenticated,
    
    // Actions
    login,
    register,
    logout,
    refreshToken,
    fetchCurrentUser,
    updateProfile,
    updateSettings,
    initialize
  }
})