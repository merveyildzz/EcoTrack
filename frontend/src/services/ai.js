import api from './api'

/**
 * AI Recommendations Service
 * Handles all AI-related API calls
 */
export const aiService = {
  // AI Status
  async getStatus() {
    const response = await api.get('/ai/status/')
    return response.data
  },

  // AI Preferences
  async getPreferences() {
    const response = await api.get('/ai/preferences/')
    return response.data
  },

  async updatePreferences(preferences) {
    const response = await api.put('/ai/preferences/', preferences)
    return response.data
  },

  // Recommendations
  async getRecommendations(params = {}) {
    const response = await api.get('/ai/recommendations/', { params })
    return response.data
  },

  async generateRecommendation(type = 'daily_tip', forceRegenerate = false) {
    const response = await api.post('/ai/recommendations/generate/', {
      recommendation_type: type,
      force_regenerate: forceRegenerate
    })
    return response.data
  },

  async getRecommendation(id) {
    const response = await api.get(`/ai/recommendations/${id}/`)
    return response.data
  },

  async updateRecommendation(id, data) {
    const response = await api.patch(`/ai/recommendations/${id}/`, data)
    return response.data
  },

  async submitFeedback(id, rating, feedback = '') {
    const response = await api.post(`/ai/recommendations/${id}/feedback/`, {
      rating,
      feedback
    })
    return response.data
  },

  // Product Suggestions
  async searchProducts(query, category = null, maxResults = 10) {
    const response = await api.post('/ai/products/search/', {
      query,
      category,
      max_results: maxResults
    })
    return response.data
  },

  async getProductSuggestions(params = {}) {
    const response = await api.get('/ai/products/', { params })
    return response.data
  },

  async trackProductInteraction(productId, action, interestLevel = null) {
    const response = await api.post(`/ai/products/${productId}/interact/`, {
      action,
      interest_level: interestLevel
    })
    return response.data
  },

  // Statistics
  async getStats() {
    const response = await api.get('/ai/stats/')
    return response.data
  }
}

export default aiService