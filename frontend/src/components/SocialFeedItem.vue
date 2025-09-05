<template>
  <div class="card hover:shadow-md transition-shadow">
    <div class="flex items-start space-x-3">
      <!-- User Avatar -->
      <div class="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center flex-shrink-0">
        <span class="text-primary-600 text-sm font-medium">
          {{ getUserInitial(item.user) }}
        </span>
      </div>

      <div class="flex-1 min-w-0">
        <!-- Feed Item Header -->
        <div class="flex items-center space-x-2 mb-2">
          <span class="font-medium text-gray-900">{{ getUserDisplayName(item.user) }}</span>
          <span class="text-gray-500">•</span>
          <span class="text-sm text-gray-500">{{ formatTimeAgo(item.created_at) }}</span>
          <span v-if="item.is_featured" class="px-2 py-1 bg-yellow-100 text-yellow-800 text-xs rounded-full">
            ⭐ Featured
          </span>
        </div>

        <!-- Activity Content -->
        <div class="flex items-start space-x-3">
          <div 
            class="w-12 h-12 rounded-lg flex items-center justify-center flex-shrink-0"
            :class="getActivityIconClass(item.activity_type)"
          >
            <span class="text-xl">{{ getActivityIcon(item.activity_type) }}</span>
          </div>

          <div class="flex-1">
            <h3 class="font-medium text-gray-900 mb-1">{{ item.title }}</h3>
            <p class="text-gray-600 text-sm mb-3">{{ item.description }}</p>

            <!-- Metadata -->
            <div v-if="item.metadata && Object.keys(item.metadata).length > 0" 
                 class="flex flex-wrap gap-4 text-sm text-gray-600">
              <span v-if="item.metadata.co2_saved" class="flex items-center">
                🌱 {{ item.metadata.co2_saved }}kg CO₂ saved
              </span>
              <span v-if="item.metadata.points" class="flex items-center">
                ⭐ {{ item.metadata.points }} points
              </span>
              <span v-if="item.metadata.rank" class="flex items-center">
                🏆 Rank #{{ item.metadata.rank }}
              </span>
              <span v-if="item.metadata.streak" class="flex items-center">
                🔥 {{ item.metadata.streak }} day streak
              </span>
            </div>
          </div>
        </div>

        <!-- Engagement -->
        <div class="flex items-center space-x-4 mt-4 pt-3 border-t border-gray-100">
          <button 
            @click="toggleLike"
            class="flex items-center space-x-1 text-sm text-gray-500 hover:text-primary-600 transition-colors"
            :class="item.isLiked ? 'text-primary-600' : ''"
          >
            <span>{{ item.isLiked ? '❤️' : '🤍' }}</span>
            <span>{{ item.likes || 0 }}</span>
          </button>
          <button 
            @click="toggleClap"
            class="flex items-center space-x-1 text-sm text-gray-500 hover:text-primary-600 transition-colors"
            :class="item.hasClapped ? 'text-primary-600' : ''"
          >
            <span>👏</span>
            <span>{{ item.claps || 0 }}</span>
          </button>
          <button 
            @click="$emit('share', item)"
            class="text-sm text-gray-500 hover:text-primary-600 transition-colors"
          >
            Share
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  item: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['like', 'clap', 'share'])

const toggleLike = () => {
  emit('like', props.item)
}

const toggleClap = () => {
  emit('clap', props.item)
}

const getActivityIcon = (activityType) => {
  const icons = {
    'badge_earned': '🏆',
    'challenge_completed': '🎯',
    'leaderboard_rank': '📈',
    'milestone_reached': '🎉',
    'streak_achievement': '🔥'
  }
  return icons[activityType] || '🌟'
}

const getActivityIconClass = (activityType) => {
  const classes = {
    'badge_earned': 'bg-yellow-100',
    'challenge_completed': 'bg-green-100',
    'leaderboard_rank': 'bg-blue-100',
    'milestone_reached': 'bg-purple-100',
    'streak_achievement': 'bg-orange-100'
  }
  return classes[activityType] || 'bg-gray-100'
}

const getUserInitial = (user) => {
  if (user?.first_name) {
    return user.first_name.charAt(0).toUpperCase()
  }
  return user?.email?.charAt(0).toUpperCase() || '?'
}

const getUserDisplayName = (user) => {
  if (user?.first_name && user?.last_name) {
    return `${user.first_name} ${user.last_name}`
  } else if (user?.first_name) {
    return user.first_name
  }
  return user?.email || 'Anonymous'
}

const formatTimeAgo = (dateString) => {
  const date = new Date(dateString)
  const now = new Date()
  const diffInHours = Math.floor((now - date) / (1000 * 60 * 60))
  
  if (diffInHours < 1) return 'Just now'
  if (diffInHours < 24) return `${diffInHours}h ago`
  
  const diffInDays = Math.floor(diffInHours / 24)
  if (diffInDays < 7) return `${diffInDays}d ago`
  
  const diffInWeeks = Math.floor(diffInDays / 7)
  return `${diffInWeeks}w ago`
}
</script>