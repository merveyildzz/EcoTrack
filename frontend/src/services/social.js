import api from './api'

export const socialApi = {
  // Badges
  async getBadges() {
    const response = await api.get('/social/badges/')
    return response.data
  },

  async getUserBadges() {
    const response = await api.get('/social/badges/user/')
    return response.data
  },

  // Challenges  
  async getChallenges(params = {}) {
    const response = await api.get('/social/challenges/', { params })
    return response.data
  },

  async getChallenge(id) {
    const response = await api.get(`/social/challenges/${id}/`)
    return response.data
  },

  async createChallenge(challengeData) {
    const response = await api.post('/social/challenges/', challengeData)
    return response.data
  },

  async joinChallenge(id) {
    const response = await api.post(`/social/challenges/${id}/join/`)
    return response.data
  },

  async leaveChallenge(id) {
    const response = await api.post(`/social/challenges/${id}/leave/`)
    return response.data
  },

  async getUserChallenges(params = {}) {
    const response = await api.get('/social/challenges/user/', { params })
    return response.data
  },

  // Leaderboards
  async getLeaderboards(params = {}) {
    const response = await api.get('/social/leaderboards/', { params })
    return response.data
  },

  async getLeaderboard(id) {
    const response = await api.get(`/social/leaderboards/${id}/`)
    return response.data
  },

  async getUserLeaderboardPosition(leaderboardId) {
    const response = await api.get(`/social/leaderboards/${leaderboardId}/position/`)
    return response.data
  },

  // Social Feed
  async getSocialFeed(params = {}) {
    const response = await api.get('/social/feed/', { params })
    return response.data
  },

  // User Stats & Dashboard
  async getUserStats() {
    const response = await api.get('/social/stats/')
    return response.data
  },

  async getUserDashboard() {
    const response = await api.get('/social/dashboard/')
    return response.data
  },

  async refreshUserData() {
    const response = await api.post('/social/refresh/')
    return response.data
  }
}

export default socialApi