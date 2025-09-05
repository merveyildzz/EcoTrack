import api from './api'

class EnterpriseService {
  // Organization Management
  async getOrganizations(params = {}) {
    const response = await api.get('/corporate/organizations/', { params })
    return response.data
  }

  async getOrganization(id) {
    const response = await api.get(`/corporate/organizations/${id}/`)
    return response.data
  }

  async createOrganization(data) {
    const response = await api.post('/corporate/organizations/', data)
    return response.data
  }

  async updateOrganization(id, data) {
    const response = await api.put(`/corporate/organizations/${id}/`, data)
    return response.data
  }

  async deleteOrganization(id) {
    await api.delete(`/corporate/organizations/${id}/`)
  }

  async getOrganizationStats(organizationId = null) {
    const url = organizationId 
      ? `/corporate/organizations/${organizationId}/stats/`
      : '/corporate/stats/'
    const response = await api.get(url)
    return response.data
  }

  async getOrganizationSettings(organizationId = null) {
    const url = organizationId 
      ? `/corporate/organizations/${organizationId}/settings/`
      : '/corporate/settings/'
    const response = await api.get(url)
    return response.data
  }

  async updateOrganizationSettings(data, organizationId = null) {
    const url = organizationId 
      ? `/corporate/organizations/${organizationId}/settings/`
      : '/corporate/settings/'
    const response = await api.put(url, data)
    return response.data
  }

  // User Management
  async getUsers(params = {}) {
    const response = await api.get('/corporate/users/', { params })
    return response.data
  }

  async getUser(id) {
    const response = await api.get(`/corporate/users/${id}/`)
    return response.data
  }

  async inviteUser(data) {
    const response = await api.post('/corporate/users/invite/', data)
    return response.data
  }

  async updateUser(id, data) {
    const response = await api.put(`/corporate/users/${id}/`, data)
    return response.data
  }

  async deleteUser(id) {
    await api.delete(`/corporate/users/${id}/`)
  }

  async resendInvite(id) {
    const response = await api.post(`/corporate/users/${id}/resend-invite/`)
    return response.data
  }

  async exportUsers(params = {}) {
    const response = await api.get('/corporate/users/export/', {
      params,
      responseType: 'blob'
    })
    return response.data
  }

  // Team Management
  async getTeams(params = {}) {
    const response = await api.get('/corporate/teams/', { params })
    return response.data
  }

  async getTeam(id) {
    const response = await api.get(`/corporate/teams/${id}/`)
    return response.data
  }

  async createTeam(data) {
    const response = await api.post('/corporate/teams/', data)
    return response.data
  }

  async updateTeam(id, data) {
    const response = await api.put(`/corporate/teams/${id}/`, data)
    return response.data
  }

  async deleteTeam(id) {
    await api.delete(`/corporate/teams/${id}/`)
  }

  async getTeamMembers(teamId, params = {}) {
    const response = await api.get(`/corporate/teams/${teamId}/members/`, { params })
    return response.data
  }

  async addTeamMember(teamId, data) {
    const response = await api.post(`/corporate/teams/${teamId}/members/`, data)
    return response.data
  }

  async removeTeamMember(teamId, userId) {
    await api.delete(`/corporate/teams/${teamId}/members/${userId}/`)
  }

  async updateTeamMember(teamId, userId, data) {
    const response = await api.put(`/corporate/teams/${teamId}/members/${userId}/`, data)
    return response.data
  }

  // Challenge Management
  async getChallenges(params = {}) {
    const response = await api.get('/corporate/challenges/', { params })
    return response.data
  }

  async getChallenge(id) {
    const response = await api.get(`/corporate/challenges/${id}/`)
    return response.data
  }

  async createChallenge(data) {
    const response = await api.post('/corporate/challenges/', data)
    return response.data
  }

  async updateChallenge(id, data) {
    const response = await api.put(`/corporate/challenges/${id}/`, data)
    return response.data
  }

  async deleteChallenge(id) {
    await api.delete(`/corporate/challenges/${id}/`)
  }

  async getChallengeParticipants(challengeId, params = {}) {
    const response = await api.get(`/corporate/challenges/${challengeId}/participants/`, { params })
    return response.data
  }

  // Bulk Import/Export
  async bulkImport(type, file, options = {}) {
    const formData = new FormData()
    formData.append('file', file)
    
    // Add options to form data
    Object.keys(options).forEach(key => {
      formData.append(key, options[key])
    })

    const response = await api.post(`/corporate/bulk-import/${type}/`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    return response.data
  }

  async getBulkImportStatus(taskId) {
    const response = await api.get(`/corporate/bulk-import/status/${taskId}/`)
    return response.data
  }

  async downloadTemplate(type) {
    const response = await api.get(`/corporate/bulk-import/template/${type}/`, {
      responseType: 'blob'
    })
    return response.data
  }

  // Analytics and Reporting
  async getAnalytics(params = {}) {
    const response = await api.get('/corporate/analytics/', { params })
    return response.data
  }

  async getCarbonReport(params = {}) {
    const response = await api.get('/corporate/reports/carbon/', { params })
    return response.data
  }

  async getUserActivityReport(params = {}) {
    const response = await api.get('/corporate/reports/user-activity/', { params })
    return response.data
  }

  async getTeamPerformanceReport(params = {}) {
    const response = await api.get('/corporate/reports/team-performance/', { params })
    return response.data
  }

  async exportReport(type, params = {}) {
    const response = await api.get(`/corporate/reports/${type}/export/`, {
      params,
      responseType: 'blob'
    })
    return response.data
  }

  // Dashboard Data
  async getDashboardData(organizationId = null) {
    const url = organizationId 
      ? `/corporate/organizations/${organizationId}/dashboard/`
      : '/corporate/dashboard/'
    const response = await api.get(url)
    return response.data
  }

  async getActivityTimeline(params = {}) {
    const response = await api.get('/corporate/activity-timeline/', { params })
    return response.data
  }

  async getLeaderboard(type = 'users', params = {}) {
    const response = await api.get(`/corporate/leaderboard/${type}/`, { params })
    return response.data
  }

  // System Management
  async getSystemHealth() {
    const response = await api.get('/corporate/system/health/')
    return response.data
  }

  async getSystemLogs(params = {}) {
    const response = await api.get('/corporate/system/logs/', { params })
    return response.data
  }

  async getAuditLog(params = {}) {
    const response = await api.get('/corporate/audit-log/', { params })
    return response.data
  }

  // Permissions and Roles
  async getUserPermissions(userId) {
    const response = await api.get(`/corporate/users/${userId}/permissions/`)
    return response.data
  }

  async updateUserRole(userId, organizationId, role) {
    const response = await api.put(`/corporate/users/${userId}/role/`, {
      organization_id: organizationId,
      role
    })
    return response.data
  }

  async getOrganizationRoles(organizationId) {
    const response = await api.get(`/corporate/organizations/${organizationId}/roles/`)
    return response.data
  }

  // Notifications and Alerts
  async getNotifications(params = {}) {
    const response = await api.get('/corporate/notifications/', { params })
    return response.data
  }

  async markNotificationRead(id) {
    const response = await api.put(`/corporate/notifications/${id}/read/`)
    return response.data
  }

  async createAlert(data) {
    const response = await api.post('/corporate/alerts/', data)
    return response.data
  }

  async getAlerts(params = {}) {
    const response = await api.get('/corporate/alerts/', { params })
    return response.data
  }

  // Integration Management
  async getIntegrations() {
    const response = await api.get('/corporate/integrations/')
    return response.data
  }

  async configureIntegration(type, config) {
    const response = await api.post(`/corporate/integrations/${type}/`, config)
    return response.data
  }

  async testIntegration(type, config) {
    const response = await api.post(`/corporate/integrations/${type}/test/`, config)
    return response.data
  }

  // SSO Configuration
  async getSSOConfig() {
    const response = await api.get('/corporate/sso/config/')
    return response.data
  }

  async updateSSOConfig(data) {
    const response = await api.put('/corporate/sso/config/', data)
    return response.data
  }

  async testSSOConnection() {
    const response = await api.post('/corporate/sso/test/')
    return response.data
  }
}

export const enterpriseService = new EnterpriseService()