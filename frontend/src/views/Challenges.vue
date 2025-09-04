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
          <div v-for="(leader, index) in topUsers" :key="leader.id" class="text-center">
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
            <h3 class="font-semibold text-gray-900">{{ leader.name }}</h3>
            <p class="text-sm text-gray-600">{{ leader.co2Saved }}kg CO₂ saved</p>
            <p class="text-xs text-gray-500">{{ leader.country }}</p>
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
import { ref, computed } from 'vue'
import { useNotificationStore } from '@/stores/notifications'

const notificationStore = useNotificationStore()

const selectedCategory = ref('all')

const challengeCategories = [
  { value: 'all', label: 'All Challenges', icon: '🌍' },
  { value: 'transport', label: 'Transport', icon: '🚗' },
  { value: 'energy', label: 'Energy', icon: '⚡' },
  { value: 'food', label: 'Food', icon: '🍽️' },
  { value: 'waste', label: 'Waste', icon: '♻️' }
]

// Mock data - in real app this would come from API
const activeChallenges = ref([
  {
    id: 1,
    title: 'Car-Free Week',
    description: 'Avoid using personal vehicles for a full week',
    icon: '🚲',
    participants: 1247,
    progress: 65,
    daysLeft: 3,
    currentValue: 4.5,
    targetValue: 7,
    unit: 'days'
  }
])

const availableChallenges = [
  {
    id: 2,
    title: 'Energy Saver',
    description: 'Reduce home energy consumption by 20% this month',
    icon: '💡',
    category: 'energy',
    participants: 892,
    difficulty: 'medium',
    targetValue: 20,
    unit: '% reduction',
    duration: 30,
    reward: '50 points'
  },
  {
    id: 3,
    title: 'Plant-Based Week',
    description: 'Eat only plant-based meals for 7 consecutive days',
    icon: '🌱',
    category: 'food',
    participants: 2156,
    difficulty: 'easy',
    targetValue: 7,
    unit: 'days',
    duration: 7,
    reward: '30 points'
  },
  {
    id: 4,
    title: 'Zero Waste Champion',
    description: 'Produce no single-use plastic waste for 2 weeks',
    icon: '🗑️',
    category: 'waste',
    participants: 543,
    difficulty: 'hard',
    targetValue: 14,
    unit: 'days',
    duration: 14,
    reward: '100 points'
  },
  {
    id: 5,
    title: 'Public Transport Hero',
    description: 'Use only public transport or walk/bike for all trips',
    icon: '🚌',
    category: 'transport',
    participants: 1834,
    difficulty: 'medium',
    targetValue: 21,
    unit: 'days',
    duration: 21,
    reward: '75 points'
  },
  {
    id: 6,
    title: 'Solar Power Month',
    description: 'Use renewable energy sources for 80% of consumption',
    icon: '☀️',
    category: 'energy',
    participants: 421,
    difficulty: 'hard',
    targetValue: 80,
    unit: '% renewable',
    duration: 30,
    reward: '150 points'
  }
]

const topUsers = [
  { id: 1, name: 'Alex Green', co2Saved: 1250, country: '🇺🇸 USA' },
  { id: 2, name: 'Maria Silva', co2Saved: 1180, country: '🇧🇷 Brazil' },
  { id: 3, name: 'Chen Wei', co2Saved: 1156, country: '🇨🇳 China' }
]

const filteredChallenges = computed(() => {
  if (selectedCategory.value === 'all') {
    return availableChallenges
  }
  return availableChallenges.filter(challenge => challenge.category === selectedCategory.value)
})

const joinChallenge = async (challenge) => {
  try {
    // In real app, this would call the API
    notificationStore.success(`Joined "${challenge.title}" challenge! Good luck! 🎯`)
    
    // Move challenge to active challenges
    activeChallenges.value.push({
      ...challenge,
      progress: 0,
      daysLeft: challenge.duration,
      currentValue: 0
    })
    
    // Remove from available challenges
    const index = availableChallenges.findIndex(c => c.id === challenge.id)
    if (index > -1) {
      availableChallenges.splice(index, 1)
    }
  } catch (error) {
    notificationStore.error('Failed to join challenge. Please try again.')
  }
}
</script>