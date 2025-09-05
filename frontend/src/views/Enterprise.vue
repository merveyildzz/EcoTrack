<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <!-- Header -->
    <div class="bg-white dark:bg-gray-800 shadow">
      <div class="px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center py-6">
          <div>
            <h1 class="text-3xl font-bold text-gray-900 dark:text-white">
              Enterprise Dashboard
            </h1>
            <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
              Manage your organization's EcoTrack deployment
            </p>
          </div>
          <div class="flex space-x-3">
            <button
              @click="refreshData"
              class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700"
            >
              <RefreshIcon class="h-4 w-4 mr-2" />
              Refresh
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Navigation Tabs -->
    <div class="border-b border-gray-200 dark:border-gray-700">
      <nav class="px-4 sm:px-6 lg:px-8">
        <div class="flex space-x-8">
          <button
            v-for="tab in tabs"
            :key="tab.key"
            @click="activeTab = tab.key"
            :class="[
              'py-4 px-1 border-b-2 font-medium text-sm',
              activeTab === tab.key
                ? 'border-green-500 text-green-600 dark:text-green-400'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
            ]"
          >
            <component :is="tab.icon" class="h-5 w-5 inline mr-2" />
            {{ tab.name }}
          </button>
        </div>
      </nav>
    </div>

    <!-- Tab Content -->
    <div class="px-4 sm:px-6 lg:px-8 py-8">
      <!-- Overview Tab -->
      <div v-if="activeTab === 'overview'" class="space-y-6">
        <!-- Stats Cards -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div
            v-for="stat in orgStats"
            :key="stat.name"
            class="bg-white dark:bg-gray-800 p-6 rounded-lg shadow"
          >
            <dt class="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
              {{ stat.name }}
            </dt>
            <dd class="mt-1 text-3xl font-semibold text-gray-900 dark:text-white">
              {{ stat.value }}
            </dd>
            <div class="mt-2">
              <span
                :class="[
                  'inline-flex items-baseline px-2.5 py-0.5 rounded-full text-sm font-medium',
                  stat.changeType === 'increase'
                    ? 'bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-100'
                    : stat.changeType === 'decrease'
                    ? 'bg-red-100 text-red-800 dark:bg-red-800 dark:text-red-100'
                    : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
                ]"
              >
                {{ stat.change }}
              </span>
            </div>
          </div>
        </div>

        <!-- Charts Row -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <!-- User Activity Chart -->
          <div class="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
            <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">
              User Activity (30 days)
            </h3>
            <div class="h-64 flex items-center justify-center text-gray-500">
              Chart placeholder - User activity over time
            </div>
          </div>

          <!-- Carbon Savings Chart -->
          <div class="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
            <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">
              Carbon Savings by Team
            </h3>
            <div class="h-64 flex items-center justify-center text-gray-500">
              Chart placeholder - Carbon savings by team
            </div>
          </div>
        </div>
      </div>

      <!-- Organizations Tab -->
      <div v-if="activeTab === 'organizations'">
        <OrganizationManagement />
      </div>

      <!-- Users Tab -->
      <div v-if="activeTab === 'users'">
        <UserManagement />
      </div>

      <!-- Teams Tab -->
      <div v-if="activeTab === 'teams'">
        <TeamManagement />
      </div>

      <!-- Settings Tab -->
      <div v-if="activeTab === 'settings'" class="space-y-6">
        <!-- Organization Settings -->
        <div class="bg-white dark:bg-gray-800 shadow rounded-lg">
          <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
            <h3 class="text-lg font-medium text-gray-900 dark:text-white">
              Organization Settings
            </h3>
          </div>
          <div class="p-6">
            <form @submit.prevent="updateSettings" class="space-y-4">
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    Monthly Carbon Budget (kg)
                  </label>
                  <input
                    v-model="settings.carbon_budget_kg_monthly"
                    type="number"
                    step="0.001"
                    class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 dark:bg-gray-700 dark:border-gray-600"
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    Timezone
                  </label>
                  <select
                    v-model="settings.timezone"
                    class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 dark:bg-gray-700 dark:border-gray-600"
                  >
                    <option value="UTC">UTC</option>
                    <option value="America/New_York">Eastern Time</option>
                    <option value="America/Los_Angeles">Pacific Time</option>
                    <option value="Europe/London">London</option>
                    <option value="Europe/Paris">Paris</option>
                  </select>
                </div>
              </div>

              <div class="space-y-4">
                <div class="flex items-center">
                  <input
                    v-model="settings.enable_team_leaderboards"
                    type="checkbox"
                    class="h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300 rounded"
                  />
                  <label class="ml-2 block text-sm text-gray-700 dark:text-gray-300">
                    Enable Team Leaderboards
                  </label>
                </div>
                <div class="flex items-center">
                  <input
                    v-model="settings.enable_public_challenges"
                    type="checkbox"
                    class="h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300 rounded"
                  />
                  <label class="ml-2 block text-sm text-gray-700 dark:text-gray-300">
                    Enable Public Challenges
                  </label>
                </div>
                <div class="flex items-center">
                  <input
                    v-model="settings.require_activity_approval"
                    type="checkbox"
                    class="h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300 rounded"
                  />
                  <label class="ml-2 block text-sm text-gray-700 dark:text-gray-300">
                    Require Activity Approval
                  </label>
                </div>
              </div>

              <div class="pt-4">
                <button
                  type="submit"
                  class="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
                >
                  Save Settings
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import {
  ChartBarIcon,
  UsersIcon,
  CogIcon,
  BuildingOfficeIcon as OfficeBuildingIcon,
  UserGroupIcon,
  ArrowPathIcon as RefreshIcon
} from '@heroicons/vue/24/outline'
import OrganizationManagement from '@/components/enterprise/OrganizationManagement.vue'
import UserManagement from '@/components/enterprise/UserManagement.vue'
import TeamManagement from '@/components/enterprise/TeamManagement.vue'
import { enterpriseService } from '@/services/enterprise'
import { useToast } from '@/composables/useToast'

export default {
  name: 'Enterprise',
  components: {
    OrganizationManagement,
    UserManagement,
    TeamManagement,
    ChartBarIcon,
    UsersIcon,
    CogIcon,
    OfficeBuildingIcon,
    UserGroupIcon,
    RefreshIcon
  },
  setup() {
    const { showToast } = useToast()
    const activeTab = ref('overview')
    const loading = ref(false)
    const orgStats = ref([])
    const settings = ref({
      carbon_budget_kg_monthly: null,
      enable_team_leaderboards: true,
      enable_public_challenges: false,
      require_activity_approval: false,
      timezone: 'UTC'
    })

    const tabs = [
      { key: 'overview', name: 'Overview', icon: ChartBarIcon },
      { key: 'organizations', name: 'Organizations', icon: OfficeBuildingIcon },
      { key: 'users', name: 'Users', icon: UsersIcon },
      { key: 'teams', name: 'Teams', icon: UserGroupIcon },
      { key: 'settings', name: 'Settings', icon: CogIcon }
    ]

    const loadStats = async () => {
      try {
        const stats = await enterpriseService.getOrganizationStats()
        orgStats.value = [
          {
            name: 'Total Users',
            value: stats.total_users?.toLocaleString() || '0',
            change: '+12%',
            changeType: 'increase'
          },
          {
            name: 'Active Teams',
            value: stats.total_teams?.toString() || '0',
            change: '+3',
            changeType: 'increase'
          },
          {
            name: 'Carbon Saved (kg)',
            value: stats.total_co2_saved?.toFixed(1) || '0.0',
            change: '+15.3%',
            changeType: 'increase'
          },
          {
            name: 'Activities',
            value: stats.total_activities?.toLocaleString() || '0',
            change: '+24%',
            changeType: 'increase'
          }
        ]
      } catch (error) {
        console.error('Error loading stats:', error)
        showToast('Failed to load organization stats', 'error')
      }
    }

    const loadSettings = async () => {
      try {
        const orgSettings = await enterpriseService.getOrganizationSettings()
        settings.value = { ...settings.value, ...orgSettings }
      } catch (error) {
        console.error('Error loading settings:', error)
      }
    }

    const updateSettings = async () => {
      try {
        await enterpriseService.updateOrganizationSettings(settings.value)
        showToast('Settings updated successfully', 'success')
      } catch (error) {
        console.error('Error updating settings:', error)
        showToast('Failed to update settings', 'error')
      }
    }

    const refreshData = async () => {
      loading.value = true
      try {
        await Promise.all([loadStats(), loadSettings()])
        showToast('Data refreshed successfully', 'success')
      } catch (error) {
        showToast('Failed to refresh data', 'error')
      } finally {
        loading.value = false
      }
    }

    onMounted(() => {
      loadStats()
      loadSettings()
    })

    return {
      activeTab,
      loading,
      orgStats,
      settings,
      tabs,
      updateSettings,
      refreshData,
      RefreshIcon
    }
  }
}
</script>