<template>
  <div class="card">
    <div class="flex items-center justify-between mb-6">
      <div>
        <h2 class="text-xl font-semibold text-gray-900">{{ leaderboard.name }}</h2>
        <p class="text-sm text-gray-600">{{ leaderboard.description }}</p>
      </div>
      <div class="flex items-center space-x-2 text-sm text-gray-500">
        <span>⏰</span>
        <span>{{ formatTimePeriod(leaderboard.time_period) }}</span>
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
            v-for="entry in entries"
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
                {{ formatScore(entry.score, leaderboard.metric_type) }}
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

    <div v-if="entries.length === 0" class="text-center py-8">
      <span class="text-4xl mb-2 block">📊</span>
      <p class="text-gray-600">No entries yet</p>
      <p class="text-sm text-gray-500">Be the first to appear on this leaderboard!</p>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  leaderboard: {
    type: Object,
    required: true
  },
  entries: {
    type: Array,
    default: () => []
  },
  currentUserId: {
    type: String,
    default: null
  }
})

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
</script>