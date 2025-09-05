<template>
  <div 
    class="card transition-all duration-200 hover:shadow-md cursor-pointer"
    :class="getBadgeCardClass(badge, earned)"
    @click="$emit('click', badge)"
  >
    <!-- Badge Header -->
    <div class="text-center mb-4">
      <div 
        class="w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-3"
        :class="getBadgeIconClass(badge, earned)"
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
    <div v-if="earned" class="text-center">
      <div class="flex items-center justify-center space-x-2 text-green-600 mb-2">
        <span class="text-sm">✓</span>
        <span class="text-sm font-medium">Earned</span>
      </div>
      <p class="text-xs text-gray-500" v-if="earnedDate">
        {{ earnedDate }}
      </p>
    </div>
    
    <div v-else-if="showProgress" class="text-center">
      <div class="mb-2">
        <p class="text-xs text-gray-500 mb-1">Progress</p>
        <div class="w-full bg-gray-200 rounded-full h-2 mb-1">
          <div 
            class="bg-primary-600 h-2 rounded-full transition-all duration-500"
            :style="{ width: `${progress}%` }"
          ></div>
        </div>
        <p class="text-xs text-gray-600">{{ progressText }}</p>
      </div>
    </div>

    <div v-else class="text-center">
      <p class="text-xs text-gray-500">{{ getCriteriaText(badge) }}</p>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  badge: {
    type: Object,
    required: true
  },
  earned: {
    type: Boolean,
    default: false
  },
  earnedDate: {
    type: String,
    default: null
  },
  progress: {
    type: Number,
    default: 0
  },
  progressText: {
    type: String,
    default: ''
  },
  showProgress: {
    type: Boolean,
    default: false
  }
})

defineEmits(['click'])

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

const getBadgeIconClass = (badge, earned) => {
  if (earned) {
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

const getBadgeCardClass = (badge, earned) => {
  if (earned) {
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

const getCriteriaText = (badge) => {
  const target = badge.criteria_value
  
  if (badge.criteria_type === 'activity_count') {
    return `Log ${target} activities`
  } else if (badge.criteria_type === 'co2_reduction') {
    return `Save ${target}kg CO₂`
  } else if (badge.criteria_type === 'streak_days') {
    return `${target} day streak`
  } else if (badge.criteria_type === 'challenge_completion') {
    return `Complete ${target} challenges`
  }
  
  return `Reach ${target} ${badge.criteria_type}`
}
</script>