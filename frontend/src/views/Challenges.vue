<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900">Challenges</h1>
      <p class="mt-2 text-gray-600">Join challenges to reduce your carbon footprint with others</p>
    </div>

    <!-- Challenge Categories -->
    <div class="flex flex-wrap gap-3 mb-8">
      <button
        v-for="category in challengeCategories"
        :key="category.value"
        @click="selectedCategory = category.value"
        class="px-4 py-2 text-sm rounded-full transition-colors"
        :class="selectedCategory === category.value
          ? 'bg-primary-100 text-primary-700 font-medium'
          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'"
      >
        {{ category.icon }} {{ category.label }}
      </button>
    </div>

    <!-- Active Challenges -->
    <div class="mb-8">
      <h2 class="text-xl font-semibold text-gray-900 mb-4">My Active Challenges</h2>
      
      <div v-if="activeChallenges.length === 0" class="card text-center py-8">
        <span class="text-4xl mb-2 block">🏆</span>
        <p class="text-gray-600 mb-4">You haven't joined any challenges yet</p>
        <p class="text-sm text-gray-500">Join a challenge below to start making an impact!</p>
      </div>
      
      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div
          v-for="challenge in activeChallenges"
          :key="challenge.id"
          class="card border-l-4 border-l-primary-500"
        >
          <div class="flex items-start justify-between mb-4">
            <div class="flex items-center space-x-3">
              <div class="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
                <span class="text-primary-700">{{ challenge.icon }}</span>
              </div>
              <div>
                <h3 class="font-semibold text-gray-900">{{ challenge.title }}</h3>
                <p class="text-sm text-gray-600">{{ challenge.participants }} participants</p>
              </div>
            </div>
            <span class="px-2 py-1 bg-green-100 text-green-800 text-xs font-medium rounded-full">
              Active
            </span>
          </div>
          
          <p class="text-sm text-gray-700 mb-4">{{ challenge.description }}</p>
          
          <!-- Progress Bar -->
          <div class="mb-4">
            <div class="flex justify-between text-sm mb-1">
              <span class="text-gray-600">Progress</span>
              <span class="text-primary-600 font-medium">{{ challenge.progress }}%</span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-2">
              <div 
                class="bg-primary-600 h-2 rounded-full transition-all duration-500"
                :style="{ width: `${challenge.progress}%` }"
              ></div>
            </div>
          </div>
          
          <div class="flex items-center justify-between text-sm text-gray-500">
            <span>{{ challenge.daysLeft }} days left</span>
            <span>{{ challenge.currentValue }}/{{ challenge.targetValue }} {{ challenge.unit }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Available Challenges -->
    <div>
      <h2 class="text-xl font-semibold text-gray-900 mb-4">Available Challenges</h2>
      
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div
          v-for="challenge in filteredChallenges"
          :key="challenge.id"
          class="card hover:shadow-md transition-shadow"
        >
          <div class="flex items-start justify-between mb-4">
            <div class="flex items-center space-x-3">
              <div class="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center">
                <span>{{ challenge.icon }}</span>
              </div>
              <div>
                <h3 class="font-semibold text-gray-900">{{ challenge.title }}</h3>
                <p class="text-sm text-gray-600">{{ challenge.participants }} participants</p>
              </div>
            </div>
            <span 
              class="px-2 py-1 text-xs font-medium rounded-full"
              :class="challenge.difficulty === 'easy' 
                ? 'bg-green-100 text-green-800'
                : challenge.difficulty === 'medium'
                ? 'bg-yellow-100 text-yellow-800'
                : 'bg-red-100 text-red-800'"
            >
              {{ challenge.difficulty }}
            </span>
          </div>
          
          <p class="text-sm text-gray-700 mb-4">{{ challenge.description }}</p>
          
          <div class="flex items-center justify-between text-sm text-gray-600 mb-4">
            <span>🎯 {{ challenge.targetValue }} {{ challenge.unit }}</span>
            <span>⏱️ {{ challenge.duration }} days</span>
          </div>
          
          <div class="flex items-center justify-between">
            <div class="text-sm">
              <span class="text-primary-600 font-medium">{{ challenge.reward }}</span>
              <span class="text-gray-500"> reward</span>
            </div>
            <button 
              @click="joinChallenge(challenge)"
              class="btn-primary text-sm px-4 py-2"
            >
              Join Challenge
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Global Leaderboard Preview -->
    <div class="mt-12">
      <div class="card bg-gradient-to-r from-primary-50 to-green-50 border-primary-200">
        <div class="text-center mb-6">
          <h2 class="text-xl font-semibold text-gray-900 mb-2">🌍 Global Leaderboard</h2>
          <p class="text-gray-600">See how you rank among eco-warriors worldwide</p>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div v-for="(leader, index) in topUsers" :key="leader.user.id" class="text-center">
            <div 
              class="w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-3"
              :class="index === 0 
                ? 'bg-yellow-100 text-yellow-600' 
                : index === 1 
                ? 'bg-gray-100 text-gray-600'
                : 'bg-orange-100 text-orange-600'"
            >
              <span class="text-2xl">{{ ['🥇', '🥈', '🥉'][index] }}</span>
            </div>
            <h3 class="font-semibold text-gray-900">{{ leader.user.first_name }} {{ leader.user.last_name }}</h3>
            <p class="text-sm text-gray-600">{{ leader.score }}kg CO₂ saved</p>
            <p class="text-xs text-gray-500">Rank #{{ leader.position }}</p>
          </div>
        </div>
        
        <div class="text-center mt-6">
          <button class="btn-secondary">
            View Full Leaderboard
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useNotificationStore } from '@/stores/notifications'
import socialApi from '@/services/social'

const notificationStore = useNotificationStore()

const selectedCategory = ref('all')

const challengeCategories = [
  { value: 'all', label: 'All Challenges', icon: '🌍' },
  { value: 'transport', label: 'Transport', icon: '🚗' },
  { value: 'energy', label: 'Energy', icon: '⚡' },
  { value: 'food', label: 'Food', icon: '🍽️' },
  { value: 'waste', label: 'Waste', icon: '♻️' }
]

const activeChallenges = ref([])
const availableChallenges = ref([])
const topUsers = ref([])
const isLoading = ref(true)


const filteredChallenges = computed(() => {
  if (selectedCategory.value === 'all') {
    return availableChallenges.value
  }
  return availableChallenges.value.filter(challenge => challenge.category === selectedCategory.value)
})

const joinChallenge = async (challenge) => {
  try {
    await socialApi.joinChallenge(challenge.id)
    notificationStore.success(`Joined "${challenge.title}" challenge! Good luck! 🎯`)
    
    // Refresh challenges data
    await loadChallenges()
  } catch (error) {
    console.error('Error joining challenge:', error)
    notificationStore.error('Failed to join challenge. Please try again.')
  }
}

const loadChallenges = async () => {
  try {
    const [availableChallengesResponse, userChallengesResponse] = await Promise.all([
      socialApi.getChallenges(),
      socialApi.getUserChallenges()
    ])
    
    availableChallenges.value = availableChallengesResponse.results || availableChallengesResponse
    activeChallenges.value = userChallengesResponse.results || userChallengesResponse
  } catch (error) {
    console.error('Error loading challenges:', error)
    notificationStore.error('Failed to load challenges')
  }
}

const loadLeaderboard = async () => {
  try {
    const leaderboards = await socialApi.getLeaderboards()
    if (leaderboards.results && leaderboards.results.length > 0) {
      const globalLeaderboard = leaderboards.results[0]
      const leaderboardDetail = await socialApi.getLeaderboard(globalLeaderboard.id)
      topUsers.value = leaderboardDetail.entries?.slice(0, 3) || []
    }
  } catch (error) {
    console.error('Error loading leaderboard:', error)
  }
}

onMounted(async () => {
  try {
    await Promise.all([
      loadChallenges(),
      loadLeaderboard()
    ])
  } finally {
    isLoading.value = false
  }
})
</script>