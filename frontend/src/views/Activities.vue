<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <div class="mb-8 flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Activities</h1>
        <p class="mt-2 text-gray-600">View and manage your carbon footprint activities</p>
      </div>
      <router-link 
        to="/log-activity" 
        class="btn-primary flex items-center space-x-2"
      >
        <span>➕</span>
        <span>Log Activity</span>
      </router-link>
    </div>

    <!-- Filters -->
    <div class="card mb-6">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Category</label>
          <select v-model="filters.category" class="input-field">
            <option value="">All Categories</option>
            <option v-for="category in categories" :key="category.id" :value="category.id">
              {{ category.name }}
            </option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Date Range</label>
          <select v-model="filters.dateRange" class="input-field">
            <option value="">All Time</option>
            <option value="today">Today</option>
            <option value="week">This Week</option>
            <option value="month">This Month</option>
          </select>
        </div>
        <div class="flex items-end">
          <button @click="applyFilters" class="btn-primary w-full">
            Apply Filters
          </button>
        </div>
      </div>
    </div>

    <!-- Activities List -->
    <div class="card">
      <div v-if="isLoading" class="text-center py-8">
        <div class="w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full animate-spin mx-auto"></div>
        <p class="mt-2 text-gray-600">Loading activities...</p>
      </div>

      <div v-else-if="activities.length === 0" class="text-center py-12">
        <span class="text-6xl mb-4 block">📝</span>
        <h3 class="text-lg font-medium text-gray-900 mb-2">No activities found</h3>
        <p class="text-gray-600 mb-6">Start tracking your carbon footprint by logging your first activity.</p>
        <router-link to="/log-activity" class="btn-primary">
          Log Your First Activity
        </router-link>
      </div>

      <div v-else class="space-y-4">
        <div 
          v-for="activity in activities" 
          :key="activity.id"
          class="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
        >
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-4">
              <div class="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center">
                <span class="text-xl">{{ getCategoryIcon(activity.category_type) }}</span>
              </div>
              <div>
                <h3 class="font-medium text-gray-900">{{ activity.activity_type }}</h3>
                <p class="text-sm text-gray-600">{{ activity.category_name }}</p>
                <p class="text-xs text-gray-500">{{ formatDateTime(activity.start_timestamp) }}</p>
              </div>
            </div>
            
            <div class="flex items-center space-x-4">
              <div class="text-right">
                <p class="text-lg font-semibold" :class="getCO2Color(activity.co2_kg)">
                  {{ formatCO2(activity.co2_kg) }} kg
                </p>
                <p class="text-xs text-gray-500">CO₂e</p>
              </div>
              
              <div class="flex items-center space-x-2">
                <button 
                  @click="recalculateActivity(activity.id)"
                  class="p-2 text-gray-400 hover:text-primary-600 transition-colors"
                  title="Recalculate CO2"
                >
                  🔄
                </button>
                <button 
                  @click="deleteActivity(activity.id)"
                  class="p-2 text-gray-400 hover:text-red-600 transition-colors"
                  title="Delete Activity"
                >
                  🗑️
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useActivitiesStore } from '@/stores/activities'
import { useNotificationStore } from '@/stores/notifications'

const activitiesStore = useActivitiesStore()
const notificationStore = useNotificationStore()

const isLoading = ref(false)
const filters = reactive({
  category: '',
  dateRange: ''
})

const activities = computed(() => activitiesStore.activities)
const categories = computed(() => activitiesStore.categories)

const formatCO2 = (value) => {
  if (!value) return '0.0'
  return parseFloat(value).toFixed(1)
}

const formatDateTime = (timestamp) => {
  if (!timestamp) return ''
  return new Date(timestamp).toLocaleDateString() + ' ' + 
         new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

const getCategoryIcon = (categoryType) => {
  const icons = {
    transportation: '🚗',
    energy: '⚡',
    food: '🍽️',
    consumption: '🛍️',
    waste: '🗑️'
  }
  return icons[categoryType] || '📊'
}

const getCO2Color = (value) => {
  if (!value) return 'text-gray-500'
  if (value < 2) return 'text-green-600'
  if (value < 5) return 'text-yellow-600'
  return 'text-red-600'
}

const applyFilters = async () => {
  isLoading.value = true
  try {
    const filterParams = {}
    if (filters.category) filterParams.category = filters.category
    if (filters.dateRange) {
      // Add date range logic here
    }
    
    await activitiesStore.fetchActivities(filterParams)
  } catch (error) {
    notificationStore.error('Failed to load activities')
  } finally {
    isLoading.value = false
  }
}

const recalculateActivity = async (id) => {
  try {
    await activitiesStore.recalculateActivity(id)
    notificationStore.success('Activity CO₂ recalculated')
  } catch (error) {
    notificationStore.error('Failed to recalculate CO₂')
  }
}

const deleteActivity = async (id) => {
  if (confirm('Are you sure you want to delete this activity?')) {
    try {
      await activitiesStore.deleteActivity(id)
      notificationStore.success('Activity deleted')
    } catch (error) {
      notificationStore.error('Failed to delete activity')
    }
  }
}

onMounted(async () => {
  await applyFilters()
})
</script>