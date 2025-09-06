<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <!-- Community Navigation -->
    <div class="mb-6">
      <nav class="flex space-x-1 bg-gray-100 rounded-lg p-1" aria-label="Community sections">
        <router-link
          to="/leaderboards"
          class="flex-1 text-center px-4 py-2 text-sm font-medium rounded-md transition-colors"
          :class="$route.path === '/leaderboards' 
            ? 'bg-white text-gray-900 shadow-sm' 
            : 'text-gray-600 hover:text-gray-900'"
        >
          🏅 Leaderboards
        </router-link>
        <router-link
          to="/challenges"
          class="flex-1 text-center px-4 py-2 text-sm font-medium rounded-md transition-colors"
          :class="$route.path === '/challenges' 
            ? 'bg-white text-gray-900 shadow-sm' 
            : 'text-gray-600 hover:text-gray-900'"
        >
          🏆 Challenges
        </router-link>
        <router-link
          to="/badges"
          class="flex-1 text-center px-4 py-2 text-sm font-medium rounded-md transition-colors"
          :class="$route.path === '/badges' 
            ? 'bg-white text-gray-900 shadow-sm' 
            : 'text-gray-600 hover:text-gray-900'"
        >
          🎖️ Badges
        </router-link>
        <router-link
          to="/social"
          class="flex-1 text-center px-4 py-2 text-sm font-medium rounded-md transition-colors"
          :class="$route.path === '/social' 
            ? 'bg-white text-gray-900 shadow-sm' 
            : 'text-gray-600 hover:text-gray-900'"
        >
          👥 Social
        </router-link>
      </nav>
    </div>

    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900">Leaderboards</h1>
      <p class="mt-2 text-gray-600">See how you stack up against other eco-warriors</p>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="flex items-center justify-center py-12">
      <div class="w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full animate-spin"></div>
      <span class="ml-3 text-gray-600">Loading leaderboards...</span>
    </div>

    <!-- Leaderboard Filters -->
    <div v-else class="flex flex-wrap gap-3 mb-8">
      <button
        v-for="board in availableLeaderboards"
        :key="board.id"
        @click="selectedLeaderboard = board"
        class="px-4 py-2 text-sm rounded-full transition-colors"
        :class="selectedLeaderboard?.id === board.id
          ? 'bg-primary-100 text-primary-700 font-medium'
          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'"
      >
        {{ getLeaderboardIcon(board.metric_type) }} {{ board.name }}
      </button>
    </div>

    <!-- Current User Rank Card -->
    <div v-if="userPosition" class="card mb-8 bg-gradient-to-r from-primary-50 to-green-50 border-primary-200">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-4">
          <div class="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center">
            <span class="text-2xl">{{ getRankEmoji(userPosition.rank) }}</span>
          </div>
          <div>
            <h3 class="text-lg font-semibold text-gray-900">Your Rank</h3>
            <p class="text-sm text-gray-600">{{ selectedLeaderboard?.name }}</p>
            <div class="flex items-center space-x-2 mt-1">
              <span class="text-2xl font-bold text-primary-600">#{{ userPosition.rank }}</span>
              <span v-if="userPosition.rank_change !== 0" class="text-sm"
                :class="userPosition.rank_change > 0 ? 'text-green-600' : 'text-red-600'">
                {{ userPosition.rank_change > 0 ? '↗' : '↘' }} {{ Math.abs(userPosition.rank_change) }}
              </span>
            </div>
          </div>
        </div>
        <div class="text-right">
          <p class="text-sm text-gray-600">Score</p>
          <p class="text-xl font-bold text-gray-900">{{ formatScore(userPosition.score, selectedLeaderboard?.metric_type) }}</p>
        </div>
      </div>
    </div>

    <!-- Leaderboard Table -->
    <div v-if="selectedLeaderboard" class="card">
      <div class="flex items-center justify-between mb-6">
        <div>
          <h2 class="text-xl font-semibold text-gray-900">{{ selectedLeaderboard.name }}</h2>
          <p class="text-sm text-gray-600">{{ selectedLeaderboard.description }}</p>
        </div>
        <div class="flex items-center space-x-2 text-sm text-gray-500">
          <span>⏰</span>
          <span>{{ formatTimePeriod(selectedLeaderboard.time_period) }}</span>
        </div>
      </div>

      <div class="overflow-x-auto">
        <table class="min-w-full">
          <thead>
            <tr class="border-b border-gray-200">
              <th class="py-3 px-4 text-left text-sm font-medium text-gray-500">Rank</th>
              <th class="py-3 px-4 text-left text-sm font-medium text-gray-500">User</th>
              <th class="py-3 px-4 text-left text-sm font-medium text-gray-500">Score</th>
              <th class="py-3 px-4 text-left text-sm font-medium text-gray-500">Change</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="entry in leaderboardEntries"
              :key="entry.id"
              class="border-b border-gray-100 hover:bg-gray-50"
              :class="entry.user.id === currentUserId ? 'bg-primary-50 border-primary-200' : ''"
            >
              <td class="py-4 px-4">
                <div class="flex items-center space-x-2">
                  <span class="text-lg">{{ getRankEmoji(entry.rank) }}</span>
                  <span class="font-medium text-gray-900">#{{ entry.rank }}</span>
                </div>
              </td>
              <td class="py-4 px-4">
                <div class="flex items-center space-x-3">
                  <div class="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
                    <span class="text-primary-600 text-sm font-medium">
                      {{ getUserInitial(entry.user) }}
                    </span>
                  </div>
                  <div>
                    <p class="font-medium text-gray-900">
                      {{ getUserDisplayName(entry.user) }}
                      <span v-if="entry.user.id === currentUserId" class="text-primary-600">(You)</span>
                    </p>
                  </div>
                </div>
              </td>
              <td class="py-4 px-4">
                <span class="font-semibold text-gray-900">
                  {{ formatScore(entry.score, selectedLeaderboard.metric_type) }}
                </span>
              </td>
              <td class="py-4 px-4">
                <span v-if="entry.rank_change === 0" class="text-gray-500">-</span>
                <span v-else-if="entry.rank_change > 0" class="text-green-600 flex items-center">
                  <span class="mr-1">↗</span> {{ entry.rank_change }}
                </span>
                <span v-else class="text-red-600 flex items-center">
                  <span class="mr-1">↘</span> {{ Math.abs(entry.rank_change) }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="leaderboardEntries.length === 0" class="text-center py-8">
        <span class="text-4xl mb-2 block">📊</span>
        <p class="text-gray-600">No entries yet</p>
        <p class="text-sm text-gray-500">Be the first to appear on this leaderboard!</p>
      </div>
    </div>

    <!-- Leaderboard Info -->
    <div class="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
      <div class="card text-center">
        <span class="text-3xl mb-2 block">🏆</span>
        <h3 class="font-semibold text-gray-900 mb-1">Top Performers</h3>
        <p class="text-sm text-gray-600">Rankings update every hour</p>
      </div>
      <div class="card text-center">
        <span class="text-3xl mb-2 block">📈</span>
        <h3 class="font-semibold text-gray-900 mb-1">Track Progress</h3>
        <p class="text-sm text-gray-600">See your ranking trends over time</p>
      </div>
      <div class="card text-center">
        <span class="text-3xl mb-2 block">🎯</span>
        <h3 class="font-semibold text-gray-900 mb-1">Compete Fairly</h3>
        <p class="text-sm text-gray-600">Multiple categories for different goals</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useNotificationStore } from '@/stores/notifications'
import socialApi from '@/services/social'

const authStore = useAuthStore()
const notificationStore = useNotificationStore()

const isLoading = ref(true)
const availableLeaderboards = ref([])
const selectedLeaderboard = ref(null)
const leaderboardEntries = ref([])
const userPosition = ref(null)

const currentUserId = computed(() => authStore.user?.id)

// Watch for leaderboard selection changes
watch(selectedLeaderboard, async (newBoard) => {
  if (newBoard) {
    await loadLeaderboardData(newBoard.id)
  }
})

const loadLeaderboards = async () => {
  try {
    const data = await socialApi.getLeaderboards()
    availableLeaderboards.value = data.results || data
    
    // Select first leaderboard by default
    if (availableLeaderboards.value.length > 0) {
      selectedLeaderboard.value = availableLeaderboards.value[0]
    }
  } catch (error) {
    console.error('Error loading leaderboards:', error)
    notificationStore.error('Failed to load leaderboards')
  }
}

const loadLeaderboardData = async (leaderboardId) => {
  try {
    // Load leaderboard entries
    const leaderboardData = await socialApi.getLeaderboard(leaderboardId)
    leaderboardEntries.value = leaderboardData.entries || []
    
    // Load user position
    try {
      userPosition.value = await socialApi.getUserLeaderboardPosition(leaderboardId)
    } catch (error) {
      // User might not be on this leaderboard yet
      userPosition.value = null
    }
  } catch (error) {
    console.error('Error loading leaderboard data:', error)
    notificationStore.error('Failed to load leaderboard data')
  }
}

const getLeaderboardIcon = (metricType) => {
  const icons = {
    'total_co2_saved': '🌱',
    'activity_count': '📊',
    'streak_days': '🔥',
    'badge_points': '🏆',
    'challenge_completions': '🎯'
  }
  return icons[metricType] || '📈'
}

const getRankEmoji = (rank) => {
  if (rank === 1) return '🥇'
  if (rank === 2) return '🥈' 
  if (rank === 3) return '🥉'
  if (rank <= 10) return '🏅'
  return '👤'
}

const formatScore = (score, metricType) => {
  if (metricType === 'total_co2_saved') {
    return `${score.toFixed(1)}kg CO₂`
  } else if (metricType === 'streak_days') {
    return `${score} days`
  } else if (metricType === 'activity_count') {
    return `${score} activities`
  } else if (metricType === 'badge_points') {
    return `${score} points`
  } else if (metricType === 'challenge_completions') {
    return `${score} challenges`
  }
  return score.toString()
}

const formatTimePeriod = (period) => {
  const periods = {
    'all_time': 'All Time',
    'yearly': 'This Year',
    'monthly': 'This Month', 
    'weekly': 'This Week'
  }
  return periods[period] || period
}

const getUserInitial = (user) => {
  if (user.first_name) {
    return user.first_name.charAt(0).toUpperCase()
  }
  return user.email.charAt(0).toUpperCase()
}

const getUserDisplayName = (user) => {
  if (user.first_name && user.last_name) {
    return `${user.first_name} ${user.last_name}`
  } else if (user.first_name) {
    return user.first_name
  }
  return user.email
}

onMounted(async () => {
  await loadLeaderboards()
  isLoading.value = false
})
</script>