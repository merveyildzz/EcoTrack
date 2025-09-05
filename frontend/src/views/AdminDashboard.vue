<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <!-- Header -->
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900">Admin Dashboard</h1>
      <p class="mt-2 text-gray-600">Manage and monitor your organization's environmental impact</p>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="flex items-center justify-center py-12">
      <div class="w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full animate-spin"></div>
      <span class="ml-3 text-gray-600">Loading admin dashboard...</span>
    </div>

    <!-- Admin Dashboard Content -->
    <div v-else>
      <!-- Admin Key Metrics -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <!-- Total Users -->
        <div class="metric-card">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600">Total Users</p>
              <p class="text-2xl font-bold text-gray-900">
                {{ adminStats?.total_users?.toLocaleString() || '0' }}
              </p>
              <p class="text-xs text-gray-500 mt-1">active members</p>
            </div>
            <div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <UsersIcon class="w-6 h-6 text-blue-600" />
            </div>
          </div>
          <div class="mt-4">
            <div class="flex items-center text-xs">
              <span class="text-green-600">↑ {{ adminStats?.user_growth || '0' }}%</span>
              <span class="text-gray-500 ml-1">vs last month</span>
            </div>
          </div>
        </div>

        <!-- Total Organizations -->
        <div class="metric-card">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600">Organizations</p>
              <p class="text-2xl font-bold text-gray-900">
                {{ adminStats?.total_organizations || '0' }}
              </p>
              <p class="text-xs text-gray-500 mt-1">registered</p>
            </div>
            <div class="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
              <OfficeBuildingIcon class="w-6 h-6 text-purple-600" />
            </div>
          </div>
          <div class="mt-4">
            <div class="flex items-center text-xs">
              <span class="text-green-600">+{{ adminStats?.new_orgs || '0' }}</span>
              <span class="text-gray-500 ml-1">this month</span>
            </div>
          </div>
        </div>

        <!-- Total CO2 Saved -->
        <div class="metric-card">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600">Total CO₂ Saved</p>
              <p class="text-2xl font-bold text-green-600">
                {{ formatCO2(adminStats?.total_co2_saved || 0) }}
              </p>
              <p class="text-xs text-gray-500 mt-1">kg CO₂e platform-wide</p>
            </div>
            <div class="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
              <span class="text-green-600 text-xl">🌱</span>
            </div>
          </div>
          <div class="mt-4">
            <div class="flex items-center text-xs">
              <span class="text-green-600">↑ {{ adminStats?.co2_growth || '0' }}%</span>
              <span class="text-gray-500 ml-1">vs last month</span>
            </div>
          </div>
        </div>

        <!-- System Health -->
        <div class="metric-card">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600">System Status</p>
              <p class="text-2xl font-bold text-green-600">
                {{ systemHealth?.status === 'healthy' ? '✓ Healthy' : '⚠ Issues' }}
              </p>
              <p class="text-xs text-gray-500 mt-1">{{ systemHealth?.uptime || '99.9%' }} uptime</p>
            </div>
            <div class="w-12 h-12 bg-indigo-100 rounded-lg flex items-center justify-center">
              <ServerIcon class="w-6 h-6 text-indigo-600" />
            </div>
          </div>
          <div class="mt-4">
            <div class="flex items-center text-xs">
              <span class="text-green-600">All systems operational</span>
            </div>
          </div>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- Main Chart Area -->
        <div class="lg:col-span-2 space-y-6">
          <!-- Platform Activity Chart -->
          <div class="card">
            <div class="flex items-center justify-between mb-6">
              <h3 class="text-lg font-semibold text-gray-900">Platform Activity</h3>
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
            <div class="h-64 flex items-center justify-center text-gray-500">
              Chart: User activity, registrations, and CO₂ savings over time
            </div>
          </div>

          <!-- Top Organizations -->
          <div class="card">
            <div class="flex items-center justify-between mb-6">
              <h3 class="text-lg font-semibold text-gray-900">Top Organizations</h3>
              <router-link to="/enterprise" class="text-sm text-primary-600 hover:text-primary-700">
                View All
              </router-link>
            </div>
            <div class="space-y-4">
              <div
                v-for="org in topOrganizations"
                :key="org.id"
                class="flex items-center justify-between p-4 bg-gray-50 rounded-lg"
              >
                <div class="flex items-center space-x-3">
                  <img
                    v-if="org.logo"
                    :src="org.logo"
                    :alt="org.name"
                    class="w-10 h-10 rounded-lg"
                  />
                  <div
                    v-else
                    class="w-10 h-10 rounded-lg bg-blue-500 flex items-center justify-center"
                  >
                    <span class="text-white font-medium text-sm">
                      {{ org.name.charAt(0) }}
                    </span>
                  </div>
                  <div>
                    <div class="font-medium text-gray-900">{{ org.name }}</div>
                    <div class="text-sm text-gray-500">{{ org.member_count }} members</div>
                  </div>
                </div>
                <div class="text-right">
                  <div class="font-medium text-green-600">{{ formatCO2(org.total_co2_saved) }}kg</div>
                  <div class="text-sm text-gray-500">CO₂ saved</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Admin Sidebar -->
        <div class="space-y-6">
          <!-- Quick Admin Actions -->
          <div class="card">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
            <div class="space-y-3">
              <router-link
                to="/enterprise"
                class="flex items-center p-3 bg-blue-50 hover:bg-blue-100 rounded-lg transition-colors group"
              >
                <div class="w-10 h-10 bg-blue-200 rounded-lg flex items-center justify-center mr-3 group-hover:bg-blue-300">
                  <OfficeBuildingIcon class="w-5 h-5 text-blue-700" />
                </div>
                <div>
                  <p class="font-medium text-gray-900">Enterprise Panel</p>
                  <p class="text-sm text-gray-600">Manage organizations</p>
                </div>
              </router-link>
              
              <button 
                @click="exportData"
                class="w-full flex items-center p-3 bg-green-50 hover:bg-green-100 rounded-lg transition-colors group"
              >
                <div class="w-10 h-10 bg-green-200 rounded-lg flex items-center justify-center mr-3 group-hover:bg-green-300">
                  <DownloadIcon class="w-5 h-5 text-green-700" />
                </div>
                <div class="text-left">
                  <p class="font-medium text-gray-900">Export Data</p>
                  <p class="text-sm text-gray-600">Download reports</p>
                </div>
              </button>

              <button 
                @click="refreshAdminData"
                class="w-full flex items-center p-3 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors group"
              >
                <div class="w-10 h-10 bg-gray-200 rounded-lg flex items-center justify-center mr-3 group-hover:bg-gray-300">
                  <RefreshIcon class="w-5 h-5 text-gray-700" />
                </div>
                <div class="text-left">
                  <p class="font-medium text-gray-900">Refresh Data</p>
                  <p class="text-sm text-gray-600">Update dashboard</p>
                </div>
              </button>
            </div>
          </div>

          <!-- Recent User Activity -->
          <div class="card">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-lg font-semibold text-gray-900">Recent Users</h3>
              <router-link to="/enterprise" class="text-sm text-primary-600 hover:text-primary-700">
                View All
              </router-link>
            </div>
            
            <div class="space-y-3">
              <div 
                v-for="user in recentUsers"
                :key="user.id"
                class="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
              >
                <div class="flex items-center space-x-3">
                  <img
                    v-if="user.avatar"
                    :src="user.avatar"
                    :alt="user.name"
                    class="w-8 h-8 rounded-full"
                  />
                  <div
                    v-else
                    class="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center"
                  >
                    <span class="text-white text-xs font-medium">
                      {{ user.email?.charAt(0).toUpperCase() || 'U' }}
                    </span>
                  </div>
                  <div>
                    <p class="text-sm font-medium text-gray-900">{{ user.full_name || user.email }}</p>
                    <p class="text-xs text-gray-500">{{ user.organization?.name || 'No org' }}</p>
                  </div>
                </div>
                <div class="text-right">
                  <span
                    :class="[
                      'px-2 py-1 text-xs font-medium rounded-full',
                      user.status === 'active'
                        ? 'bg-green-100 text-green-800'
                        : user.status === 'invited'
                        ? 'bg-yellow-100 text-yellow-800'
                        : 'bg-red-100 text-red-800'
                    ]"
                  >
                    {{ user.status }}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- System Alerts -->
          <div v-if="systemAlerts?.length > 0" class="card">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">System Alerts</h3>
            <div class="space-y-3">
              <div
                v-for="alert in systemAlerts"
                :key="alert.id"
                :class="[
                  'p-3 rounded-lg border',
                  alert.severity === 'high'
                    ? 'bg-red-50 border-red-200'
                    : alert.severity === 'medium'
                    ? 'bg-yellow-50 border-yellow-200'
                    : 'bg-blue-50 border-blue-200'
                ]"
              >
                <div class="flex items-start space-x-2">
                  <span
                    :class="[
                      'text-sm',
                      alert.severity === 'high'
                        ? 'text-red-600'
                        : alert.severity === 'medium'
                        ? 'text-yellow-600'
                        : 'text-blue-600'
                    ]"
                  >
                    {{ alert.severity === 'high' ? '🚨' : alert.severity === 'medium' ? '⚠️' : 'ℹ️' }}
                  </span>
                  <div class="flex-1">
                    <p class="text-sm font-medium text-gray-900">{{ alert.title }}</p>
                    <p class="text-xs text-gray-600 mt-1">{{ alert.message }}</p>
                    <p class="text-xs text-gray-500 mt-1">{{ formatDateShort(alert.created_at) }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Platform Stats -->
          <div class="card">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">Platform Overview</h3>
            <div class="space-y-4">
              <div class="flex justify-between items-center">
                <span class="text-sm text-gray-600">Active Sessions</span>
                <span class="font-medium">{{ adminStats?.active_sessions || 0 }}</span>
              </div>
              <div class="flex justify-between items-center">
                <span class="text-sm text-gray-600">Daily Activities</span>
                <span class="font-medium">{{ adminStats?.daily_activities || 0 }}</span>
              </div>
              <div class="flex justify-between items-center">
                <span class="text-sm text-gray-600">Storage Used</span>
                <span class="font-medium">{{ adminStats?.storage_used || '0 GB' }}</span>
              </div>
              <div class="flex justify-between items-center">
                <span class="text-sm text-gray-600">API Calls Today</span>
                <span class="font-medium">{{ adminStats?.api_calls?.toLocaleString() || '0' }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { 
  UsersIcon, 
  BuildingOfficeIcon as OfficeBuildingIcon, 
  ServerIcon, 
  ArrowDownTrayIcon as DownloadIcon, 
  ArrowPathIcon as RefreshIcon 
} from '@heroicons/vue/24/outline'
import { enterpriseService } from '@/services/enterprise'
import { useNotificationStore } from '@/stores/notifications'

const notificationStore = useNotificationStore()

const isLoading = ref(true)
const chartPeriod = ref('7D')

// Admin-specific data
const adminStats = ref({})
const systemHealth = ref({})
const topOrganizations = ref([])
const recentUsers = ref([])
const systemAlerts = ref([])

const formatCO2 = (value) => {
  if (!value) return '0.0'
  return parseFloat(value).toLocaleString(undefined, { minimumFractionDigits: 1, maximumFractionDigits: 1 })
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

const loadAdminData = async () => {
  try {
    // Load admin dashboard data
    const [stats, organizations, users] = await Promise.all([
      enterpriseService.getDashboardData(),
      enterpriseService.getOrganizations({ limit: 5, ordering: '-total_co2_saved' }),
      enterpriseService.getUsers({ limit: 5, ordering: '-created_at' })
    ])

    adminStats.value = stats
    topOrganizations.value = organizations.results || organizations.slice(0, 5)
    recentUsers.value = users.results || users.slice(0, 5)

    // Mock system health data
    systemHealth.value = {
      status: 'healthy',
      uptime: '99.9%'
    }

    // Mock system alerts
    systemAlerts.value = [
      {
        id: 1,
        severity: 'medium',
        title: 'High API Usage',
        message: 'API usage is above 80% of monthly quota',
        created_at: new Date().toISOString()
      }
    ]

  } catch (error) {
    console.error('Error loading admin data:', error)
    notificationStore.error('Failed to load admin dashboard')
  }
}

const exportData = async () => {
  try {
    const blob = await enterpriseService.exportReport('platform-summary')
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `platform-report-${new Date().toISOString().split('T')[0]}.csv`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
    notificationStore.success('Report exported successfully')
  } catch (error) {
    notificationStore.error('Failed to export report')
  }
}

const refreshAdminData = async () => {
  try {
    await loadAdminData()
    notificationStore.success('Admin dashboard refreshed')
  } catch (error) {
    notificationStore.error('Failed to refresh dashboard')
  }
}

onMounted(async () => {
  try {
    await loadAdminData()
  } finally {
    isLoading.value = false
  }
})
</script>

<style scoped>
.metric-card {
  @apply bg-white rounded-lg shadow p-6 border border-gray-200;
}

.card {
  @apply bg-white rounded-lg shadow p-6 border border-gray-200;
}
</style>