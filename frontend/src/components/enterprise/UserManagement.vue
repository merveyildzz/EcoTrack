<template>
  <div class="space-y-6">
    <!-- Header with Actions -->
    <div class="sm:flex sm:items-center sm:justify-between">
      <div>
        <h2 class="text-2xl font-bold text-gray-900 dark:text-white">User Management</h2>
        <p class="mt-2 text-sm text-gray-700 dark:text-gray-300">
          Manage users across all organizations
        </p>
      </div>
      <div class="mt-4 sm:mt-0 sm:flex sm:space-x-3">
        <button
          @click="showInviteModal = true"
          class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700"
        >
          <UserAddIcon class="h-4 w-4 mr-2" />
          Invite User
        </button>
        <button
          @click="showBulkImportModal = true"
          class="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 dark:bg-gray-800 dark:text-gray-300 dark:border-gray-600"
        >
          <UploadIcon class="h-4 w-4 mr-2" />
          Bulk Import
        </button>
        <button
          @click="exportUsers"
          class="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 dark:bg-gray-800 dark:text-gray-300 dark:border-gray-600"
        >
          <DownloadIcon class="h-4 w-4 mr-2" />
          Export
        </button>
      </div>
    </div>

    <!-- Filters and Search -->
    <div class="bg-white dark:bg-gray-800 shadow rounded-lg">
      <div class="p-4 border-b border-gray-200 dark:border-gray-700">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div>
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search users..."
              class="block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 dark:bg-gray-700 dark:border-gray-600"
            />
          </div>
          <div>
            <select
              v-model="selectedOrganization"
              class="block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 dark:bg-gray-700 dark:border-gray-600"
            >
              <option value="">All Organizations</option>
              <option
                v-for="org in organizations"
                :key="org.id"
                :value="org.id"
              >
                {{ org.name }}
              </option>
            </select>
          </div>
          <div>
            <select
              v-model="selectedRole"
              class="block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 dark:bg-gray-700 dark:border-gray-600"
            >
              <option value="">All Roles</option>
              <option value="admin">Admin</option>
              <option value="manager">Manager</option>
              <option value="member">Member</option>
            </select>
          </div>
          <div>
            <select
              v-model="selectedStatus"
              class="block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 dark:bg-gray-700 dark:border-gray-600"
            >
              <option value="">All Status</option>
              <option value="active">Active</option>
              <option value="invited">Invited</option>
              <option value="suspended">Suspended</option>
            </select>
          </div>
        </div>
      </div>
    </div>

    <!-- Users Table -->
    <div class="bg-white dark:bg-gray-800 shadow overflow-hidden sm:rounded-lg">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead class="bg-gray-50 dark:bg-gray-700">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                User
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                Organization
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                Role
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                Team
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                Status
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                Last Login
              </th>
              <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
            <tr
              v-for="user in filteredUsers"
              :key="user.id"
              class="hover:bg-gray-50 dark:hover:bg-gray-700"
            >
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <img
                    v-if="user.avatar"
                    :src="user.avatar"
                    :alt="user.full_name"
                    class="h-10 w-10 rounded-full"
                  />
                  <div
                    v-else
                    class="h-10 w-10 rounded-full bg-blue-500 flex items-center justify-center"
                  >
                    <span class="text-white font-medium">
                      {{ user.first_name?.charAt(0) || user.email.charAt(0).toUpperCase() }}
                    </span>
                  </div>
                  <div class="ml-4">
                    <div class="text-sm font-medium text-gray-900 dark:text-white">
                      {{ user.full_name || `${user.first_name} ${user.last_name}` }}
                    </div>
                    <div class="text-sm text-gray-500 dark:text-gray-400">
                      {{ user.email }}
                    </div>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-900 dark:text-white">
                  {{ user.organization?.name || 'N/A' }}
                </div>
                <div class="text-sm text-gray-500 dark:text-gray-400">
                  {{ user.job_title || user.department }}
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span
                  :class="[
                    'inline-flex px-2 py-1 text-xs font-semibold rounded-full',
                    user.role === 'admin'
                      ? 'bg-red-100 text-red-800 dark:bg-red-800 dark:text-red-100'
                      : user.role === 'manager'
                      ? 'bg-blue-100 text-blue-800 dark:bg-blue-800 dark:text-blue-100'
                      : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
                  ]"
                >
                  {{ user.role }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                {{ user.teams?.map(t => t.name).join(', ') || 'No team' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span
                  :class="[
                    'inline-flex px-2 py-1 text-xs font-semibold rounded-full',
                    user.status === 'active'
                      ? 'bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-100'
                      : user.status === 'invited'
                      ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-800 dark:text-yellow-100'
                      : 'bg-red-100 text-red-800 dark:bg-red-800 dark:text-red-100'
                  ]"
                >
                  {{ user.status }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                {{ user.last_login ? formatDate(user.last_login) : 'Never' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <div class="flex justify-end space-x-2">
                  <button
                    @click="viewUser(user)"
                    class="text-green-600 hover:text-green-900 dark:text-green-400"
                  >
                    View
                  </button>
                  <button
                    @click="editUser(user)"
                    class="text-blue-600 hover:text-blue-900 dark:text-blue-400"
                  >
                    Edit
                  </button>
                  <button
                    v-if="user.status === 'invited'"
                    @click="resendInvite(user)"
                    class="text-purple-600 hover:text-purple-900 dark:text-purple-400"
                  >
                    Resend
                  </button>
                  <button
                    @click="toggleUserStatus(user)"
                    :class="[
                      user.status === 'active'
                        ? 'text-red-600 hover:text-red-900 dark:text-red-400'
                        : 'text-green-600 hover:text-green-900 dark:text-green-400'
                    ]"
                  >
                    {{ user.status === 'active' ? 'Suspend' : 'Activate' }}
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Pagination -->
    <div class="bg-white dark:bg-gray-800 px-4 py-3 border-t border-gray-200 dark:border-gray-700 sm:px-6">
      <div class="flex items-center justify-between">
        <div class="text-sm text-gray-700 dark:text-gray-300">
          Showing {{ (currentPage - 1) * itemsPerPage + 1 }} to 
          {{ Math.min(currentPage * itemsPerPage, totalItems) }} of {{ totalItems }} results
        </div>
        <div class="flex space-x-1">
          <button
            @click="currentPage--"
            :disabled="currentPage === 1"
            class="px-3 py-2 text-sm border rounded-l-md disabled:opacity-50"
          >
            Previous
          </button>
          <button
            @click="currentPage++"
            :disabled="currentPage * itemsPerPage >= totalItems"
            class="px-3 py-2 text-sm border rounded-r-md disabled:opacity-50"
          >
            Next
          </button>
        </div>
      </div>
    </div>

    <!-- Invite User Modal -->
    <UserInviteModal
      v-if="showInviteModal"
      :show="showInviteModal"
      :organizations="organizations"
      @close="showInviteModal = false"
      @invited="onUserInvited"
    />

    <!-- Edit User Modal -->
    <UserEditModal
      v-if="showEditModal"
      :show="showEditModal"
      :user="selectedUser"
      :organizations="organizations"
      @close="showEditModal = false"
      @updated="onUserUpdated"
    />

    <!-- Bulk Import Modal -->
    <BulkImportModal
      v-if="showBulkImportModal"
      :show="showBulkImportModal"
      type="users"
      @close="showBulkImportModal = false"
      @imported="onBulkImported"
    />
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { UserAddIcon, UploadIcon, DownloadIcon } from '@heroicons/vue/outline'
import UserInviteModal from './UserInviteModal.vue'
import UserEditModal from './UserEditModal.vue'
import BulkImportModal from './BulkImportModal.vue'
import { enterpriseService } from '@/services/enterprise'
import { useToast } from '@/composables/useToast'

export default {
  name: 'UserManagement',
  components: {
    UserInviteModal,
    UserEditModal,
    BulkImportModal
  },
  setup() {
    const { showToast } = useToast()
    
    const users = ref([])
    const organizations = ref([])
    const searchQuery = ref('')
    const selectedOrganization = ref('')
    const selectedRole = ref('')
    const selectedStatus = ref('')
    const currentPage = ref(1)
    const itemsPerPage = ref(10)
    const totalItems = ref(0)
    const loading = ref(false)
    
    const showInviteModal = ref(false)
    const showEditModal = ref(false)
    const showBulkImportModal = ref(false)
    const selectedUser = ref(null)

    const filteredUsers = computed(() => {
      let filtered = users.value

      if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase()
        filtered = filtered.filter(user =>
          user.email.toLowerCase().includes(query) ||
          user.first_name?.toLowerCase().includes(query) ||
          user.last_name?.toLowerCase().includes(query)
        )
      }

      if (selectedOrganization.value) {
        filtered = filtered.filter(user => 
          user.organization?.id === selectedOrganization.value
        )
      }

      if (selectedRole.value) {
        filtered = filtered.filter(user => user.role === selectedRole.value)
      }

      if (selectedStatus.value) {
        filtered = filtered.filter(user => user.status === selectedStatus.value)
      }

      totalItems.value = filtered.length
      return filtered.slice(
        (currentPage.value - 1) * itemsPerPage.value,
        currentPage.value * itemsPerPage.value
      )
    })

    const loadUsers = async () => {
      try {
        loading.value = true
        const response = await enterpriseService.getUsers({
          page: currentPage.value,
          limit: itemsPerPage.value
        })
        users.value = response.results || response
        totalItems.value = response.count || response.length
      } catch (error) {
        console.error('Error loading users:', error)
        showToast('Failed to load users', 'error')
      } finally {
        loading.value = false
      }
    }

    const loadOrganizations = async () => {
      try {
        const response = await enterpriseService.getOrganizations()
        organizations.value = response.results || response
      } catch (error) {
        console.error('Error loading organizations:', error)
      }
    }

    const viewUser = (user) => {
      console.log('View user:', user)
    }

    const editUser = (user) => {
      selectedUser.value = user
      showEditModal.value = true
    }

    const toggleUserStatus = async (user) => {
      try {
        const newStatus = user.status === 'active' ? 'suspended' : 'active'
        await enterpriseService.updateUser(user.id, { status: newStatus })
        user.status = newStatus
        showToast(
          `User ${newStatus === 'active' ? 'activated' : 'suspended'} successfully`,
          'success'
        )
      } catch (error) {
        showToast('Failed to update user status', 'error')
      }
    }

    const resendInvite = async (user) => {
      try {
        await enterpriseService.resendInvite(user.id)
        showToast('Invitation sent successfully', 'success')
      } catch (error) {
        showToast('Failed to resend invitation', 'error')
      }
    }

    const exportUsers = async () => {
      try {
        const blob = await enterpriseService.exportUsers({
          organization: selectedOrganization.value,
          role: selectedRole.value,
          status: selectedStatus.value
        })
        
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `users-export-${new Date().toISOString().split('T')[0]}.csv`
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        window.URL.revokeObjectURL(url)
        
        showToast('Users exported successfully', 'success')
      } catch (error) {
        showToast('Failed to export users', 'error')
      }
    }

    const onUserInvited = (newUser) => {
      users.value.unshift(newUser)
      showInviteModal.value = false
      showToast('User invited successfully', 'success')
    }

    const onUserUpdated = (updatedUser) => {
      const index = users.value.findIndex(user => user.id === updatedUser.id)
      if (index !== -1) {
        users.value[index] = updatedUser
      }
      showEditModal.value = false
      showToast('User updated successfully', 'success')
    }

    const onBulkImported = (results) => {
      loadUsers()
      showBulkImportModal.value = false
      showToast(`Bulk import completed: ${results.success} successful, ${results.errors} errors`, 'info')
    }

    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString()
    }

    watch([searchQuery, selectedOrganization, selectedRole, selectedStatus], () => {
      currentPage.value = 1
    })

    onMounted(() => {
      loadUsers()
      loadOrganizations()
    })

    return {
      users,
      organizations,
      searchQuery,
      selectedOrganization,
      selectedRole,
      selectedStatus,
      currentPage,
      itemsPerPage,
      totalItems,
      loading,
      showInviteModal,
      showEditModal,
      showBulkImportModal,
      selectedUser,
      filteredUsers,
      viewUser,
      editUser,
      toggleUserStatus,
      resendInvite,
      exportUsers,
      onUserInvited,
      onUserUpdated,
      onBulkImported,
      formatDate,
      UserAddIcon,
      UploadIcon,
      DownloadIcon
    }
  }
}
</script>
</template>