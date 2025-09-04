<template>
  <div class="min-h-screen bg-gradient-to-br from-primary-50 to-green-100 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full">
      <div class="text-center mb-8">
        <div class="w-16 h-16 bg-primary-600 rounded-xl flex items-center justify-center mx-auto mb-4">
          <span class="text-white font-bold text-2xl">🌱</span>
        </div>
        <h2 class="text-3xl font-bold text-gray-900">Join EcoTrack</h2>
        <p class="mt-2 text-gray-600">Start tracking your carbon footprint today</p>
      </div>

      <div class="bg-white rounded-2xl shadow-xl p-8">
        <form @submit.prevent="handleRegister" class="space-y-6">
          <div>
            <label for="email" class="block text-sm font-medium text-gray-700 mb-2">
              Email address
            </label>
            <input
              id="email"
              v-model="form.email"
              type="email"
              required
              class="input-field"
              placeholder="Enter your email"
              :disabled="isLoading"
            />
            <div v-if="errors.email" class="mt-1 text-sm text-red-600">
              {{ errors.email[0] }}
            </div>
          </div>

          <div>
            <label for="username" class="block text-sm font-medium text-gray-700 mb-2">
              Username
            </label>
            <input
              id="username"
              v-model="form.username"
              type="text"
              required
              class="input-field"
              placeholder="Choose a username"
              :disabled="isLoading"
            />
            <div v-if="errors.username" class="mt-1 text-sm text-red-600">
              {{ errors.username[0] }}
            </div>
          </div>

          <div>
            <label for="password" class="block text-sm font-medium text-gray-700 mb-2">
              Password
            </label>
            <input
              id="password"
              v-model="form.password"
              type="password"
              required
              class="input-field"
              placeholder="Create a password"
              :disabled="isLoading"
            />
            <div v-if="errors.password" class="mt-1 text-sm text-red-600">
              {{ errors.password[0] }}
            </div>
          </div>

          <div>
            <label for="password_confirm" class="block text-sm font-medium text-gray-700 mb-2">
              Confirm Password
            </label>
            <input
              id="password_confirm"
              v-model="form.password_confirm"
              type="password"
              required
              class="input-field"
              placeholder="Confirm your password"
              :disabled="isLoading"
            />
            <div v-if="errors.password_confirm" class="mt-1 text-sm text-red-600">
              {{ errors.password_confirm[0] }}
            </div>
          </div>

          <div>
            <label for="timezone" class="block text-sm font-medium text-gray-700 mb-2">
              Timezone
            </label>
            <select
              id="timezone"
              v-model="form.timezone"
              class="input-field"
              :disabled="isLoading"
            >
              <option value="UTC">UTC</option>
              <option value="America/New_York">Eastern Time (ET)</option>
              <option value="America/Chicago">Central Time (CT)</option>
              <option value="America/Denver">Mountain Time (MT)</option>
              <option value="America/Los_Angeles">Pacific Time (PT)</option>
              <option value="Europe/London">London (GMT)</option>
              <option value="Europe/Paris">Central European Time</option>
              <option value="Asia/Tokyo">Japan Standard Time</option>
              <option value="Asia/Shanghai">China Standard Time</option>
              <option value="Australia/Sydney">Australian Eastern Time</option>
            </select>
            <div v-if="errors.timezone" class="mt-1 text-sm text-red-600">
              {{ errors.timezone[0] }}
            </div>
          </div>

          <div class="flex items-start">
            <div class="flex items-center h-5">
              <input
                id="agree"
                v-model="form.agree"
                type="checkbox"
                required
                class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
              />
            </div>
            <div class="ml-3 text-sm">
              <label for="agree" class="text-gray-700">
                I agree to the 
                <a href="#" class="font-medium text-primary-600 hover:text-primary-500">Terms of Service</a> 
                and 
                <a href="#" class="font-medium text-primary-600 hover:text-primary-500">Privacy Policy</a>
              </label>
            </div>
          </div>

          <div>
            <button
              type="submit"
              class="w-full btn-primary flex items-center justify-center"
              :disabled="isLoading || !form.agree"
            >
              <div v-if="isLoading" class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
              {{ isLoading ? 'Creating account...' : 'Create account' }}
            </button>
          </div>

          <div v-if="errors.non_field_errors" class="bg-red-50 border border-red-200 rounded-lg p-3">
            <div class="text-sm text-red-600">
              {{ errors.non_field_errors[0] }}
            </div>
          </div>
        </form>

        <div class="mt-6">
          <div class="relative">
            <div class="absolute inset-0 flex items-center">
              <div class="w-full border-t border-gray-300"></div>
            </div>
            <div class="relative flex justify-center text-sm">
              <span class="px-2 bg-white text-gray-500">Already have an account?</span>
            </div>
          </div>

          <div class="mt-6">
            <router-link
              to="/login"
              class="w-full btn-secondary flex items-center justify-center"
            >
              Sign in instead
            </router-link>
          </div>
        </div>
      </div>

      <div class="mt-8 text-center">
        <p class="text-xs text-gray-500">
          By creating an account, you're joining thousands of users working to reduce their carbon footprint
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useNotificationStore } from '@/stores/notifications'

const router = useRouter()
const authStore = useAuthStore()
const notificationStore = useNotificationStore()

const form = reactive({
  email: '',
  username: '',
  password: '',
  password_confirm: '',
  timezone: Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC',
  agree: false
})

const errors = ref({})
const isLoading = ref(false)

const handleRegister = async () => {
  isLoading.value = true
  errors.value = {}

  // Client-side validation
  if (form.password !== form.password_confirm) {
    errors.value = { password_confirm: ['Passwords do not match'] }
    isLoading.value = false
    return
  }

  try {
    await authStore.register({
      email: form.email,
      username: form.username,
      password: form.password,
      password_confirm: form.password_confirm,
      timezone: form.timezone
    })
    
    notificationStore.success('Account created successfully! Welcome to EcoTrack.')
    router.push('/dashboard')
  } catch (error) {
    if (error.response?.data) {
      errors.value = error.response.data
    } else {
      notificationStore.error('Registration failed. Please try again.')
    }
  } finally {
    isLoading.value = false
  }
}
</script>