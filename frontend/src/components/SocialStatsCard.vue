<template>
  <div class="card">
    <h3 class="text-lg font-semibold text-gray-900 mb-4">{{ title }}</h3>
    <div class="space-y-4">
      <!-- Stats Grid -->
      <div v-if="displayMode === 'grid'" class="grid grid-cols-2 gap-4">
        <div 
          v-for="stat in stats" 
          :key="stat.key"
          class="text-center p-3 bg-gray-50 rounded-lg"
        >
          <div 
            class="w-10 h-10 rounded-lg flex items-center justify-center mx-auto mb-2"
            :class="stat.iconClass"
          >
            <span class="text-lg">{{ stat.icon }}</span>
          </div>
          <p class="text-xl font-bold text-gray-900">{{ formatStatValue(stat.value, stat.type) }}</p>
          <p class="text-sm text-gray-600">{{ stat.label }}</p>
        </div>
      </div>

      <!-- Stats List -->
      <div v-else class="space-y-3">
        <div 
          v-for="stat in stats" 
          :key="stat.key"
          class="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
        >
          <div class="flex items-center space-x-3">
            <div 
              class="w-8 h-8 rounded-lg flex items-center justify-center"
              :class="stat.iconClass"
            >
              <span class="text-sm">{{ stat.icon }}</span>
            </div>
            <span class="text-gray-600">{{ stat.label }}</span>
          </div>
          <span class="font-medium text-gray-900">{{ formatStatValue(stat.value, stat.type) }}</span>
        </div>
      </div>

      <!-- Action Button -->
      <div v-if="actionButton" class="pt-2 border-t border-gray-100">
        <router-link 
          :to="actionButton.route" 
          class="block text-center text-sm text-primary-600 hover:text-primary-700 font-medium"
        >
          {{ actionButton.text }}
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  title: {
    type: String,
    required: true
  },
  stats: {
    type: Array,
    required: true
  },
  displayMode: {
    type: String,
    default: 'list', // 'list' or 'grid'
    validator: (value) => ['list', 'grid'].includes(value)
  },
  actionButton: {
    type: Object,
    default: null
  }
})

const formatStatValue = (value, type) => {
  if (value === null || value === undefined) return '---'
  
  switch (type) {
    case 'co2':
      return `${value.toFixed(1)}kg`
    case 'rank':
      return `#${value}`
    case 'percentage':
      return `${value}%`
    case 'days':
      return `${value} days`
    case 'points':
      return `${value} pts`
    case 'count':
      return value.toString()
    default:
      return value.toString()
  }
}
</script>