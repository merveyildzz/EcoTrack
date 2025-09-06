<template>
  <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <!-- Header -->
    <div class="text-center mb-8">
      <div class="w-20 h-20 bg-gradient-to-br from-purple-100 to-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
        <span class="text-4xl">🤖</span>
      </div>
      <h1 class="text-3xl font-bold text-gray-900 mb-2">EcoTrack AI Assistant</h1>
      <p class="text-gray-600 max-w-2xl mx-auto">
        Get personalized eco-friendly recommendations, ask questions about sustainability, 
        and discover new ways to reduce your carbon footprint with AI-powered insights.
      </p>
      <div class="flex items-center justify-center mt-4">
        <span class="px-3 py-1 bg-purple-100 text-purple-700 text-sm rounded-full flex items-center">
          ✨ Powered by Advanced AI
        </span>
      </div>
    </div>

    <!-- AI Status Card -->
    <div class="card mb-6" v-if="aiStatus">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-3">
          <div class="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
            <span class="text-green-600">✅</span>
          </div>
          <div>
            <h3 class="font-semibold text-gray-900">AI Status: Active</h3>
            <p class="text-sm text-gray-600">Using {{ aiStatus.current_provider || 'AI' }} • Model: {{ aiStatus.model || 'Advanced' }}</p>
          </div>
        </div>
        <button 
          @click="loadAIStatus"
          class="text-gray-400 hover:text-gray-600"
        >
          🔄
        </button>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
      <button
        @click="generateQuickRecommendation('daily_tip')"
        class="card hover:shadow-lg transition-all duration-200 text-left group"
        :disabled="isGenerating"
      >
        <div class="flex items-start space-x-3">
          <div class="w-12 h-12 bg-gradient-to-br from-green-100 to-emerald-100 rounded-lg flex items-center justify-center group-hover:from-green-200 group-hover:to-emerald-200 transition-colors">
            <span class="text-xl">💡</span>
          </div>
          <div class="flex-1">
            <h3 class="font-semibold text-gray-900 mb-1">Daily Eco Tip</h3>
            <p class="text-sm text-gray-600">Get a personalized tip for today</p>
          </div>
        </div>
      </button>

      <button
        @click="generateQuickRecommendation('coaching')"
        class="card hover:shadow-lg transition-all duration-200 text-left group"
        :disabled="isGenerating"
      >
        <div class="flex items-start space-x-3">
          <div class="w-12 h-12 bg-gradient-to-br from-blue-100 to-indigo-100 rounded-lg flex items-center justify-center group-hover:from-blue-200 group-hover:to-indigo-200 transition-colors">
            <span class="text-xl">🎯</span>
          </div>
          <div class="flex-1">
            <h3 class="font-semibold text-gray-900 mb-1">AI Coaching</h3>
            <p class="text-sm text-gray-600">Get guidance on your eco journey</p>
          </div>
        </div>
      </button>

      <button
        @click="showProductSearch = true"
        class="card hover:shadow-lg transition-all duration-200 text-left group"
      >
        <div class="flex items-start space-x-3">
          <div class="w-12 h-12 bg-gradient-to-br from-orange-100 to-yellow-100 rounded-lg flex items-center justify-center group-hover:from-orange-200 group-hover:to-yellow-200 transition-colors">
            <span class="text-xl">🛍️</span>
          </div>
          <div class="flex-1">
            <h3 class="font-semibold text-gray-900 mb-1">Find Eco Products</h3>
            <p class="text-sm text-gray-600">Discover sustainable alternatives</p>
          </div>
        </div>
      </button>
    </div>

    <!-- Product Search Modal -->
    <div v-if="showProductSearch" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 m-4 max-w-md w-full">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold">Search Eco Products</h3>
          <button @click="showProductSearch = false" class="text-gray-400 hover:text-gray-600">✕</button>
        </div>
        <div class="space-y-4">
          <input
            v-model="productQuery"
            placeholder="What eco-friendly product are you looking for?"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          />
          <div class="flex space-x-2">
            <button
              @click="searchProducts"
              :disabled="!productQuery.trim() || isSearching"
              class="flex-1 bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 disabled:opacity-50"
            >
              {{ isSearching ? '🔍 Searching...' : '🔍 Search' }}
            </button>
            <button
              @click="showProductSearch = false"
              class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Recent Recommendations -->
    <div class="card mb-6" v-if="recommendations.length > 0">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-lg font-semibold text-gray-900">Your AI Recommendations</h3>
        <button
          @click="loadRecommendations"
          class="text-purple-600 hover:text-purple-800 text-sm"
        >
          🔄 Refresh
        </button>
      </div>
      
      <div class="space-y-4">
        <div
          v-for="recommendation in recommendations"
          :key="recommendation.id"
          class="bg-gradient-to-r from-purple-50 to-blue-50 p-4 rounded-lg border border-purple-200"
        >
          <div class="flex items-start justify-between">
            <div class="flex-1">
              <div class="flex items-center space-x-2 mb-2">
                <span class="text-lg">{{ getRecommendationIcon(recommendation.recommendation_type) }}</span>
                <h4 class="font-medium text-gray-900">{{ recommendation.title || 'AI Recommendation' }}</h4>
                <span class="px-2 py-1 bg-purple-100 text-purple-700 text-xs rounded-full">
                  {{ formatRecommendationType(recommendation.recommendation_type) }}
                </span>
              </div>
              <p class="text-gray-700 text-sm mb-3">{{ recommendation.content }}</p>
              <div class="flex items-center justify-between">
                <span class="text-xs text-gray-500">{{ formatTimeAgo(recommendation.created_at) }}</span>
                <div class="flex space-x-2" v-if="!recommendation.user_rating">
                  <button 
                    @click="rateRecommendation(recommendation.id, 5)"
                    class="text-green-600 hover:text-green-800 text-sm"
                  >👍 Helpful</button>
                  <button 
                    @click="rateRecommendation(recommendation.id, 1)"
                    class="text-red-600 hover:text-red-800 text-sm"
                  >👎 Not helpful</button>
                </div>
                <span v-else class="text-xs text-gray-500">
                  {{ recommendation.user_rating >= 4 ? '👍 Rated helpful' : '👎 Rated not helpful' }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Product Suggestions -->
    <div class="card" v-if="productSuggestions.length > 0">
      <h3 class="text-lg font-semibold text-gray-900 mb-4">Recommended Eco Products</h3>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div
          v-for="product in productSuggestions"
          :key="product.id"
          class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
        >
          <div class="flex items-start justify-between mb-3">
            <h4 class="font-medium text-gray-900">{{ product.title }}</h4>
            <span class="px-2 py-1 bg-green-100 text-green-700 text-xs rounded-full">
              {{ product.category || 'Eco' }}
            </span>
          </div>
          <p class="text-gray-600 text-sm mb-3">{{ product.description }}</p>
          <div class="flex items-center justify-between">
            <span class="text-sm font-medium text-green-600">${{ product.price || 'N/A' }}</span>
            <button
              @click="trackProductInteraction(product.id, 'clicked')"
              class="text-purple-600 hover:text-purple-800 text-sm"
            >
              View Product →
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="recommendations.length === 0 && productSuggestions.length === 0 && !isLoading" class="card text-center py-12">
      <div class="w-24 h-24 bg-gradient-to-br from-purple-100 to-blue-100 rounded-full flex items-center justify-center mx-auto mb-6">
        <span class="text-4xl">🚀</span>
      </div>
      <h3 class="text-xl font-semibold text-gray-900 mb-3">Ready to Get Started?</h3>
      <p class="text-gray-600 mb-6 max-w-md mx-auto">
        Click on one of the quick actions above to get your first AI-powered recommendation!
      </p>
      <div class="flex flex-wrap justify-center gap-3">
        <span class="px-3 py-1 bg-gray-100 text-gray-700 text-sm rounded-full">🌱 Personalized Tips</span>
        <span class="px-3 py-1 bg-gray-100 text-gray-700 text-sm rounded-full">🎯 Smart Coaching</span>
        <span class="px-3 py-1 bg-gray-100 text-gray-700 text-sm rounded-full">🛍️ Product Discovery</span>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="card text-center py-12">
      <div class="w-8 h-8 border-4 border-purple-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
      <p class="text-gray-600">Loading AI recommendations...</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useNotificationStore } from '@/stores/notifications'
import aiService from '@/services/ai'

const notificationStore = useNotificationStore()

// Reactive data
const isLoading = ref(true)
const isGenerating = ref(false)
const isSearching = ref(false)
const aiStatus = ref(null)
const recommendations = ref([])
const productSuggestions = ref([])
const showProductSearch = ref(false)
const productQuery = ref('')

// Load AI status
const loadAIStatus = async () => {
  try {
    aiStatus.value = await aiService.getStatus()
  } catch (error) {
    console.log('AI status not available')
  }
}

// Load recommendations
const loadRecommendations = async () => {
  try {
    const data = await aiService.getRecommendations({ limit: 5 })
    recommendations.value = Array.isArray(data) ? data : data.results || []
  } catch (error) {
    console.log('No recommendations available')
    recommendations.value = []
  }
}

// Load product suggestions
const loadProductSuggestions = async () => {
  try {
    const data = await aiService.getProductSuggestions({ limit: 4 })
    productSuggestions.value = Array.isArray(data) ? data : data.results || []
  } catch (error) {
    console.log('No product suggestions available')
    productSuggestions.value = []
  }
}

// Generate quick recommendation
const generateQuickRecommendation = async (type) => {
  isGenerating.value = true
  try {
    const response = await aiService.generateRecommendation(type)
    if (response.recommendation) {
      recommendations.value.unshift(response.recommendation)
      notificationStore.success('New AI recommendation generated!')
    } else {
      notificationStore.info(response.message || 'Using recent recommendation')
    }
  } catch (error) {
    console.error('Failed to generate recommendation:', error)
    notificationStore.error('AI recommendations are currently unavailable. Please check your settings.')
  } finally {
    isGenerating.value = false
  }
}

// Search for products
const searchProducts = async () => {
  if (!productQuery.value.trim()) return
  
  isSearching.value = true
  try {
    const response = await aiService.searchProducts(productQuery.value, null, 6)
    productSuggestions.value = response.results || []
    showProductSearch.value = false
    productQuery.value = ''
    
    if (productSuggestions.value.length > 0) {
      notificationStore.success(`Found ${productSuggestions.value.length} eco-friendly products!`)
    } else {
      notificationStore.info('No products found. Try a different search term.')
    }
  } catch (error) {
    console.error('Failed to search products:', error)
    notificationStore.error('Product search is currently unavailable.')
  } finally {
    isSearching.value = false
  }
}

// Rate recommendation
const rateRecommendation = async (recommendationId, rating) => {
  try {
    await aiService.submitFeedback(recommendationId, rating)
    // Update the recommendation in the list
    const index = recommendations.value.findIndex(r => r.id === recommendationId)
    if (index !== -1) {
      recommendations.value[index].user_rating = rating
    }
    notificationStore.success('Thank you for your feedback!')
  } catch (error) {
    console.error('Failed to rate recommendation:', error)
    notificationStore.error('Failed to submit rating')
  }
}

// Track product interaction
const trackProductInteraction = async (productId, action) => {
  try {
    await aiService.trackProductInteraction(productId, action)
  } catch (error) {
    console.log('Failed to track interaction')
  }
}

// Helper functions
const getRecommendationIcon = (type) => {
  const icons = {
    'daily_tip': '💡',
    'coaching': '🎯',
    'activity': '🏃',
    'challenge': '🏆',
    'product': '🛍️'
  }
  return icons[type] || '✨'
}

const formatRecommendationType = (type) => {
  const types = {
    'daily_tip': 'Daily Tip',
    'coaching': 'AI Coaching',
    'activity': 'Activity',
    'challenge': 'Challenge',
    'product': 'Product'
  }
  return types[type] || 'Recommendation'
}

const formatTimeAgo = (dateString) => {
  const date = new Date(dateString)
  const now = new Date()
  const diffInSeconds = Math.floor((now - date) / 1000)
  
  if (diffInSeconds < 60) return 'Just now'
  if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`
  if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`
  return `${Math.floor(diffInSeconds / 86400)}d ago`
}

// Initialize
onMounted(async () => {
  try {
    await Promise.all([
      loadAIStatus(),
      loadRecommendations(),
      loadProductSuggestions()
    ])
  } catch (error) {
    console.error('Failed to load AI data:', error)
  } finally {
    isLoading.value = false
  }
})
</script>