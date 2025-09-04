<template>
  <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900">Profile Settings</h1>
      <p class="mt-2 text-gray-600">Manage your account information and preferences</p>
    </div>

    <!-- Profile Overview Card -->
    <div class="card mb-6">
      <div class="flex items-center space-x-6">
        <div class="w-20 h-20 bg-gradient-to-r from-primary-500 to-green-500 rounded-full flex items-center justify-center">
          <span class="text-2xl text-white font-bold">
            {{ user?.first_name?.charAt(0) || user?.email?.charAt(0).toUpperCase() }}
          </span>
        </div>
        <div>
          <h2 class="text-xl font-semibold text-gray-900">{{ user?.first_name }} {{ user?.last_name }}</h2>
          <p class="text-gray-600">{{ user?.email }}</p>
          <div class="flex items-center space-x-4 mt-2">
            <span class="px-2 py-1 bg-green-100 text-green-800 text-xs font-medium rounded-full">
              Member since {{ formatDate(user?.date_joined) }}
            </span>
            <span class="px-2 py-1 bg-primary-100 text-primary-800 text-xs font-medium rounded-full">
              {{ totalActivities }} activities logged
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Personal Information -->
    <div class="card mb-6">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-lg font-semibold text-gray-900">Personal Information</h3>
        <button 
          @click="editingPersonal = !editingPersonal"
          class="text-primary-600 hover:text-primary-700 text-sm font-medium"
        >
          {{ editingPersonal ? 'Cancel' : 'Edit' }}
        </button>
      </div>

      <form @submit.prevent="updatePersonalInfo" class="space-y-4">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">First Name</label>
            <input
              v-model="personalForm.first_name"
              type="text"
              class="input-field"
              :disabled="!editingPersonal"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Last Name</label>
            <input
              v-model="personalForm.last_name"
              type="text"
              class="input-field"
              :disabled="!editingPersonal"
            />
          </div>
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Email</label>
          <input
            v-model="personalForm.email"
            type="email"
            class="input-field"
            :disabled="!editingPersonal"
          />
        </div>

        <div v-if="editingPersonal" class="flex space-x-3">
          <button type="submit" class="btn-primary" :disabled="isUpdatingPersonal">
            {{ isUpdatingPersonal ? 'Saving...' : 'Save Changes' }}
          </button>
          <button type="button" @click="cancelPersonalEdit" class="btn-secondary">
            Cancel
          </button>
        </div>
      </form>
    </div>

    <!-- Carbon Footprint Goals -->
    <div class="card mb-6">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-lg font-semibold text-gray-900">Carbon Footprint Goals</h3>
        <button 
          @click="editingGoals = !editingGoals"
          class="text-primary-600 hover:text-primary-700 text-sm font-medium"
        >
          {{ editingGoals ? 'Cancel' : 'Edit' }}
        </button>
      </div>

      <form @submit.prevent="updateGoals" class="space-y-4">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Daily CO₂ Goal (kg)</label>
            <input
              v-model.number="goalsForm.daily_co2_goal"
              type="number"
              step="0.1"
              min="0"
              class="input-field"
              :disabled="!editingGoals"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Monthly CO₂ Goal (kg)</label>
            <input
              v-model.number="goalsForm.monthly_co2_goal"
              type="number"
              step="0.1"
              min="0"
              class="input-field"
              :disabled="!editingGoals"
            />
          </div>
        </div>

        <div v-if="editingGoals" class="flex space-x-3">
          <button type="submit" class="btn-primary" :disabled="isUpdatingGoals">
            {{ isUpdatingGoals ? 'Saving...' : 'Save Goals' }}
          </button>
          <button type="button" @click="cancelGoalsEdit" class="btn-secondary">
            Cancel
          </button>
        </div>
      </form>
    </div>

    <!-- Notification Preferences -->
    <div class="card mb-6">
      <h3 class="text-lg font-semibold text-gray-900 mb-4">Notification Preferences</h3>
      
      <div class="space-y-4">
        <div class="flex items-center justify-between">
          <div>
            <p class="font-medium text-gray-900">Daily Reminders</p>
            <p class="text-sm text-gray-600">Get reminded to log your daily activities</p>
          </div>
          <label class="flex items-center">
            <input
              v-model="notificationForm.daily_reminders"
              type="checkbox"
              class="form-checkbox h-5 w-5 text-primary-600"
              @change="updateNotifications"
            />
          </label>
        </div>

        <div class="flex items-center justify-between">
          <div>
            <p class="font-medium text-gray-900">Goal Achievements</p>
            <p class="text-sm text-gray-600">Celebrate when you reach your carbon goals</p>
          </div>
          <label class="flex items-center">
            <input
              v-model="notificationForm.goal_achievements"
              type="checkbox"
              class="form-checkbox h-5 w-5 text-primary-600"
              @change="updateNotifications"
            />
          </label>
        </div>

        <div class="flex items-center justify-between">
          <div>
            <p class="font-medium text-gray-900">Weekly Reports</p>
            <p class="text-sm text-gray-600">Receive weekly carbon footprint summaries</p>
          </div>
          <label class="flex items-center">
            <input
              v-model="notificationForm.weekly_reports"
              type="checkbox"
              class="form-checkbox h-5 w-5 text-primary-600"
              @change="updateNotifications"
            />
          </label>
        </div>
      </div>
    </div>

    <!-- Account Statistics -->
    <div class="card mb-6">
      <h3 class="text-lg font-semibold text-gray-900 mb-4">Account Statistics</h3>
      
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div class="text-center">
          <div class="text-3xl font-bold text-primary-600">{{ totalActivities }}</div>
          <div class="text-sm text-gray-600">Total Activities</div>
        </div>
        <div class="text-center">
          <div class="text-3xl font-bold text-green-600">{{ totalCO2Saved.toFixed(1) }}</div>
          <div class="text-sm text-gray-600">kg CO₂ Tracked</div>
        </div>
        <div class="text-center">
          <div class="text-3xl font-bold text-yellow-600">{{ streakDays }}</div>
          <div class="text-sm text-gray-600">Day Streak</div>
        </div>
      </div>
    </div>

    <!-- Danger Zone -->
    <div class="card border-red-200 bg-red-50">
      <h3 class="text-lg font-semibold text-red-800 mb-4">Danger Zone</h3>
      
      <div class="space-y-4">
        <div class="flex items-center justify-between">
          <div>
            <p class="font-medium text-red-800">Delete Account</p>
            <p class="text-sm text-red-600">Permanently delete your account and all data</p>
          </div>
          <button 
            @click="showDeleteConfirmation = true"
            class="px-4 py-2 bg-red-600 text-white text-sm font-medium rounded-lg hover:bg-red-700 transition-colors"
          >
            Delete Account
          </button>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteConfirmation" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 max-w-md w-mx-4">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Confirm Account Deletion</h3>
        <p class="text-gray-600 mb-6">
          This action cannot be undone. All your activities, data, and account information will be permanently deleted.
        </p>
        <div class="flex space-x-3">
          <button 
            @click="deleteAccount"
            class="flex-1 bg-red-600 text-white py-2 px-4 rounded-lg hover:bg-red-700 transition-colors"
            :disabled="isDeletingAccount"
          >
            {{ isDeletingAccount ? 'Deleting...' : 'Delete Account' }}
          </button>
          <button 
            @click="showDeleteConfirmation = false"
            class="flex-1 bg-gray-300 text-gray-700 py-2 px-4 rounded-lg hover:bg-gray-400 transition-colors"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useActivitiesStore } from '@/stores/activities'
import { useNotificationStore } from '@/stores/notifications'
import { useRouter } from 'vue-router'

const router = useRouter()
const authStore = useAuthStore()
const activitiesStore = useActivitiesStore()
const notificationStore = useNotificationStore()

const editingPersonal = ref(false)
const editingGoals = ref(false)
const isUpdatingPersonal = ref(false)
const isUpdatingGoals = ref(false)
const isDeletingAccount = ref(false)
const showDeleteConfirmation = ref(false)

const user = computed(() => authStore.user)
const totalActivities = ref(0)
const totalCO2Saved = ref(0)
const streakDays = ref(0)

const personalForm = reactive({
  first_name: '',
  last_name: '',
  email: ''
})

const goalsForm = reactive({
  daily_co2_goal: 10,
  monthly_co2_goal: 300
})

const notificationForm = reactive({
  daily_reminders: true,
  goal_achievements: true,
  weekly_reports: false
})

const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString()
}

const updatePersonalInfo = async () => {
  isUpdatingPersonal.value = true
  try {
    // In real app, this would call the API
    await new Promise(resolve => setTimeout(resolve, 1000)) // Simulate API call
    
    notificationStore.success('Personal information updated successfully')
    editingPersonal.value = false
  } catch (error) {
    notificationStore.error('Failed to update personal information')
  } finally {
    isUpdatingPersonal.value = false
  }
}

const cancelPersonalEdit = () => {
  // Reset form to original values
  if (user.value) {
    personalForm.first_name = user.value.first_name || ''
    personalForm.last_name = user.value.last_name || ''
    personalForm.email = user.value.email || ''
  }
  editingPersonal.value = false
}

const updateGoals = async () => {
  isUpdatingGoals.value = true
  try {
    // In real app, this would call the API
    await new Promise(resolve => setTimeout(resolve, 1000)) // Simulate API call
    
    notificationStore.success('Goals updated successfully')
    editingGoals.value = false
  } catch (error) {
    notificationStore.error('Failed to update goals')
  } finally {
    isUpdatingGoals.value = false
  }
}

const cancelGoalsEdit = () => {
  // Reset form to original values
  goalsForm.daily_co2_goal = 10
  goalsForm.monthly_co2_goal = 300
  editingGoals.value = false
}

const updateNotifications = async () => {
  try {
    // In real app, this would call the API
    await new Promise(resolve => setTimeout(resolve, 500)) // Simulate API call
    
    notificationStore.success('Notification preferences updated')
  } catch (error) {
    notificationStore.error('Failed to update notification preferences')
  }
}

const deleteAccount = async () => {
  isDeletingAccount.value = true
  try {
    // In real app, this would call the API
    await new Promise(resolve => setTimeout(resolve, 2000)) // Simulate API call
    
    await authStore.logout()
    router.push('/login')
    notificationStore.success('Account deleted successfully')
  } catch (error) {
    notificationStore.error('Failed to delete account')
  } finally {
    isDeletingAccount.value = false
    showDeleteConfirmation.value = false
  }
}

onMounted(async () => {
  // Initialize form with user data
  if (user.value) {
    personalForm.first_name = user.value.first_name || ''
    personalForm.last_name = user.value.last_name || ''
    personalForm.email = user.value.email || ''
  }

  // Load user statistics - in real app these would come from API
  totalActivities.value = 23
  totalCO2Saved.value = 145.6
  streakDays.value = 7
})
</script>