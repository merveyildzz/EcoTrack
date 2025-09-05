<template>
  <div class="space-y-6">
    <!-- Header with Actions -->
    <div class="sm:flex sm:items-center sm:justify-between">
      <div>
        <h2 class="text-2xl font-bold text-gray-900 dark:text-white">Team Management</h2>
        <p class="mt-2 text-sm text-gray-700 dark:text-gray-300">
          Manage teams across all organizations
        </p>
      </div>
      <div class="mt-4 sm:mt-0 sm:flex sm:space-x-3">
        <button
          @click="showCreateModal = true"
          class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700"
        >
          <PlusIcon class="h-4 w-4 mr-2" />
          New Team
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
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search teams..."
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

    <!-- Teams Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div
        v-for="team in filteredTeams"
        :key="team.id"
        class="bg-white dark:bg-gray-800 shadow rounded-lg overflow-hidden hover:shadow-lg transition-shadow"
      >
        <!-- Team Header -->
        <div class="p-6 border-b border-gray-200 dark:border-gray-700">
          <div class="flex items-center justify-between">
            <div>
              <h3 class="text-lg font-medium text-gray-900 dark:text-white">
                {{ team.name }}
              </h3>
              <p class="text-sm text-gray-500 dark:text-gray-400">
                {{ team.organization?.name }}
              </p>
            </div>
            <div class="flex space-x-2">
              <span
                :class="[
                  'inline-flex px-2 py-1 text-xs font-semibold rounded-full',
                  team.is_active
                    ? 'bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-100'
                    : 'bg-red-100 text-red-800 dark:bg-red-800 dark:text-red-100'
                ]"
              >
                {{ team.is_active ? 'Active' : 'Inactive' }}
              </span>
            </div>
          </div>
          
          <p v-if="team.description" class="mt-2 text-sm text-gray-600 dark:text-gray-400">
            {{ team.description }}
          </p>
        </div>

        <!-- Team Stats -->
        <div class="p-6">
          <div class="grid grid-cols-2 gap-4 mb-4">
            <div class="text-center">
              <div class="text-2xl font-semibold text-gray-900 dark:text-white">
                {{ team.member_count || 0 }}
              </div>
              <div class="text-sm text-gray-500 dark:text-gray-400">Members</div>
            </div>
            <div class="text-center">
              <div class="text-2xl font-semibold text-green-600">
                {{ (team.total_co2_saved || 0).toFixed(1) }}kg
              </div>
              <div class="text-sm text-gray-500 dark:text-gray-400">CO₂ Saved</div>
            </div>
          </div>

          <!-- Team Manager -->
          <div v-if="team.manager" class="flex items-center mb-4">
            <img
              v-if="team.manager.avatar"
              :src="team.manager.avatar"
              :alt="team.manager.name"
              class="h-8 w-8 rounded-full"
            />
            <div
              v-else
              class="h-8 w-8 rounded-full bg-blue-500 flex items-center justify-center"
            >
              <span class="text-white text-xs font-medium">
                {{ team.manager.first_name?.charAt(0) || 'M' }}
              </span>
            </div>
            <div class="ml-3">
              <p class="text-sm font-medium text-gray-900 dark:text-white">
                {{ team.manager.full_name }}
              </p>
              <p class="text-xs text-gray-500 dark:text-gray-400">Team Manager</p>
            </div>
          </div>

          <!-- Recent Activities -->
          <div class="mb-4">
            <h4 class="text-sm font-medium text-gray-900 dark:text-white mb-2">
              Recent Activities
            </h4>
            <div v-if="team.recent_activities?.length" class="space-y-2">
              <div
                v-for="activity in team.recent_activities.slice(0, 3)"
                :key="activity.id"
                class="flex items-center text-sm"
              >
                <div class="w-2 h-2 bg-green-400 rounded-full mr-2"></div>
                <span class="text-gray-600 dark:text-gray-400 truncate">
                  {{ activity.activity_type }} - {{ activity.co2_kg.toFixed(1) }}kg saved
                </span>
              </div>
            </div>
            <div v-else class="text-sm text-gray-500 dark:text-gray-400">
              No recent activities
            </div>
          </div>

          <!-- Actions -->
          <div class="flex justify-between items-center pt-4 border-t border-gray-200 dark:border-gray-700">
            <button
              @click="viewTeam(team)"
              class="text-sm text-green-600 hover:text-green-900 dark:text-green-400"
            >
              View Details
            </button>
            <div class="flex space-x-2">
              <button
                @click="editTeam(team)"
                class="text-sm text-blue-600 hover:text-blue-900 dark:text-blue-400"
              >
                Edit
              </button>
              <button
                @click="toggleTeamStatus(team)"
                :class="[
                  'text-sm',
                  team.is_active
                    ? 'text-red-600 hover:text-red-900 dark:text-red-400'
                    : 'text-green-600 hover:text-green-900 dark:text-green-400'
                ]"
              >
                {{ team.is_active ? 'Deactivate' : 'Activate' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Pagination -->
    <div class="bg-white dark:bg-gray-800 px-4 py-3 border-t border-gray-200 dark:border-gray-700 sm:px-6 rounded-lg">
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

    <!-- Create Team Modal -->
    <TeamModal
      v-if="showCreateModal"
      :show="showCreateModal"
      :organizations="organizations"
      @close="showCreateModal = false"
      @created="onTeamCreated"
    />

    <!-- Edit Team Modal -->
    <TeamModal
      v-if="showEditModal"
      :show="showEditModal"
      :team="selectedTeam"
      :organizations="organizations"
      @close="showEditModal = false"
      @updated="onTeamUpdated"
    />

    <!-- Team Detail Modal -->
    <TeamDetailModal
      v-if="showDetailModal"
      :show="showDetailModal"
      :team="selectedTeam"
      @close="showDetailModal = false"
    />

    <!-- Bulk Import Modal -->
    <BulkImportModal
      v-if="showBulkImportModal"
      :show="showBulkImportModal"
      type="teams"
      @close="showBulkImportModal = false"
      @imported="onBulkImported"
    />
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { PlusIcon, ArrowUpTrayIcon as UploadIcon } from '@heroicons/vue/24/outline'
import TeamModal from './TeamModal.vue'
import TeamDetailModal from './TeamDetailModal.vue'
import BulkImportModal from './BulkImportModal.vue'
import { enterpriseService } from '@/services/enterprise'
import { useToast } from '@/composables/useToast'

export default {
  name: 'TeamManagement',
  components: {
    TeamModal,
    TeamDetailModal,
    BulkImportModal,
    PlusIcon,
    UploadIcon
  },
  setup() {
    const { showToast } = useToast()
    
    const teams = ref([])
    const organizations = ref([])
    const searchQuery = ref('')
    const selectedOrganization = ref('')
    const selectedStatus = ref('')
    const currentPage = ref(1)
    const itemsPerPage = ref(9) // 3x3 grid
    const totalItems = ref(0)
    const loading = ref(false)
    
    const showCreateModal = ref(false)
    const showEditModal = ref(false)
    const showDetailModal = ref(false)
    const showBulkImportModal = ref(false)
    const selectedTeam = ref(null)

    const filteredTeams = computed(() => {
      let filtered = teams.value

      if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase()
        filtered = filtered.filter(team =>
          team.name.toLowerCase().includes(query) ||
          team.description?.toLowerCase().includes(query) ||
          team.organization?.name.toLowerCase().includes(query)
        )
      }

      if (selectedOrganization.value) {
        filtered = filtered.filter(team => 
          team.organization?.id === selectedOrganization.value
        )
      }

      if (selectedStatus.value !== '') {
        const isActive = selectedStatus.value === 'true'
        filtered = filtered.filter(team => team.is_active === isActive)
      }

      totalItems.value = filtered.length
      return filtered.slice(
        (currentPage.value - 1) * itemsPerPage.value,
        currentPage.value * itemsPerPage.value
      )
    })

    const loadTeams = async () => {
      try {
        loading.value = true
        const response = await enterpriseService.getTeams({
          page: currentPage.value,
          limit: itemsPerPage.value
        })
        teams.value = response.results || response
        totalItems.value = response.count || response.length
      } catch (error) {
        console.error('Error loading teams:', error)
        showToast('Failed to load teams', 'error')
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

    const viewTeam = (team) => {
      selectedTeam.value = team
      showDetailModal.value = true
    }

    const editTeam = (team) => {
      selectedTeam.value = team
      showEditModal.value = true
    }

    const toggleTeamStatus = async (team) => {
      try {
        await enterpriseService.updateTeam(team.id, {
          is_active: !team.is_active
        })
        team.is_active = !team.is_active
        showToast(
          `Team ${team.is_active ? 'activated' : 'deactivated'} successfully`,
          'success'
        )
      } catch (error) {
        showToast('Failed to update team status', 'error')
      }
    }

    const onTeamCreated = (newTeam) => {
      teams.value.unshift(newTeam)
      showCreateModal.value = false
      showToast('Team created successfully', 'success')
    }

    const onTeamUpdated = (updatedTeam) => {
      const index = teams.value.findIndex(team => team.id === updatedTeam.id)
      if (index !== -1) {
        teams.value[index] = updatedTeam
      }
      showEditModal.value = false
      showToast('Team updated successfully', 'success')
    }

    const onBulkImported = (results) => {
      loadTeams()
      showBulkImportModal.value = false
      showToast(`Bulk import completed: ${results.success} successful, ${results.errors} errors`, 'info')
    }

    watch([searchQuery, selectedOrganization, selectedStatus], () => {
      currentPage.value = 1
    })

    onMounted(() => {
      loadTeams()
      loadOrganizations()
    })

    return {
      teams,
      organizations,
      searchQuery,
      selectedOrganization,
      selectedStatus,
      currentPage,
      itemsPerPage,
      totalItems,
      loading,
      showCreateModal,
      showEditModal,
      showDetailModal,
      showBulkImportModal,
      selectedTeam,
      filteredTeams,
      viewTeam,
      editTeam,
      toggleTeamStatus,
      onTeamCreated,
      onTeamUpdated,
      onBulkImported,
      PlusIcon,
      UploadIcon
    }
  }
}
</script>