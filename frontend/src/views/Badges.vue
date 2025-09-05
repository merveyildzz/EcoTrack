<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900">Achievements & Badges</h1>
      <p class="mt-2 text-gray-600">Track your progress and earn rewards for your eco-friendly actions</p>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="flex items-center justify-center py-12">
      <div class="w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full animate-spin"></div>
      <span class="ml-3 text-gray-600">Loading achievements...</span>
    </div>

    <div v-else>
      <!-- Progress Summary -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div class="card text-center">
          <div class="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center mx-auto mb-3">
            <span class="text-yellow-600 text-xl">🏆</span>
          </div>
          <h3 class="font-semibold text-gray-900">{{ earnedBadges.length }}</h3>
          <p class="text-sm text-gray-600">Badges Earned</p>
        </div>
        <div class="card text-center">
          <div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-3">
            <span class="text-blue-600 text-xl">⭐</span>
          </div>
          <h3 class="font-semibold text-gray-900">{{ totalPoints }}</h3>
          <p class="text-sm text-gray-600">Total Points</p>
        </div>
        <div class="card text-center">
          <div class="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mx-auto mb-3">
            <span class="text-green-600 text-xl">📈</span>
          </div>
          <h3 class="font-semibold text-gray-900">{{ completionPercentage }}%</h3>
          <p class="text-sm text-gray-600">Completion</p>
        </div>
        <div class="card text-center">
          <div class="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mx-auto mb-3">
            <span class="text-purple-600 text-xl">🔥</span>
          </div>
          <h3 class="font-semibold text-gray-900">{{ recentBadges }}</h3>
          <p class="text-sm text-gray-600">This Month</p>
        </div>
      </div>

      <!-- Filter Tabs -->
      <div class="flex flex-wrap gap-3 mb-8">
        <button
          v-for="filter in badgeFilters"
          :key="filter.value"
          @click="selectedFilter = filter.value"
          class="px-4 py-2 text-sm rounded-full transition-colors"
          :class="selectedFilter === filter.value
            ? 'bg-primary-100 text-primary-700 font-medium'
            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'"
        >
          {{ filter.icon }} {{ filter.label }}
        </button>
      </div>

      <!-- Badges Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        <div
          v-for="badge in filteredBadges"
          :key="badge.id"
          class="card transition-all duration-200 hover:shadow-md"
          :class="getBadgeCardClass(badge)"
        >
          <!-- Badge Header -->
          <div class="text-center mb-4">
            <div 
              class="w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-3"
              :class="getBadgeIconClass(badge)"
            >
              <span class="text-2xl">{{ getBadgeIcon(badge) }}</span>
            </div>
            <h3 class="font-semibold text-gray-900 mb-1">{{ badge.name }}</h3>
            <div class="flex items-center justify-center space-x-1">
              <span 
                class="px-2 py-1 text-xs font-medium rounded-full"
                :class="getRarityClass(badge.rarity)"
              >
                {{ badge.rarity }}
              </span>
              <span class="text-sm text-gray-500">{{ badge.points }}pts</span>
            </div>
          </div>

          <!-- Badge Description -->
          <p class="text-sm text-gray-600 text-center mb-4">{{ badge.description }}</p>

          <!-- Badge Status -->
          <div v-if="isEarned(badge)" class="text-center">
            <div class="flex items-center justify-center space-x-2 text-green-600 mb-2">
              <span class="text-sm">✓</span>
              <span class="text-sm font-medium">Earned</span>
            </div>
            <p class="text-xs text-gray-500">
              {{ getEarnedDate(badge) }}
            </p>
          </div>
          
          <div v-else class="text-center">
            <div class="mb-2">
              <p class="text-xs text-gray-500 mb-1">Progress</p>
              <div class="w-full bg-gray-200 rounded-full h-2 mb-1">
                <div 
                  class="bg-primary-600 h-2 rounded-full transition-all duration-500"
                  :style="{ width: `${getBadgeProgress(badge)}%` }"
                ></div>
              </div>
              <p class="text-xs text-gray-600">{{ getBadgeProgressText(badge) }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-if="filteredBadges.length === 0" class="text-center py-12">
        <span class="text-4xl mb-4 block">🏆</span>
        <h3 class="text-lg font-medium text-gray-900 mb-2">No badges found</h3>
        <p class="text-gray-600">Try changing your filter or start completing activities to earn badges!</p>
      </div>

      <!-- Badge Categories Info -->
      <div class="mt-12 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div class="card text-center bg-blue-50 border-blue-200">
          <span class="text-3xl mb-2 block">📊</span>
          <h3 class="font-semibold text-gray-900 mb-1">Activity Badges</h3>
          <p class="text-sm text-gray-600">For logging eco-friendly activities</p>
        </div>
        <div class="card text-center bg-green-50 border-green-200">
          <span class="text-3xl mb-2 block">🌱</span>
          <h3 class="font-semibold text-gray-900 mb-1">Impact Badges</h3>
          <p class="text-sm text-gray-600">For reducing CO₂ emissions</p>
        </div>
        <div class="card text-center bg-orange-50 border-orange-200">
          <span class="text-3xl mb-2 block">🔥</span>
          <h3 class="font-semibold text-gray-900 mb-1">Streak Badges</h3>
          <p class="text-sm text-gray-600">For maintaining daily habits</p>
        </div>
        <div class="card text-center bg-purple-50 border-purple-200">
          <span class="text-3xl mb-2 block">🎯</span>
          <h3 class="font-semibold text-gray-900 mb-1">Challenge Badges</h3>
          <p class="text-sm text-gray-600">For completing challenges</p>
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

const isLoading = ref(true)
const allBadges = ref([])
const earnedBadges = ref([])
const selectedFilter = ref('all')

const badgeFilters = [
  { value: 'all', label: 'All Badges', icon: '🏆' },
  { value: 'earned', label: 'Earned', icon: '✅' },
  { value: 'available', label: 'Available', icon: '🎯' },
  { value: 'common', label: 'Common', icon: '⚪' },
  { value: 'rare', label: 'Rare', icon: '🔵' },
  { value: 'epic', label: 'Epic', icon: '🟣' },
  { value: 'legendary', label: 'Legendary', icon: '🟡' }
]

const filteredBadges = computed(() => {
  let filtered = allBadges.value
  
  if (selectedFilter.value === 'earned') {
    const earnedIds = earnedBadges.value.map(eb => eb.badge.id)
    filtered = allBadges.value.filter(badge => earnedIds.includes(badge.id))
  } else if (selectedFilter.value === 'available') {
    const earnedIds = earnedBadges.value.map(eb => eb.badge.id)
    filtered = allBadges.value.filter(badge => !earnedIds.includes(badge.id))
  } else if (['common', 'uncommon', 'rare', 'epic', 'legendary'].includes(selectedFilter.value)) {
    filtered = allBadges.value.filter(badge => badge.rarity === selectedFilter.value)
  }
  
  return filtered
})

const totalPoints = computed(() => {
  return earnedBadges.value.reduce((sum, eb) => sum + (eb.badge.points || 0), 0)
})

const completionPercentage = computed(() => {
  if (allBadges.value.length === 0) return 0
  return Math.round((earnedBadges.value.length / allBadges.value.length) * 100)
})

const recentBadges = computed(() => {
  const oneMonthAgo = new Date()
  oneMonthAgo.setMonth(oneMonthAgo.getMonth() - 1)
  
  return earnedBadges.value.filter(eb => 
    new Date(eb.earned_at) > oneMonthAgo
  ).length
})

const loadBadges = async () => {
  try {
    const [badgesData, userBadgesData] = await Promise.all([
      socialApi.getBadges(),
      socialApi.getUserBadges()
    ])
    
    allBadges.value = badgesData.results || badgesData
    earnedBadges.value = userBadgesData.results || userBadgesData
  } catch (error) {
    console.error('Error loading badges:', error)
    notificationStore.error('Failed to load badges')
  }
}

const isEarned = (badge) => {
  return earnedBadges.value.some(eb => eb.badge.id === badge.id)
}

const getEarnedDate = (badge) => {
  const earned = earnedBadges.value.find(eb => eb.badge.id === badge.id)
  if (earned) {
    return new Date(earned.earned_at).toLocaleDateString()
  }
  return ''
}

const getBadgeIcon = (badge) => {
  if (badge.icon && badge.icon.length > 0) {
    return badge.icon
  }
  
  const typeIcons = {
    'activity_count': '📊',
    'co2_reduction': '🌱', 
    'streak_days': '🔥',
    'challenge_completion': '🎯',
    'social_engagement': '👥'
  }
  return typeIcons[badge.criteria_type] || '🏆'
}

const getBadgeIconClass = (badge) => {
  if (isEarned(badge)) {
    return getRarityIconClass(badge.rarity)
  }
  return 'bg-gray-100'
}

const getRarityIconClass = (rarity) => {
  const classes = {
    'common': 'bg-gray-100',
    'uncommon': 'bg-green-100',
    'rare': 'bg-blue-100', 
    'epic': 'bg-purple-100',
    'legendary': 'bg-yellow-100'
  }
  return classes[rarity] || 'bg-gray-100'
}

const getBadgeCardClass = (badge) => {
  if (isEarned(badge)) {
    const rarityClasses = {
      'common': 'border-gray-300 bg-gray-50',
      'uncommon': 'border-green-300 bg-green-50',
      'rare': 'border-blue-300 bg-blue-50',
      'epic': 'border-purple-300 bg-purple-50', 
      'legendary': 'border-yellow-300 bg-yellow-50'
    }
    return rarityClasses[badge.rarity] || ''
  }
  return 'opacity-75'
}

const getRarityClass = (rarity) => {
  const classes = {
    'common': 'bg-gray-100 text-gray-800',
    'uncommon': 'bg-green-100 text-green-800',
    'rare': 'bg-blue-100 text-blue-800',
    'epic': 'bg-purple-100 text-purple-800',
    'legendary': 'bg-yellow-100 text-yellow-800'
  }
  return classes[rarity] || 'bg-gray-100 text-gray-800'
}

const getBadgeProgress = (badge) => {
  // This would need to be calculated based on user's actual progress
  // For now, return a mock progress
  const earned = earnedBadges.value.find(eb => eb.badge.id === badge.id)
  if (earned) return 100
  
  // Mock progress calculation - in real app this would come from API
  return Math.floor(Math.random() * 80) // Random progress between 0-80%
}

const getBadgeProgressText = (badge) => {
  const progress = getBadgeProgress(badge)
  const target = badge.criteria_value
  const current = Math.floor((progress / 100) * target)
  
  if (badge.criteria_type === 'activity_count') {
    return `${current}/${target} activities`
  } else if (badge.criteria_type === 'co2_reduction') {
    return `${current.toFixed(1)}/${target}kg CO₂ saved`
  } else if (badge.criteria_type === 'streak_days') {
    return `${current}/${target} days streak`
  } else if (badge.criteria_type === 'challenge_completion') {
    return `${current}/${target} challenges`
  }
  
  return `${current}/${target}`
}

onMounted(async () => {
  await loadBadges()
  isLoading.value = false
})
</script>