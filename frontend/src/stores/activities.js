import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'

export const useActivitiesStore = defineStore('activities', () => {
  // State
  const activities = ref([])
  const categories = ref([])
  const templates = ref([])
  const dashboardData = ref(null)
  const isLoading = ref(false)

  // Getters
  const totalCO2Today = computed(() => {
    const today = new Date().toISOString().split('T')[0]
    return activities.value
      .filter(activity => activity.start_timestamp?.startsWith(today))
      .reduce((sum, activity) => sum + (parseFloat(activity.co2_kg) || 0), 0)
  })

  const activitiesByCategory = computed(() => {
    const grouped = {}
    activities.value.forEach(activity => {
      const category = activity.category_name || 'Other'
      if (!grouped[category]) {
        grouped[category] = []
      }
      grouped[category].push(activity)
    })
    return grouped
  })

  // Actions
  const fetchActivities = async (filters = {}) => {
    isLoading.value = true
    try {
      const params = new URLSearchParams(filters).toString()
      const response = await api.get(`/activities/?${params}`)
      activities.value = response.data.results || response.data
      return activities.value
    } catch (error) {
      throw error
    } finally {
      isLoading.value = false
    }
  }

  const fetchCategories = async () => {
    try {
      const response = await api.get('/activities/categories/')
      categories.value = response.data.results || response.data
      return categories.value
    } catch (error) {
      throw error
    }
  }

  const fetchTemplates = async (categoryId = null) => {
    try {
      const params = categoryId ? `?category=${categoryId}` : ''
      const response = await api.get(`/activities/templates/${params}`)
      templates.value = response.data.results || response.data
      return templates.value
    } catch (error) {
      throw error
    }
  }

  const createActivity = async (activityData) => {
    isLoading.value = true
    try {
      const response = await api.post('/activities/', activityData)
      const newActivity = response.data
      
      // Add to the beginning of activities array
      activities.value.unshift(newActivity)
      
      return newActivity
    } catch (error) {
      throw error
    } finally {
      isLoading.value = false
    }
  }

  const updateActivity = async (id, activityData) => {
    try {
      const response = await api.put(`/activities/${id}/`, activityData)
      const updatedActivity = response.data
      
      // Update in activities array
      const index = activities.value.findIndex(a => a.id === id)
      if (index !== -1) {
        activities.value[index] = updatedActivity
      }
      
      return updatedActivity
    } catch (error) {
      throw error
    }
  }

  const deleteActivity = async (id) => {
    try {
      await api.delete(`/activities/${id}/`)
      
      // Remove from activities array
      const index = activities.value.findIndex(a => a.id === id)
      if (index !== -1) {
        activities.value.splice(index, 1)
      }
      
      return true
    } catch (error) {
      throw error
    }
  }

  const recalculateActivity = async (id) => {
    try {
      const response = await api.post(`/activities/${id}/recalculate/`)
      const updatedActivity = response.data.activity
      
      // Update in activities array
      const index = activities.value.findIndex(a => a.id === id)
      if (index !== -1) {
        activities.value[index] = updatedActivity
      }
      
      return response.data
    } catch (error) {
      throw error
    }
  }

  const fetchDashboard = async () => {
    try {
      const response = await api.get('/activities/dashboard/')
      dashboardData.value = response.data
      return dashboardData.value
    } catch (error) {
      throw error
    }
  }

  // Initialize data
  const initialize = async () => {
    await Promise.all([
      fetchCategories(),
      fetchTemplates(),
      fetchDashboard()
    ])
  }

  return {
    // State
    activities,
    categories,
    templates,
    dashboardData,
    isLoading,

    // Getters
    totalCO2Today,
    activitiesByCategory,

    // Actions
    fetchActivities,
    fetchCategories,
    fetchTemplates,
    createActivity,
    updateActivity,
    deleteActivity,
    recalculateActivity,
    fetchDashboard,
    initialize
  }
})