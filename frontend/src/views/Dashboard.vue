<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <!-- Header -->
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900">My Dashboard</h1>
      <p class="mt-2 text-gray-600">Track your personal environmental impact and make a difference</p>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="flex items-center justify-center py-12">
      <div class="w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full animate-spin"></div>
      <span class="ml-3 text-gray-600">Loading your dashboard...</span>
    </div>

    <!-- Dashboard Content -->
    <div v-else>
      <!-- Key Metrics -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <!-- Today's CO2 -->
        <div class="metric-card">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600">Today's CO₂</p>
              <p class="text-2xl font-bold text-gray-900">
                {{ formatCO2(dashboardData?.today_co2_kg || 0) }}
              </p>
              <p class="text-xs text-gray-500 mt-1">kg CO₂e</p>
            </div>
            <div class="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center">
              <span class="text-primary-600 text-xl">📊</span>
            </div>
          </div>
          <div class="mt-4">
            <div class="flex items-center text-xs">
              <span class="text-green-600">↓ 12%</span>
              <span class="text-gray-500 ml-1">vs yesterday</span>
            </div>
          </div>
        </div>

        <!-- Weekly CO2 -->
        <div class="metric-card">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600">This Week</p>
              <p class="text-2xl font-bold text-gray-900">
                {{ formatCO2(dashboardData?.weekly_co2_kg || 0) }}
              </p>
              <p class="text-xs text-gray-500 mt-1">kg CO₂e</p>
            </div>
            <div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <span class="text-blue-600 text-xl">📈</span>
            </div>
          </div>
          <div class="mt-4">
            <div class="flex items-center text-xs">
              <span class="text-red-600">↑ 5%</span>
              <span class="text-gray-500 ml-1">vs last week</span>
            </div>
          </div>
        </div>

        <!-- Activities Count -->
        <div class="metric-card">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600">Activities Today</p>
              <p class="text-2xl font-bold text-gray-900">
                {{ dashboardData?.activities_today || 0 }}
              </p>
              <p class="text-xs text-gray-500 mt-1">logged</p>
            </div>
            <div class="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center">
              <span class="text-yellow-600 text-xl">✨</span>
            </div>
          </div>
          <div class="mt-4">
            <div class="flex items-center text-xs">
              <span class="text-green-600">+3</span>
              <span class="text-gray-500 ml-1">new today</span>
            </div>
          </div>
        </div>

        <!-- Carbon Rating -->
        <div class="metric-card">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600">Carbon Rating</p>
              <p class="text-2xl font-bold text-green-600">B+</p>
              <p class="text-xs text-gray-500 mt-1">Good progress</p>
            </div>
            <div class="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
              <span class="text-green-600 text-xl">🌱</span>
            </div>
          </div>
          <div class="mt-4">
            <div class="flex items-center text-xs">
              <span class="text-green-600">Improved</span>
              <span class="text-gray-500 ml-1">this month</span>
            </div>
          </div>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- Main Chart Area -->
        <div class="lg:col-span-2">
          <!-- CO2 Trend Chart -->
          <div class="card mb-6">
            <div class="flex items-center justify-between mb-6">
              <h3 class="text-lg font-semibold text-gray-900">CO₂ Emissions Trend</h3>
              <div class="flex space-x-2">
                <button 
                  v-for="period in ['7D', '30D', '90D']" 
                  :key="period"
                  @click="chartPeriod = period"
                  class="px-3 py-1 text-sm rounded-lg transition-colors"
                  :class="chartPeriod === period 
                    ? 'bg-primary-100 text-primary-700 font-medium' 
                    : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'"
                >
                  {{ period }}
                </button>
              </div>
            </div>
            <div class="h-64">
              <TrendChart :data="trendData" :period="chartPeriod" />
            </div>
          </div>

          <!-- Category Breakdown -->
          <div class="card">
            <h3 class="text-lg font-semibold text-gray-900 mb-6">Emissions by Category</h3>
            <div class="h-64">
              <CategoryChart :data="categoryData" />
            </div>
          </div>
        </div>

        <!-- Sidebar -->
        <div class="space-y-6">
          <!-- Quick Actions -->
          <div class="card">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
            <div class="space-y-3">
              <router-link
                to="/log-activity"
                class="flex items-center p-3 bg-primary-50 hover:bg-primary-100 rounded-lg transition-colors group"
              >
                <div class="w-10 h-10 bg-primary-200 rounded-lg flex items-center justify-center mr-3 group-hover:bg-primary-300">
                  <span class="text-primary-700">➕</span>
                </div>
                <div>
                  <p class="font-medium text-gray-900">Log Activity</p>
                  <p class="text-sm text-gray-600">Add new carbon activity</p>
                </div>
              </router-link>
              
              <button 
                @click="refreshData"
                class="w-full flex items-center p-3 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors group"
              >
                <div class="w-10 h-10 bg-gray-200 rounded-lg flex items-center justify-center mr-3 group-hover:bg-gray-300">
                  <span class="text-gray-700">🔄</span>
                </div>
                <div class="text-left">
                  <p class="font-medium text-gray-900">Refresh Data</p>
                  <p class="text-sm text-gray-600">Update dashboard</p>
                </div>
              </button>
            </div>
          </div>

          <!-- Recent Activities -->
          <div class="card">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-lg font-semibold text-gray-900">Recent Activities</h3>
              <router-link 
                to="/activities" 
                class="text-sm text-primary-600 hover:text-primary-700 font-medium"
              >
                View all
              </router-link>
            </div>
            
            <div v-if="recentActivities.length === 0" class="text-center py-8 text-gray-500">
              <span class="text-4xl mb-2 block">📝</span>
              <p class="text-sm">No activities logged today</p>
              <router-link 
                to="/log-activity" 
                class="text-primary-600 hover:text-primary-700 text-sm font-medium"
              >
                Log your first activity
              </router-link>
            </div>
            
            <div v-else class="space-y-3">
              <div 
                v-for="activity in recentActivities" 
                :key="activity.id"
                class="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
              >
                <div class="flex items-center space-x-3">
                  <div class="w-8 h-8 bg-white rounded-lg flex items-center justify-center">
                    <span class="text-sm">{{ getCategoryIcon(activity.category_type) }}</span>
                  </div>
                  <div>
                    <p class="text-sm font-medium text-gray-900">{{ activity.activity_type }}</p>
                    <p class="text-xs text-gray-500">{{ formatTime(activity.start_timestamp) }}</p>
                  </div>
                </div>
                <div class="text-right">
                  <p class="text-sm font-medium" :class="getCO2Color(activity.co2_kg)">
                    {{ formatCO2(activity.co2_kg) }}
                  </p>
                  <p class="text-xs text-gray-500">kg CO₂e</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Social Stats -->
          <div class="card">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">Your Achievements</h3>
            <div class="space-y-4">
              <!-- Current Rank -->
              <div class="flex items-center justify-between p-3 bg-primary-50 rounded-lg">
                <div class="flex items-center space-x-3">
                  <div class="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
                    <span class="text-primary-700">🏆</span>
                  </div>
                  <div>
                    <p class="font-medium text-gray-900">Global Rank</p>
                    <p class="text-sm text-gray-600">#{{ socialStats?.global_rank || '---' }}</p>
                  </div>
                </div>
                <router-link to="/leaderboards" class="text-sm text-primary-600 hover:text-primary-700">
                  View All
                </router-link>
              </div>

              <!-- Badges -->
              <div class="flex items-center justify-between p-3 bg-yellow-50 rounded-lg">
                <div class="flex items-center space-x-3">
                  <div class="w-10 h-10 bg-yellow-100 rounded-lg flex items-center justify-center">
                    <span class="text-yellow-700">🏅</span>
                  </div>
                  <div>
                    <p class="font-medium text-gray-900">Badges Earned</p>
                    <p class="text-sm text-gray-600">{{ socialStats?.badges_earned || 0 }} total</p>
                  </div>
                </div>
                <router-link to="/badges" class="text-sm text-primary-600 hover:text-primary-700">
                  View All
                </router-link>
              </div>

              <!-- Current Streak -->
              <div class="flex items-center justify-between p-3 bg-orange-50 rounded-lg">
                <div class="flex items-center space-x-3">
                  <div class="w-10 h-10 bg-orange-100 rounded-lg flex items-center justify-center">
                    <span class="text-orange-700">🔥</span>
                  </div>
                  <div>
                    <p class="font-medium text-gray-900">Daily Streak</p>
                    <p class="text-sm text-gray-600">{{ socialStats?.current_streak || 0 }} days</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Recent Achievements -->
          <div v-if="recentBadges?.length > 0" class="card">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">Recent Achievements</h3>
            <div class="space-y-3">
              <div 
                v-for="badge in recentBadges.slice(0, 3)" 
                :key="badge.id"
                class="flex items-center space-x-3 p-2 bg-gray-50 rounded-lg"
              >
                <div class="w-8 h-8 bg-yellow-100 rounded-lg flex items-center justify-center">
                  <span class="text-sm">🏆</span>
                </div>
                <div class="flex-1">
                  <p class="text-sm font-medium text-gray-900">{{ badge.badge.name }}</p>
                  <p class="text-xs text-gray-500">{{ formatDateShort(badge.earned_at) }}</p>
                </div>
                <span class="text-xs text-primary-600 font-medium">+{{ badge.badge.points }}pts</span>
              </div>
            </div>
            <router-link to="/badges" class="block text-center text-sm text-primary-600 hover:text-primary-700 mt-3">
              View All Badges
            </router-link>
          </div>

          <!-- Active Challenges -->
          <div v-if="activeChallenges?.length > 0" class="card">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">Active Challenges</h3>
            <div class="space-y-3">
              <div 
                v-for="challenge in activeChallenges.slice(0, 2)" 
                :key="challenge.id"
                class="p-3 bg-green-50 rounded-lg border border-green-200"
              >
                <div class="flex items-center justify-between mb-2">
                  <h4 class="font-medium text-gray-900 text-sm">{{ challenge.challenge.title }}</h4>
                  <span class="text-xs text-green-600">{{ challenge.progress_percentage.toFixed(0) }}%</span>
                </div>
                <div class="w-full bg-green-200 rounded-full h-2">
                  <div 
                    class="bg-green-600 h-2 rounded-full transition-all duration-500"
                    :style="{ width: `${challenge.progress_percentage}%` }"
                  ></div>
                </div>
                <p class="text-xs text-gray-600 mt-2">
                  {{ challenge.current_progress.toFixed(1) }}/{{ challenge.challenge.goal_value }} 
                  {{ challenge.challenge.goal_unit }}
                </p>
              </div>
            </div>
            <router-link to="/challenges" class="block text-center text-sm text-primary-600 hover:text-primary-700 mt-3">
              View All Challenges
            </router-link>
          </div>

          <!-- Environmental Tip -->
          <div class="card bg-gradient-to-r from-green-50 to-primary-50 border-green-200">
            <div class="flex items-start space-x-3">
              <div class="w-10 h-10 bg-green-200 rounded-lg flex items-center justify-center flex-shrink-0">
                <span class="text-green-700">💡</span>
              </div>
              <div>
                <h4 class="font-medium text-gray-900 mb-2">Daily Eco Tip</h4>
                <p class="text-sm text-gray-700 leading-relaxed">
                  Taking public transport instead of driving can reduce your daily carbon footprint by up to 50%. 
                  Try combining trips or walking short distances!
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useActivitiesStore } from '@/stores/activities'
import { useNotificationStore } from '@/stores/notifications'
import socialApi from '@/services/social'
import TrendChart from '@/components/TrendChart.vue'
import CategoryChart from '@/components/CategoryChart.vue'

const activitiesStore = useActivitiesStore()
const notificationStore = useNotificationStore()

const isLoading = ref(true)
const chartPeriod = ref('7D')

// Social data
const socialStats = ref(null)
const recentBadges = ref([])
const activeChallenges = ref([])

const dashboardData = computed(() => activitiesStore.dashboardData)
const recentActivities = computed(() => dashboardData.value?.recent_activities || [])

// Mock data for charts - in a real app this would come from the API
const trendData = computed(() => {
  // Generate sample trend data based on period
  const days = chartPeriod.value === '7D' ? 7 : chartPeriod.value === '30D' ? 30 : 90
  return Array.from({ length: days }, (_, i) => ({
    date: new Date(Date.now() - (days - 1 - i) * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    co2: Math.random() * 10 + 5
  }))
})

const categoryData = computed(() => {
  const breakdown = dashboardData.value?.category_breakdown || {}
  return Object.entries(breakdown).map(([category, value]) => ({
    category,
    value,
    color: getCategoryColor(category)
  }))
})

const formatCO2 = (value) => {
  if (!value) return '0.0'
  return parseFloat(value).toFixed(1)
}

const formatTime = (timestamp) => {
  if (!timestamp) return ''
  return new Date(timestamp).toLocaleTimeString([], { 
    hour: '2-digit', 
    minute: '2-digit' 
  })
}

const formatDateShort = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  const now = new Date()
  const diffInDays = Math.floor((now - date) / (1000 * 60 * 60 * 24))
  
  if (diffInDays === 0) return 'Today'
  if (diffInDays === 1) return 'Yesterday'
  if (diffInDays < 7) return `${diffInDays}d ago`
  return date.toLocaleDateString()
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

const getCategoryColor = (category) => {
  const colors = {
    'Car Travel': '#ef4444',
    'Public Transport': '#22c55e',
    'Air Travel': '#f59e0b',
    'Electricity': '#3b82f6',
    'Natural Gas': '#8b5cf6',
    'Food': '#06b6d4'
  }
  return colors[category] || '#6b7280'
}

const refreshData = async () => {
  try {
    await activitiesStore.fetchDashboard()
    notificationStore.success('Dashboard data refreshed')
  } catch (error) {
    notificationStore.error('Failed to refresh data')
  }
}

const loadSocialData = async () => {
  try {
    const dashboard = await socialApi.getUserDashboard()
    socialStats.value = dashboard.stats
    recentBadges.value = dashboard.recent_badges || []
    activeChallenges.value = dashboard.active_challenges || []
    
    // Add mock global rank for demo
    if (socialStats.value) {
      socialStats.value.global_rank = Math.floor(Math.random() * 1000) + 1
    }
  } catch (error) {
    console.error('Error loading social data:', error)
    // Don't show error notification for social data as it's not critical
  }
}

onMounted(async () => {
  try {
    await Promise.all([
      activitiesStore.fetchDashboard(),
      loadSocialData()
    ])
  } catch (error) {
    notificationStore.error('Failed to load dashboard data')
  } finally {
    isLoading.value = false
  }
})
</script>