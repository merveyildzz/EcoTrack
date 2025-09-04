<template>
  <div class="min-h-screen bg-gradient-to-br from-primary-50 to-green-100 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full">
      <div class="text-center mb-8">
        <div class="w-16 h-16 bg-primary-600 rounded-xl flex items-center justify-center mx-auto mb-4">
          <span class="text-white font-bold text-2xl">🌱</span>
        </div>
        <h2 class="text-3xl font-bold text-gray-900">Welcome to EcoTrack</h2>
        <p class="mt-2 text-gray-600">Track your carbon footprint with AI-powered insights</p>
      </div>

      <div class="bg-white rounded-2xl shadow-xl p-8">
        <form @submit.prevent="handleLogin" class="space-y-6">
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
            <label for="password" class="block text-sm font-medium text-gray-700 mb-2">
              Password
            </label>
            <input
              id="password"
              v-model="form.password"
              type="password"
              required
              class="input-field"
              placeholder="Enter your password"
              :disabled="isLoading"
            />
            <div v-if="errors.password" class="mt-1 text-sm text-red-600">
              {{ errors.password[0] }}
            </div>
          </div>

          <div class="flex items-center justify-between">
            <div class="flex items-center">
              <input
                id="remember-me"
                v-model="form.remember"
                type="checkbox"
                class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
              />
              <label for="remember-me" class="ml-2 block text-sm text-gray-700">
                Remember me
              </label>
            </div>
            <div class="text-sm">
              <a href="#" class="font-medium text-primary-600 hover:text-primary-500">
                Forgot your password?
              </a>
            </div>
          </div>

          <div>
            <button
              type="submit"
              class="w-full btn-primary flex items-center justify-center"
              :disabled="isLoading"
            >
              <div v-if="isLoading" class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
              {{ isLoading ? 'Signing in...' : 'Sign in' }}
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
              <span class="px-2 bg-white text-gray-500">Don't have an account?</span>
            </div>
          </div>

          <div class="mt-6">
            <router-link
              to="/register"
              class="w-full btn-secondary flex items-center justify-center"
            >
              Create an account
            </router-link>
          </div>
        </div>
      </div>

      <div class="mt-8 text-center">
        <p class="text-xs text-gray-500">
          By signing in, you agree to our 
          <a href="#" class="text-primary-600 hover:underline">Terms of Service</a> and 
          <a href="#" class="text-primary-600 hover:underline">Privacy Policy</a>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useNotificationStore } from '@/stores/notifications'

const router = useRouter()
const authStore = useAuthStore()
const notificationStore = useNotificationStore()

const form = reactive({
  email: '',
  password: '',
  remember: false
})

const errors = ref({})
const isLoading = ref(false)

const handleLogin = async () => {
  isLoading.value = true
  errors.value = {}

  try {
    await authStore.login({
      email: form.email,
      password: form.password
    })
    
    notificationStore.success('Welcome back! Successfully signed in.')
    router.push('/dashboard')
  } catch (error) {
    if (error.response?.status === 401) {
      errors.value = { non_field_errors: ['Invalid email or password'] }
    } else if (error.response?.data) {
      errors.value = error.response.data
    } else {
      notificationStore.error('Login failed. Please try again.')
    }
  } finally {
    isLoading.value = false
  }
}
</script>