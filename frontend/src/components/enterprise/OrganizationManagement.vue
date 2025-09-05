<template>
  <div class="space-y-6">
    <!-- Header with Actions -->
    <div class="sm:flex sm:items-center sm:justify-between">
      <div>
        <h2 class="text-2xl font-bold text-gray-900 dark:text-white">Organizations</h2>
        <p class="mt-2 text-sm text-gray-700 dark:text-gray-300">
          Manage all organizations in your EcoTrack deployment
        </p>
      </div>
      <div class="mt-4 sm:mt-0 sm:flex sm:space-x-3">
        <button
          @click="showCreateModal = true"
          class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700"
        >
          <PlusIcon class="h-4 w-4 mr-2" />
          New Organization
        </button>
        <button
          @click="showBulkImportModal = true"
          class="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 dark:bg-gray-800 dark:text-gray-300 dark:border-gray-600"
        >
          <UploadIcon class="h-4 w-4 mr-2" />
          Bulk Import
        </button>
      </div>
    </div>

    <!-- Filters and Search -->
    <div class="bg-white dark:bg-gray-800 shadow rounded-lg">
      <div class="p-4 border-b border-gray-200 dark:border-gray-700">
        <div class="sm:flex sm:items-center sm:space-x-4">
          <div class="flex-1">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search organizations..."
              class="block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 dark:bg-gray-700 dark:border-gray-600"
            />
          </div>
          <div class="mt-3 sm:mt-0">
            <select
              v-model="selectedPlan"
              class="block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 dark:bg-gray-700 dark:border-gray-600"
            >
              <option value="">All Plans</option>
              <option value="basic">Basic</option>
              <option value="professional">Professional</option>
              <option value="enterprise">Enterprise</option>
            </select>
          </div>
          <div class="mt-3 sm:mt-0">
            <select
              v-model="selectedStatus"
              class="block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 dark:bg-gray-700 dark:border-gray-600"
            >
              <option value="">All Status</option>
              <option value="true">Active</option>
              <option value="false">Inactive</option>
            </select>
          </div>
        </div>
      </div>
    </div>

    <!-- Organizations Table -->
    <div class="bg-white dark:bg-gray-800 shadow overflow-hidden sm:rounded-lg">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead class="bg-gray-50 dark:bg-gray-700">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                Organization
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                Plan
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                Members
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                Teams
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                Status
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                Created
              </th>
              <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
            <tr
              v-for="org in filteredOrganizations"
              :key="org.id"
              class="hover:bg-gray-50 dark:hover:bg-gray-700"
            >
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <img
                    v-if="org.logo"
                    :src="org.logo"
                    :alt="org.name"
                    class="h-10 w-10 rounded-full"
                  />
                  <div
                    v-else
                    class="h-10 w-10 rounded-full bg-green-500 flex items-center justify-center"
                  >
                    <span class="text-white font-medium">
                      {{ org.name.charAt(0).toUpperCase() }}
                    </span>
                  </div>
                  <div class="ml-4">
                    <div class="text-sm font-medium text-gray-900 dark:text-white">
                      {{ org.name }}
                    </div>
                    <div class="text-sm text-gray-500 dark:text-gray-400">
                      {{ org.domain }}
                    </div>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span
                  :class="[
                    'inline-flex px-2 py-1 text-xs font-semibold rounded-full',
                    org.plan === 'enterprise'
                      ? 'bg-purple-100 text-purple-800 dark:bg-purple-800 dark:text-purple-100'
                      : org.plan === 'professional'
                      ? 'bg-blue-100 text-blue-800 dark:bg-blue-800 dark:text-blue-100'
                      : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
                  ]"
                >
                  {{ org.plan }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                {{ org.member_count || 0 }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                {{ org.team_count || 0 }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span
                  :class="[
                    'inline-flex px-2 py-1 text-xs font-semibold rounded-full',
                    org.is_active
                      ? 'bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-100'
                      : 'bg-red-100 text-red-800 dark:bg-red-800 dark:text-red-100'
                  ]"
                >
                  {{ org.is_active ? 'Active' : 'Inactive' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                {{ formatDate(org.created_at) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <div class="flex justify-end space-x-2">
                  <button
                    @click="viewOrganization(org)"
                    class="text-green-600 hover:text-green-900 dark:text-green-400"
                  >
                    View
                  </button>
                  <button
                    @click="editOrganization(org)"
                    class="text-blue-600 hover:text-blue-900 dark:text-blue-400"
                  >
                    Edit
                  </button>
                  <button
                    @click="toggleOrganizationStatus(org)"
                    :class="[
                      org.is_active
                        ? 'text-red-600 hover:text-red-900 dark:text-red-400'
                        : 'text-green-600 hover:text-green-900 dark:text-green-400'
                    ]"
                  >
                    {{ org.is_active ? 'Deactivate' : 'Activate' }}
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

    <!-- Create Organization Modal -->
    <OrganizationModal
      v-if="showCreateModal"
      :show="showCreateModal"
      @close="showCreateModal = false"
      @created="onOrganizationCreated"
    />

    <!-- Edit Organization Modal -->
    <OrganizationModal
      v-if="showEditModal"
      :show="showEditModal"
      :organization="selectedOrganization"
      @close="showEditModal = false"
      @updated="onOrganizationUpdated"
    />

    <!-- Bulk Import Modal -->
    <BulkImportModal
      v-if="showBulkImportModal"
      :show="showBulkImportModal"
      type="organizations"
      @close="showBulkImportModal = false"
      @imported="onBulkImported"
    />
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { PlusIcon, UploadIcon } from '@heroicons/vue/outline'
import OrganizationModal from './OrganizationModal.vue'
import BulkImportModal from './BulkImportModal.vue'
import { enterpriseService } from '@/services/enterprise'
import { useToast } from '@/composables/useToast'

export default {
  name: 'OrganizationManagement',
  components: {
    OrganizationModal,
    BulkImportModal
  },
  setup() {
    const { showToast } = useToast()
    
    const organizations = ref([])
    const searchQuery = ref('')
    const selectedPlan = ref('')
    const selectedStatus = ref('')
    const currentPage = ref(1)
    const itemsPerPage = ref(10)
    const totalItems = ref(0)
    const loading = ref(false)
    
    const showCreateModal = ref(false)
    const showEditModal = ref(false)
    const showBulkImportModal = ref(false)
    const selectedOrganization = ref(null)

    const filteredOrganizations = computed(() => {
      let filtered = organizations.value

      if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase()
        filtered = filtered.filter(org =>
          org.name.toLowerCase().includes(query) ||
          org.domain.toLowerCase().includes(query)
        )
      }

      if (selectedPlan.value) {
        filtered = filtered.filter(org => org.plan === selectedPlan.value)
      }

      if (selectedStatus.value !== '') {
        const isActive = selectedStatus.value === 'true'
        filtered = filtered.filter(org => org.is_active === isActive)
      }

      totalItems.value = filtered.length
      return filtered.slice(
        (currentPage.value - 1) * itemsPerPage.value,
        currentPage.value * itemsPerPage.value
      )
    })

    const loadOrganizations = async () => {
      try {
        loading.value = true
        const response = await enterpriseService.getOrganizations({
          page: currentPage.value,
          limit: itemsPerPage.value
        })
        organizations.value = response.results || response
        totalItems.value = response.count || response.length
      } catch (error) {
        console.error('Error loading organizations:', error)
        showToast('Failed to load organizations', 'error')
      } finally {
        loading.value = false
      }
    }

    const viewOrganization = (org) => {
      // Navigate to organization detail view
      console.log('View organization:', org)
    }

    const editOrganization = (org) => {
      selectedOrganization.value = org
      showEditModal.value = true
    }

    const toggleOrganizationStatus = async (org) => {
      try {
        await enterpriseService.updateOrganization(org.id, {
          is_active: !org.is_active
        })
        org.is_active = !org.is_active
        showToast(
          `Organization ${org.is_active ? 'activated' : 'deactivated'} successfully`,
          'success'
        )
      } catch (error) {
        showToast('Failed to update organization status', 'error')
      }
    }

    const onOrganizationCreated = (newOrg) => {
      organizations.value.unshift(newOrg)
      showCreateModal.value = false
      showToast('Organization created successfully', 'success')
    }

    const onOrganizationUpdated = (updatedOrg) => {
      const index = organizations.value.findIndex(org => org.id === updatedOrg.id)
      if (index !== -1) {
        organizations.value[index] = updatedOrg
      }
      showEditModal.value = false
      showToast('Organization updated successfully', 'success')
    }

    const onBulkImported = (results) => {
      loadOrganizations()
      showBulkImportModal.value = false
      showToast(`Bulk import completed: ${results.success} successful, ${results.errors} errors`, 'info')
    }

    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString()
    }

    watch([searchQuery, selectedPlan, selectedStatus], () => {
      currentPage.value = 1
    })

    onMounted(() => {
      loadOrganizations()
    })

    return {
      organizations,
      searchQuery,
      selectedPlan,
      selectedStatus,
      currentPage,
      itemsPerPage,
      totalItems,
      loading,
      showCreateModal,
      showEditModal,
      showBulkImportModal,
      selectedOrganization,
      filteredOrganizations,
      viewOrganization,
      editOrganization,
      toggleOrganizationStatus,
      onOrganizationCreated,
      onOrganizationUpdated,
      onBulkImported,
      formatDate,
      PlusIcon,
      UploadIcon
    }
  }
}
</script>
</template>