<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900">Community Feed</h1>
      <p class="mt-2 text-gray-600">See what other eco-warriors are achieving</p>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="flex items-center justify-center py-12">
      <div class="w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full animate-spin"></div>
      <span class="ml-3 text-gray-600">Loading activity feed...</span>
    </div>

    <div v-else class="grid grid-cols-1 lg:grid-cols-3 gap-8">
      <!-- Main Feed -->
      <div class="lg:col-span-2">
        <!-- Feed Filters -->
        <div class="flex flex-wrap gap-3 mb-6">
          <button
            v-for="filter in feedFilters"
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

        <!-- Feed Items -->
        <div class="space-y-4">
          <div
            v-for="item in filteredFeedItems"
            :key="item.id"
            class="card hover:shadow-md transition-shadow"
          >
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
                    @click="toggleLike(item)"
                    class="flex items-center space-x-1 text-sm text-gray-500 hover:text-primary-600 transition-colors"
                    :class="item.isLiked ? 'text-primary-600' : ''"
                  >
                    <span>{{ item.isLiked ? '❤️' : '🤍' }}</span>
                    <span>{{ item.likes || 0 }}</span>
                  </button>
                  <button class="flex items-center space-x-1 text-sm text-gray-500 hover:text-primary-600 transition-colors">
                    <span>👏</span>
                    <span>{{ item.claps || 0 }}</span>
                  </button>
                  <button class="text-sm text-gray-500 hover:text-primary-600 transition-colors">
                    Share
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Empty State -->
        <div v-if="filteredFeedItems.length === 0" class="text-center py-12">
          <span class="text-4xl mb-4 block">📱</span>
          <h3 class="text-lg font-medium text-gray-900 mb-2">No activity yet</h3>
          <p class="text-gray-600">Be the first to share your eco-achievements!</p>
        </div>

        <!-- Load More -->
        <div v-if="hasMore" class="text-center mt-8">
          <button 
            @click="loadMore"
            :disabled="isLoadingMore"
            class="btn-secondary"
          >
            <span v-if="isLoadingMore">Loading...</span>
            <span v-else>Load More</span>
          </button>
        </div>
      </div>

      <!-- Sidebar -->
      <div class="space-y-6">
        <!-- Quick Stats -->
        <div class="card">
          <h3 class="font-semibold text-gray-900 mb-4">Your Impact Today</h3>
          <div class="space-y-3">
            <div class="flex items-center justify-between">
              <span class="text-gray-600">CO₂ Saved</span>
              <span class="font-medium">{{ userStats?.daily_co2 || 0 }}kg</span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-gray-600">Activities</span>
              <span class="font-medium">{{ userStats?.daily_activities || 0 }}</span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-gray-600">Streak</span>
              <span class="font-medium">{{ userStats?.current_streak || 0 }} days</span>
            </div>
          </div>
        </div>

        <!-- Top Contributors -->
        <div class="card">
          <h3 class="font-semibold text-gray-900 mb-4">Top Contributors This Week</h3>
          <div class="space-y-3">
            <div
              v-for="(contributor, index) in topContributors"
              :key="contributor.id"
              class="flex items-center space-x-3"
            >
              <div class="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
                <span class="text-primary-600 text-sm font-medium">
                  {{ getUserInitial(contributor) }}
                </span>
              </div>
              <div class="flex-1">
                <p class="font-medium text-gray-900 text-sm">{{ getUserDisplayName(contributor) }}</p>
                <p class="text-xs text-gray-500">{{ contributor.weekly_co2 }}kg CO₂ saved</p>
              </div>
              <span class="text-lg">{{ ['🥇', '🥈', '🥉', '🏅', '🏅'][index] }}</span>
            </div>
          </div>
        </div>

        <!-- Recent Badges -->
        <div class="card">
          <h3 class="font-semibold text-gray-900 mb-4">Recent Badges</h3>
          <div class="space-y-3">
            <div
              v-for="badge in recentBadges"
              :key="badge.id"
              class="flex items-center space-x-3"
            >
              <div class="w-8 h-8 bg-yellow-100 rounded-full flex items-center justify-center">
                <span>🏆</span>
              </div>
              <div>
                <p class="font-medium text-gray-900 text-sm">{{ badge.badge.name }}</p>
                <p class="text-xs text-gray-500">{{ formatTimeAgo(badge.earned_at) }}</p>
              </div>
            </div>
          </div>
          <div v-if="recentBadges.length === 0" class="text-center py-4">
            <p class="text-sm text-gray-500">No recent badges</p>
          </div>
        </div>

        <!-- Quick Actions -->
        <div class="card">
          <h3 class="font-semibold text-gray-900 mb-4">Quick Actions</h3>
          <div class="space-y-2">
            <router-link to="/log-activity" class="btn-primary w-full text-center">
              Log Activity
            </router-link>
            <router-link to="/challenges" class="btn-secondary w-full text-center">
              Join Challenge
            </router-link>
            <button @click="refreshFeed" class="btn-outline w-full">
              Refresh Feed
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useNotificationStore } from '@/stores/notifications'
import socialApi from '@/services/social'

const authStore = useAuthStore()
const notificationStore = useNotificationStore()

const isLoading = ref(true)
const isLoadingMore = ref(false)
const feedItems = ref([])
const selectedFilter = ref('all')
const hasMore = ref(true)
const userStats = ref(null)
const topContributors = ref([])
const recentBadges = ref([])

const feedFilters = [
  { value: 'all', label: 'All Activity', icon: '🌍' },
  { value: 'badge_earned', label: 'Badges', icon: '🏆' },
  { value: 'challenge_completed', label: 'Challenges', icon: '🎯' },
  { value: 'leaderboard_rank', label: 'Rankings', icon: '📈' },
  { value: 'milestone_reached', label: 'Milestones', icon: '🎉' }
]

const filteredFeedItems = computed(() => {
  if (selectedFilter.value === 'all') {
    return feedItems.value
  }
  return feedItems.value.filter(item => item.activity_type === selectedFilter.value)
})

const loadSocialFeed = async () => {
  try {
    const data = await socialApi.getSocialFeed()
    feedItems.value = (data.results || data).map(item => ({
      ...item,
      isLiked: false, // This would come from API
      likes: Math.floor(Math.random() * 20), // Mock data
      claps: Math.floor(Math.random() * 15)
    }))
  } catch (error) {
    console.error('Error loading social feed:', error)
    notificationStore.error('Failed to load activity feed')
  }
}

const loadSidebarData = async () => {
  try {
    const [dashboard, userBadges] = await Promise.all([
      socialApi.getUserDashboard(),
      socialApi.getUserBadges()
    ])
    
    userStats.value = dashboard.stats
    recentBadges.value = (dashboard.recent_badges || []).slice(0, 5)
    
    // Mock top contributors data
    topContributors.value = [
      { id: 1, first_name: 'Alex', last_name: 'Green', email: 'alex@example.com', weekly_co2: 45.2 },
      { id: 2, first_name: 'Maria', last_name: 'Silva', email: 'maria@example.com', weekly_co2: 42.1 },
      { id: 3, first_name: 'Chen', last_name: 'Wei', email: 'chen@example.com', weekly_co2: 38.9 },
      { id: 4, first_name: 'Sarah', last_name: 'Johnson', email: 'sarah@example.com', weekly_co2: 35.7 },
      { id: 5, first_name: 'Ahmed', last_name: 'Hassan', email: 'ahmed@example.com', weekly_co2: 33.2 }
    ]
  } catch (error) {
    console.error('Error loading sidebar data:', error)
  }
}

const loadMore = async () => {
  if (isLoadingMore.value) return
  
  isLoadingMore.value = true
  try {
    // In real app, this would load next page
    await new Promise(resolve => setTimeout(resolve, 1000))
    hasMore.value = false
  } catch (error) {
    notificationStore.error('Failed to load more items')
  } finally {
    isLoadingMore.value = false
  }
}

const refreshFeed = async () => {
  try {
    await socialApi.refreshUserData()
    await loadSocialFeed()
    notificationStore.success('Feed refreshed!')
  } catch (error) {
    notificationStore.error('Failed to refresh feed')
  }
}

const toggleLike = async (item) => {
  // Mock like functionality
  item.isLiked = !item.isLiked
  item.likes += item.isLiked ? 1 : -1
  
  // In real app, this would call API
  notificationStore.success(item.isLiked ? 'Liked!' : 'Unliked!')
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

onMounted(async () => {
  await Promise.all([
    loadSocialFeed(),
    loadSidebarData()
  ])
  isLoading.value = false
})
</script>