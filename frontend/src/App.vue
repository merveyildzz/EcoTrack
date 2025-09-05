<template>
  <div id="app" class="min-h-screen bg-gray-50">
    <!-- Navigation -->
    <nav v-if="!isAuthPage" class="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-40">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <div class="flex items-center">
            <router-link :to="isAdmin ? '/admin' : '/dashboard'" class="flex items-center space-x-2">
              <div class="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
                <span class="text-white font-bold text-sm">🌱</span>
              </div>
              <h1 class="text-xl font-bold text-gray-900">EcoTrack</h1>
            </router-link>
          </div>
          
          <div class="hidden md:flex items-center space-x-6">
            <router-link 
              :to="isAdmin ? '/admin' : '/dashboard'" 
              class="text-gray-700 hover:text-primary-600 px-3 py-2 text-sm font-medium transition-colors"
              :class="{ 'text-primary-600 border-b-2 border-primary-600': ($route.path === '/dashboard' && !isAdmin) || ($route.path === '/admin' && isAdmin) }"
            >
              {{ isAdmin ? 'Admin' : 'Dashboard' }}
            </router-link>
            <router-link 
              to="/activities" 
              class="text-gray-700 hover:text-primary-600 px-3 py-2 text-sm font-medium transition-colors"
              :class="{ 'text-primary-600 border-b-2 border-primary-600': $route.path.startsWith('/activities') }"
            >
              Activities
            </router-link>
            <router-link 
              to="/challenges" 
              class="text-gray-700 hover:text-primary-600 px-3 py-2 text-sm font-medium transition-colors"
              :class="{ 'text-primary-600 border-b-2 border-primary-600': $route.path === '/challenges' }"
            >
              Challenges
            </router-link>
            <router-link 
              to="/leaderboards" 
              class="text-gray-700 hover:text-primary-600 px-3 py-2 text-sm font-medium transition-colors"
              :class="{ 'text-primary-600 border-b-2 border-primary-600': $route.path === '/leaderboards' }"
            >
              Leaderboards
            </router-link>
            <router-link 
              to="/badges" 
              class="text-gray-700 hover:text-primary-600 px-3 py-2 text-sm font-medium transition-colors"
              :class="{ 'text-primary-600 border-b-2 border-primary-600': $route.path === '/badges' }"
            >
              Badges
            </router-link>
            <router-link 
              to="/social" 
              class="text-gray-700 hover:text-primary-600 px-3 py-2 text-sm font-medium transition-colors"
              :class="{ 'text-primary-600 border-b-2 border-primary-600': $route.path === '/social' }"
            >
              Social
            </router-link>
            <router-link 
              v-if="isAdmin"
              to="/enterprise" 
              class="text-gray-700 hover:text-primary-600 px-3 py-2 text-sm font-medium transition-colors"
              :class="{ 'text-primary-600 border-b-2 border-primary-600': $route.path === '/enterprise' }"
            >
              Enterprise
            </router-link>
          </div>
          
          <div class="flex items-center space-x-4">
            <!-- Mobile menu button -->
            <button 
              @click="mobileMenuOpen = !mobileMenuOpen"
              class="md:hidden p-2 rounded-md text-gray-600 hover:text-gray-900 hover:bg-gray-100"
            >
              <svg v-if="!mobileMenuOpen" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
              </svg>
              <svg v-else class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
            
            <!-- Desktop logout button -->
            <button @click="logout" class="hidden md:block text-gray-700 hover:text-primary-600 text-sm font-medium">
              Sign Out
            </button>
            <div class="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
              <span class="text-primary-600 text-sm font-medium">{{ userInitial }}</span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Mobile Navigation -->
      <div v-show="mobileMenuOpen" class="md:hidden border-t border-gray-200 bg-white">
        <div class="px-4 py-2 space-y-1">
          <router-link 
            :to="isAdmin ? '/admin' : '/dashboard'"
            @click="mobileMenuOpen = false"
            class="block px-3 py-2 text-sm font-medium text-gray-700 hover:text-primary-600 hover:bg-gray-50 rounded-md"
            :class="{ 'text-primary-600 bg-primary-50': ($route.path === '/dashboard' && !isAdmin) || ($route.path === '/admin' && isAdmin) }"
          >
            📊 {{ isAdmin ? 'Admin' : 'Dashboard' }}
          </router-link>
          <router-link 
            to="/activities" 
            @click="mobileMenuOpen = false"
            class="block px-3 py-2 text-sm font-medium text-gray-700 hover:text-primary-600 hover:bg-gray-50 rounded-md"
            :class="{ 'text-primary-600 bg-primary-50': $route.path.startsWith('/activities') }"
          >
            📝 Activities
          </router-link>
          <router-link 
            to="/challenges" 
            @click="mobileMenuOpen = false"
            class="block px-3 py-2 text-sm font-medium text-gray-700 hover:text-primary-600 hover:bg-gray-50 rounded-md"
            :class="{ 'text-primary-600 bg-primary-50': $route.path === '/challenges' }"
          >
            🏆 Challenges
          </router-link>
          <router-link 
            to="/leaderboards" 
            @click="mobileMenuOpen = false"
            class="block px-3 py-2 text-sm font-medium text-gray-700 hover:text-primary-600 hover:bg-gray-50 rounded-md"
            :class="{ 'text-primary-600 bg-primary-50': $route.path === '/leaderboards' }"
          >
            🏅 Leaderboards
          </router-link>
          <router-link 
            to="/badges" 
            @click="mobileMenuOpen = false"
            class="block px-3 py-2 text-sm font-medium text-gray-700 hover:text-primary-600 hover:bg-gray-50 rounded-md"
            :class="{ 'text-primary-600 bg-primary-50': $route.path === '/badges' }"
          >
            🎖️ Badges
          </router-link>
          <router-link 
            to="/social" 
            @click="mobileMenuOpen = false"
            class="block px-3 py-2 text-sm font-medium text-gray-700 hover:text-primary-600 hover:bg-gray-50 rounded-md"
            :class="{ 'text-primary-600 bg-primary-50': $route.path === '/social' }"
          >
            👥 Social
          </router-link>
          <router-link 
            v-if="isAdmin"
            to="/enterprise" 
            @click="mobileMenuOpen = false"
            class="block px-3 py-2 text-sm font-medium text-gray-700 hover:text-primary-600 hover:bg-gray-50 rounded-md"
            :class="{ 'text-primary-600 bg-primary-50': $route.path === '/enterprise' }"
          >
            🏢 Enterprise
          </router-link>
          <!-- Mobile logout button -->
          <button 
            @click="logout" 
            class="block w-full text-left px-3 py-2 text-sm font-medium text-gray-700 hover:text-red-600 hover:bg-red-50 rounded-md border-t border-gray-200 mt-2 pt-3"
          >
            🚪 Sign Out
          </button>
        </div>
      </div>
    </nav>

    <!-- Main Content -->
    <main class="flex-1">
      <router-view />
    </main>
    
    <!-- Toast Notifications -->
    <div v-if="notifications.length" class="fixed bottom-4 right-4 space-y-2 z-50">
      <div 
        v-for="notification in notifications" 
        :key="notification.id"
        class="max-w-sm bg-white border border-gray-200 rounded-lg shadow-lg p-4 transform transition-all duration-300"
        :class="{
          'border-green-200 bg-green-50': notification.type === 'success',
          'border-red-200 bg-red-50': notification.type === 'error',
          'border-blue-200 bg-blue-50': notification.type === 'info'
        }"
      >
        <div class="flex items-start space-x-3">
          <div class="flex-shrink-0">
            <span v-if="notification.type === 'success'" class="text-green-500">✅</span>
            <span v-else-if="notification.type === 'error'" class="text-red-500">❌</span>
            <span v-else class="text-blue-500">ℹ️</span>
          </div>
          <div class="flex-1">
            <p class="text-sm font-medium" :class="{
              'text-green-800': notification.type === 'success',
              'text-red-800': notification.type === 'error',
              'text-blue-800': notification.type === 'info'
            }">
              {{ notification.message }}
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useNotificationStore } from '@/stores/notifications'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const notificationStore = useNotificationStore()

const mobileMenuOpen = ref(false)

const isAuthPage = computed(() => {
  return ['/login', '/register'].includes(route.path)
})

const userInitial = computed(() => {
  return authStore.user?.email?.[0]?.toUpperCase() || 'U'
})

const isAdmin = computed(() => {
  return authStore.user?.is_staff || authStore.user?.is_superuser
})

const notifications = computed(() => notificationStore.notifications)

const logout = async () => {
  await authStore.logout()
  router.push('/login')
}

onMounted(() => {
  // Check if user is authenticated
  if (!authStore.isAuthenticated && !isAuthPage.value) {
    router.push('/login')
  }
})
</script>