<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900">EcoTrack Community</h1>
      <p class="mt-2 text-gray-600">Connect, share, and inspire eco-friendly actions together</p>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="flex items-center justify-center py-12">
      <div class="w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full animate-spin"></div>
      <span class="ml-3 text-gray-600">Loading community...</span>
    </div>

    <div v-else class="grid grid-cols-1 lg:grid-cols-3 gap-8">
      <!-- Main Content -->
      <div class="lg:col-span-2">
        <!-- Navigation Tabs -->
        <div class="bg-white rounded-lg shadow-sm mb-6">
          <nav class="flex space-x-8 px-6" aria-label="Community sections">
            <button
              v-for="tab in communityTabs"
              :key="tab.key"
              @click="activeTab = tab.key"
              :class="[
                'py-4 px-1 border-b-2 font-medium text-sm transition-colors',
                activeTab === tab.key
                  ? 'border-green-500 text-green-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              ]"
            >
              <span class="mr-2">{{ tab.icon }}</span>
              {{ tab.name }}
              <span v-if="tab.count" class="ml-2 bg-gray-100 text-gray-600 py-1 px-2 rounded-full text-xs">
                {{ tab.count }}
              </span>
            </button>
          </nav>
        </div>

        <!-- Tab Content -->
        <div class="space-y-6">
          <!-- Activity Feed Tab -->
          <div v-if="activeTab === 'feed'">
            <!-- Share Your Impact -->
            <div class="bg-white rounded-lg shadow-sm p-6 mb-6">
              <div class="flex items-start space-x-3">
                <img
                  v-if="currentUser?.avatar"
                  :src="currentUser.avatar"
                  :alt="currentUser.name"
                  class="w-10 h-10 rounded-full"
                />
                <div
                  v-else
                  class="w-10 h-10 bg-green-500 rounded-full flex items-center justify-center"
                >
                  <span class="text-white font-medium">
                    {{ currentUser?.first_name?.charAt(0) || 'U' }}
                  </span>
                </div>
                <div class="flex-1">
                  <textarea
                    v-model="shareText"
                    placeholder="Share your latest eco-achievement or tip with the community..."
                    rows="3"
                    class="w-full border-gray-300 rounded-lg shadow-sm focus:ring-green-500 focus:border-green-500 resize-none"
                  ></textarea>
                  <div class="flex justify-between items-center mt-3">
                    <div class="flex space-x-3 text-sm text-gray-500">
                      <button
                        @click="showImageUpload = true"
                        class="flex items-center hover:text-green-600"
                      >
                        📷 Photo
                      </button>
                      <button class="flex items-center hover:text-green-600">
                        📍 Location
                      </button>
                      <button class="flex items-center hover:text-green-600">
                        🏷️ Tag Activity
                      </button>
                    </div>
                    <button
                      @click="sharePost"
                      :disabled="!shareText.trim()"
                      class="px-4 py-2 bg-green-600 text-white rounded-lg text-sm font-medium hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Share
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <!-- Feed Items -->
            <div class="space-y-6">
              <div
                v-for="post in feedPosts"
                :key="post.id"
                class="bg-white rounded-lg shadow-sm p-6 hover:shadow-md transition-shadow"
              >
                <!-- Post Header -->
                <div class="flex items-center justify-between mb-4">
                  <div class="flex items-center space-x-3">
                    <img
                      v-if="post.user.avatar"
                      :src="post.user.avatar"
                      :alt="post.user.name"
                      class="w-10 h-10 rounded-full"
                    />
                    <div
                      v-else
                      class="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center"
                    >
                      <span class="text-white font-medium text-sm">
                        {{ post.user.first_name?.charAt(0) || 'U' }}
                      </span>
                    </div>
                    <div>
                      <div class="flex items-center space-x-2">
                        <h4 class="font-medium text-gray-900">{{ getUserDisplayName(post.user) }}</h4>
                        <span v-if="post.user.verified" class="text-green-500">✓</span>
                        <span v-if="post.is_featured" class="px-2 py-1 bg-yellow-100 text-yellow-800 text-xs rounded-full">
                          ⭐ Featured
                        </span>
                      </div>
                      <p class="text-sm text-gray-500">{{ formatTimeAgo(post.created_at) }}</p>
                    </div>
                  </div>
                  <button class="text-gray-400 hover:text-gray-600">
                    ⋯
                  </button>
                </div>

                <!-- Post Content -->
                <div class="mb-4">
                  <p class="text-gray-900 mb-3">{{ post.content }}</p>
                  
                  <!-- Achievement Display -->
                  <div
                    v-if="post.achievement"
                    class="bg-gradient-to-r from-green-50 to-blue-50 rounded-lg p-4 border border-green-200 mb-3"
                  >
                    <div class="flex items-center space-x-3">
                      <div class="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
                        <span class="text-2xl">{{ getAchievementIcon(post.achievement.type) }}</span>
                      </div>
                      <div>
                        <h5 class="font-medium text-gray-900">{{ post.achievement.title }}</h5>
                        <p class="text-sm text-gray-600">{{ post.achievement.description }}</p>
                        <div class="flex space-x-4 mt-2 text-sm">
                          <span class="text-green-600">🌱 {{ post.achievement.co2_saved }}kg CO₂ saved</span>
                          <span class="text-blue-600">⭐ {{ post.achievement.points }} points</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- Post Image -->
                  <img
                    v-if="post.image"
                    :src="post.image"
                    :alt="'Post by ' + getUserDisplayName(post.user)"
                    class="w-full rounded-lg mb-3 max-h-96 object-cover"
                  />
                </div>

                <!-- Post Actions -->
                <div class="flex items-center justify-between pt-3 border-t border-gray-100">
                  <div class="flex items-center space-x-6">
                    <button
                      @click="toggleLike(post)"
                      class="flex items-center space-x-2 text-sm hover:text-green-600 transition-colors"
                      :class="post.isLiked ? 'text-green-600' : 'text-gray-500'"
                    >
                      <span class="text-lg">{{ post.isLiked ? '💚' : '🤍' }}</span>
                      <span>{{ post.likes || 0 }}</span>
                    </button>
                    <button class="flex items-center space-x-2 text-sm text-gray-500 hover:text-blue-600">
                      <span class="text-lg">💬</span>
                      <span>{{ post.comments || 0 }}</span>
                    </button>
                    <button class="flex items-center space-x-2 text-sm text-gray-500 hover:text-purple-600">
                      <span class="text-lg">🔄</span>
                      <span>{{ post.shares || 0 }}</span>
                    </button>
                  </div>
                  <button class="text-sm text-gray-500 hover:text-gray-700">
                    🔗 Share
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Challenges Tab -->
          <div v-if="activeTab === 'challenges'">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div
                v-for="challenge in communityChallenges"
                :key="challenge.id"
                class="bg-white rounded-lg shadow-sm p-6 hover:shadow-md transition-shadow"
              >
                <div class="flex justify-between items-start mb-4">
                  <div>
                    <h3 class="text-lg font-semibold text-gray-900">{{ challenge.title }}</h3>
                    <p class="text-sm text-gray-600 mt-1">{{ challenge.description }}</p>
                  </div>
                  <span class="px-3 py-1 bg-green-100 text-green-800 text-sm rounded-full">
                    {{ challenge.status }}
                  </span>
                </div>
                
                <div class="space-y-3 mb-4">
                  <div class="flex justify-between text-sm">
                    <span class="text-gray-600">Progress</span>
                    <span class="font-medium">{{ challenge.progress }}%</span>
                  </div>
                  <div class="w-full bg-gray-200 rounded-full h-2">
                    <div
                      class="bg-green-600 h-2 rounded-full transition-all duration-500"
                      :style="{ width: challenge.progress + '%' }"
                    ></div>
                  </div>
                  <div class="flex justify-between text-sm text-gray-600">
                    <span>{{ challenge.participants }} participants</span>
                    <span>{{ challenge.timeLeft }} left</span>
                  </div>
                </div>

                <button
                  v-if="!challenge.isJoined"
                  @click="joinChallenge(challenge)"
                  class="w-full bg-green-600 text-white py-2 rounded-lg hover:bg-green-700"
                >
                  Join Challenge
                </button>
                <button
                  v-else
                  class="w-full bg-green-100 text-green-800 py-2 rounded-lg cursor-not-allowed"
                >
                  ✓ Joined
                </button>
              </div>
            </div>
          </div>

          <!-- Events Tab -->
          <div v-if="activeTab === 'events'">
            <div class="space-y-6">
              <div
                v-for="event in communityEvents"
                :key="event.id"
                class="bg-white rounded-lg shadow-sm p-6"
              >
                <div class="flex items-start space-x-4">
                  <div class="text-center">
                    <div class="bg-green-100 text-green-800 px-3 py-2 rounded-lg">
                      <div class="text-lg font-bold">{{ event.day }}</div>
                      <div class="text-xs">{{ event.month }}</div>
                    </div>
                  </div>
                  <div class="flex-1">
                    <h3 class="text-lg font-semibold text-gray-900">{{ event.title }}</h3>
                    <p class="text-gray-600 mt-1">{{ event.description }}</p>
                    <div class="flex items-center space-x-4 mt-3 text-sm text-gray-500">
                      <span>📍 {{ event.location }}</span>
                      <span>🕐 {{ event.time }}</span>
                      <span>👥 {{ event.attendees }} attending</span>
                    </div>
                    <button
                      @click="attendEvent(event)"
                      :class="[
                        'mt-3 px-4 py-2 rounded-lg text-sm font-medium',
                        event.isAttending
                          ? 'bg-green-100 text-green-800'
                          : 'bg-green-600 text-white hover:bg-green-700'
                      ]"
                    >
                      {{ event.isAttending ? '✓ Attending' : 'Attend Event' }}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Groups Tab -->
          <div v-if="activeTab === 'groups'">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div
                v-for="group in communityGroups"
                :key="group.id"
                class="bg-white rounded-lg shadow-sm p-6"
              >
                <div class="flex items-start space-x-3 mb-4">
                  <img
                    v-if="group.avatar"
                    :src="group.avatar"
                    :alt="group.name"
                    class="w-12 h-12 rounded-lg"
                  />
                  <div
                    v-else
                    class="w-12 h-12 bg-gradient-to-br from-green-400 to-blue-500 rounded-lg flex items-center justify-center"
                  >
                    <span class="text-white font-bold">{{ group.name.charAt(0) }}</span>
                  </div>
                  <div class="flex-1">
                    <h3 class="font-semibold text-gray-900">{{ group.name }}</h3>
                    <p class="text-sm text-gray-600">{{ group.description }}</p>
                    <div class="flex items-center space-x-3 mt-2 text-sm text-gray-500">
                      <span>👥 {{ group.members }} members</span>
                      <span>📝 {{ group.posts }} posts</span>
                    </div>
                  </div>
                </div>
                <button
                  @click="joinGroup(group)"
                  :class="[
                    'w-full py-2 rounded-lg text-sm font-medium',
                    group.isJoined
                      ? 'bg-gray-100 text-gray-800'
                      : 'bg-green-600 text-white hover:bg-green-700'
                  ]"
                >
                  {{ group.isJoined ? '✓ Joined' : 'Join Group' }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Sidebar -->
      <div class="space-y-6">
        <!-- Your Stats -->
        <div class="bg-white rounded-lg shadow-sm p-6">
          <h3 class="font-semibold text-gray-900 mb-4">Your Impact This Week</h3>
          <div class="space-y-4">
            <div class="text-center">
              <div class="text-3xl font-bold text-green-600">{{ userStats?.weekly_co2 || 0 }}kg</div>
              <div class="text-sm text-gray-600">CO₂ Saved</div>
            </div>
            <div class="grid grid-cols-2 gap-4 text-center">
              <div>
                <div class="text-xl font-semibold text-blue-600">{{ userStats?.activities || 0 }}</div>
                <div class="text-xs text-gray-600">Activities</div>
              </div>
              <div>
                <div class="text-xl font-semibold text-purple-600">{{ userStats?.streak || 0 }}</div>
                <div class="text-xs text-gray-600">Day Streak</div>
              </div>
            </div>
            <div class="pt-3 border-t">
              <div class="flex justify-between text-sm">
                <span class="text-gray-600">Community Rank</span>
                <span class="font-medium text-green-600">#{{ userStats?.rank || '---' }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Trending Topics -->
        <div class="bg-white rounded-lg shadow-sm p-6">
          <h3 class="font-semibold text-gray-900 mb-4">Trending Topics</h3>
          <div class="space-y-3">
            <div
              v-for="topic in trendingTopics"
              :key="topic.id"
              class="flex items-center justify-between hover:bg-gray-50 p-2 rounded-lg cursor-pointer"
            >
              <div>
                <div class="font-medium text-gray-900 text-sm">#{{ topic.tag }}</div>
                <div class="text-xs text-gray-500">{{ topic.posts }} posts</div>
              </div>
              <div class="text-green-600 text-xs">{{ topic.growth }}↗️</div>
            </div>
          </div>
        </div>

        <!-- Community Leaders -->
        <div class="bg-white rounded-lg shadow-sm p-6">
          <div class="flex justify-between items-center mb-4">
            <h3 class="font-semibold text-gray-900">Community Leaders</h3>
            <router-link to="/leaderboards" class="text-sm text-green-600 hover:text-green-700">
              View All
            </router-link>
          </div>
          <div class="space-y-3">
            <div
              v-for="(leader, index) in communityLeaders"
              :key="leader.id"
              class="flex items-center space-x-3"
            >
              <span class="text-lg">{{ ['🥇', '🥈', '🥉'][index] || '🏅' }}</span>
              <img
                v-if="leader.avatar"
                :src="leader.avatar"
                :alt="leader.name"
                class="w-8 h-8 rounded-full"
              />
              <div
                v-else
                class="w-8 h-8 bg-gradient-to-br from-green-400 to-blue-500 rounded-full flex items-center justify-center"
              >
                <span class="text-white text-xs font-medium">
                  {{ leader.first_name?.charAt(0) || 'U' }}
                </span>
              </div>
              <div class="flex-1">
                <div class="font-medium text-gray-900 text-sm">{{ getUserDisplayName(leader) }}</div>
                <div class="text-xs text-gray-500">{{ leader.total_co2 }}kg CO₂ saved</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Quick Actions -->
        <div class="bg-white rounded-lg shadow-sm p-6">
          <h3 class="font-semibold text-gray-900 mb-4">Community Actions</h3>
          <div class="space-y-3">
            <button
              @click="createGroup"
              class="w-full flex items-center justify-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 text-sm"
            >
              🏠 Create Group
            </button>
            <button
              @click="startChallenge"
              class="w-full flex items-center justify-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm"
            >
              🎯 Start Challenge
            </button>
            <button
              @click="organizeEvent"
              class="w-full flex items-center justify-center px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 text-sm"
            >
              📅 Organize Event
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
const activeTab = ref('feed')
const shareText = ref('')
const showImageUpload = ref(false)

// Data
const feedPosts = ref([])
const communityChallenges = ref([])
const communityEvents = ref([])
const communityGroups = ref([])
const userStats = ref({})
const trendingTopics = ref([])
const communityLeaders = ref([])

const currentUser = computed(() => authStore.user)

const communityTabs = [
  { key: 'feed', name: 'Activity Feed', icon: '🌍', count: null },
  { key: 'challenges', name: 'Challenges', icon: '🎯', count: 12 },
  { key: 'events', name: 'Events', icon: '📅', count: 5 },
  { key: 'groups', name: 'Groups', icon: '👥', count: 8 }
]

// Mock data initialization
const initializeMockData = () => {
  // Mock feed posts
  feedPosts.value = [
    {
      id: 1,
      user: { id: 1, first_name: 'Sarah', last_name: 'Green', avatar: null, verified: true },
      content: 'Just completed my first month of cycling to work! The fresh air and exercise make such a difference to my day.',
      created_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
      achievement: {
        type: 'streak',
        title: '30-Day Cycling Streak',
        description: 'Cycled to work for 30 consecutive days',
        co2_saved: 45.5,
        points: 500
      },
      likes: 24,
      comments: 8,
      shares: 3,
      isLiked: false,
      is_featured: true
    },
    {
      id: 2,
      user: { id: 2, first_name: 'Marcus', last_name: 'Chen', avatar: null },
      content: 'Switched to renewable energy for my home today! Every small step counts towards our planet\'s future. 🌱',
      created_at: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(),
      achievement: {
        type: 'milestone',
        title: 'Green Energy Hero',
        description: 'Switched to 100% renewable energy',
        co2_saved: 120.0,
        points: 1000
      },
      likes: 42,
      comments: 12,
      shares: 7,
      isLiked: true
    }
  ]

  // Mock challenges
  communityChallenges.value = [
    {
      id: 1,
      title: 'Plastic-Free Week',
      description: 'Reduce single-use plastic for 7 days',
      status: 'Active',
      progress: 65,
      participants: 234,
      timeLeft: '3 days',
      isJoined: false
    },
    {
      id: 2,
      title: 'Car-Free Challenge',
      description: 'Use alternative transport for a month',
      status: 'Active',
      progress: 82,
      participants: 156,
      timeLeft: '12 days',
      isJoined: true
    }
  ]

  // Mock events
  communityEvents.value = [
    {
      id: 1,
      title: 'Community Tree Planting',
      description: 'Join us for a morning of tree planting in Central Park',
      day: '15',
      month: 'SEP',
      location: 'Central Park',
      time: '9:00 AM',
      attendees: 87,
      isAttending: false
    }
  ]

  // Mock groups
  communityGroups.value = [
    {
      id: 1,
      name: 'Urban Gardeners',
      description: 'Tips and tricks for city gardening',
      members: 1240,
      posts: 89,
      isJoined: false
    },
    {
      id: 2,
      name: 'Zero Waste Living',
      description: 'Living plastic-free and waste-free',
      members: 2100,
      posts: 156,
      isJoined: true
    }
  ]

  // Mock user stats
  userStats.value = {
    weekly_co2: 23.5,
    activities: 12,
    streak: 7,
    rank: 156
  }

  // Mock trending topics
  trendingTopics.value = [
    { id: 1, tag: 'PlasticFree', posts: 89, growth: '+12%' },
    { id: 2, tag: 'Cycling', posts: 67, growth: '+8%' },
    { id: 3, tag: 'SolarPower', posts: 45, growth: '+15%' }
  ]

  // Mock community leaders
  communityLeaders.value = [
    { id: 1, first_name: 'Emma', last_name: 'Watson', total_co2: 234.5 },
    { id: 2, first_name: 'David', last_name: 'Kim', total_co2: 198.2 },
    { id: 3, first_name: 'Lisa', last_name: 'Rodriguez', total_co2: 176.8 }
  ]
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

const getAchievementIcon = (type) => {
  const icons = {
    streak: '🔥',
    milestone: '🎉',
    badge: '🏆',
    challenge: '🎯'
  }
  return icons[type] || '⭐'
}

const sharePost = () => {
  if (!shareText.value.trim()) return
  
  const newPost = {
    id: Date.now(),
    user: currentUser.value,
    content: shareText.value,
    created_at: new Date().toISOString(),
    likes: 0,
    comments: 0,
    shares: 0,
    isLiked: false
  }
  
  feedPosts.value.unshift(newPost)
  shareText.value = ''
  notificationStore.success('Post shared with the community!')
}

const toggleLike = (post) => {
  post.isLiked = !post.isLiked
  post.likes += post.isLiked ? 1 : -1
}

const joinChallenge = (challenge) => {
  challenge.isJoined = true
  challenge.participants += 1
  notificationStore.success(`Joined ${challenge.title}!`)
}

const attendEvent = (event) => {
  event.isAttending = !event.isAttending
  event.attendees += event.isAttending ? 1 : -1
  notificationStore.success(event.isAttending ? `You're attending ${event.title}!` : `Removed from ${event.title}`)
}

const joinGroup = (group) => {
  group.isJoined = !group.isJoined
  group.members += group.isJoined ? 1 : -1
  notificationStore.success(group.isJoined ? `Joined ${group.name}!` : `Left ${group.name}`)
}

const createGroup = () => {
  notificationStore.info('Group creation feature coming soon!')
}

const startChallenge = () => {
  notificationStore.info('Challenge creation feature coming soon!')
}

const organizeEvent = () => {
  notificationStore.info('Event organization feature coming soon!')
}

onMounted(async () => {
  try {
    // Initialize with mock data for now
    initializeMockData()
    
    // In a real app, load data from API
    // await loadCommunityData()
  } finally {
    isLoading.value = false
  }
})
</script>

<style scoped>
.btn-primary {
  @apply px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 font-medium transition-colors;
}

.btn-secondary {
  @apply px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 font-medium transition-colors;
}

.btn-outline {
  @apply px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 font-medium transition-colors;
}
</style>
</template>