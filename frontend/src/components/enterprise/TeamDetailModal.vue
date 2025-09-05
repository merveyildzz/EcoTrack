<template>
  <div v-if="show" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full max-w-4xl max-h-[90vh] overflow-hidden">
      <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
        <div class="flex justify-between items-center">
          <div>
            <h3 class="text-lg font-medium text-gray-900 dark:text-white">
              {{ team?.name }} Details
            </h3>
            <p class="text-sm text-gray-500 dark:text-gray-400">
              {{ team?.organization?.name }}
            </p>
          </div>
          <button
            @click="$emit('close')"
            class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
          >
            <XIcon class="h-6 w-6" />
          </button>
        </div>
      </div>
      
      <div class="overflow-y-auto max-h-[calc(90vh-120px)]">
        <div class="p-6">
          <!-- Team Info -->
          <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
            <div class="bg-green-50 dark:bg-green-900 p-4 rounded-lg">
              <div class="text-2xl font-semibold text-green-600">
                {{ team?.member_count || 0 }}
              </div>
              <div class="text-sm text-green-700 dark:text-green-300">Members</div>
            </div>
            <div class="bg-blue-50 dark:bg-blue-900 p-4 rounded-lg">
              <div class="text-2xl font-semibold text-blue-600">
                {{ (team?.total_co2_saved || 0).toFixed(1) }}kg
              </div>
              <div class="text-sm text-blue-700 dark:text-blue-300">CO₂ Saved</div>
            </div>
            <div class="bg-purple-50 dark:bg-purple-900 p-4 rounded-lg">
              <div class="text-2xl font-semibold text-purple-600">
                {{ team?.total_activities || 0 }}
              </div>
              <div class="text-sm text-purple-700 dark:text-purple-300">Activities</div>
            </div>
          </div>

          <!-- Team Members -->
          <div class="mb-8">
            <div class="flex justify-between items-center mb-4">
              <h4 class="text-lg font-medium text-gray-900 dark:text-white">
                Team Members
              </h4>
              <button
                @click="showAddMember = true"
                class="px-3 py-1 text-sm bg-green-600 text-white rounded-md hover:bg-green-700"
              >
                Add Member
              </button>
            </div>
            
            <div class="bg-white dark:bg-gray-800 shadow overflow-hidden sm:rounded-lg">
              <div class="overflow-x-auto">
                <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                  <thead class="bg-gray-50 dark:bg-gray-700">
                    <tr>
                      <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">
                        Member
                      </th>
                      <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">
                        Role
                      </th>
                      <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">
                        CO₂ Saved
                      </th>
                      <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">
                        Joined
                      </th>
                      <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                    <tr
                      v-for="member in teamMembers"
                      :key="member.id"
                      class="hover:bg-gray-50 dark:hover:bg-gray-700"
                    >
                      <td class="px-6 py-4 whitespace-nowrap">
                        <div class="flex items-center">
                          <img
                            v-if="member.user.avatar"
                            :src="member.user.avatar"
                            :alt="member.user.name"
                            class="h-8 w-8 rounded-full"
                          />
                          <div
                            v-else
                            class="h-8 w-8 rounded-full bg-blue-500 flex items-center justify-center"
                          >
                            <span class="text-white text-xs font-medium">
                              {{ member.user.first_name?.charAt(0) || 'U' }}
                            </span>
                          </div>
                          <div class="ml-3">
                            <div class="text-sm font-medium text-gray-900 dark:text-white">
                              {{ member.user.full_name }}
                            </div>
                            <div class="text-sm text-gray-500 dark:text-gray-400">
                              {{ member.user.email }}
                            </div>
                          </div>
                        </div>
                      </td>
                      <td class="px-6 py-4 whitespace-nowrap">
                        <span
                          :class="[
                            'inline-flex px-2 py-1 text-xs font-semibold rounded-full',
                            member.role === 'lead'
                              ? 'bg-purple-100 text-purple-800 dark:bg-purple-800 dark:text-purple-100'
                              : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
                          ]"
                        >
                          {{ member.role }}
                        </span>
                      </td>
                      <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                        {{ (member.co2_saved || 0).toFixed(1) }}kg
                      </td>
                      <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                        {{ formatDate(member.joined_at) }}
                      </td>
                      <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <button
                          @click="removeMember(member)"
                          class="text-red-600 hover:text-red-900 dark:text-red-400"
                        >
                          Remove
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <!-- Recent Activities -->
          <div>
            <h4 class="text-lg font-medium text-gray-900 dark:text-white mb-4">
              Recent Activities
            </h4>
            <div class="space-y-3">
              <div
                v-for="activity in recentActivities"
                :key="activity.id"
                class="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg"
              >
                <div class="flex justify-between items-start">
                  <div>
                    <div class="font-medium text-gray-900 dark:text-white">
                      {{ activity.activity_type }}
                    </div>
                    <div class="text-sm text-gray-600 dark:text-gray-400">
                      by {{ activity.user.full_name }}
                    </div>
                  </div>
                  <div class="text-right">
                    <div class="text-green-600 font-medium">
                      {{ activity.co2_kg.toFixed(1) }}kg saved
                    </div>
                    <div class="text-sm text-gray-500">
                      {{ formatDate(activity.created_at) }}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, watch } from 'vue'
import { XIcon } from '@heroicons/vue/outline'
import { enterpriseService } from '@/services/enterprise'
import { useToast } from '@/composables/useToast'

export default {
  name: 'TeamDetailModal',
  props: {
    show: Boolean,
    team: Object
  },
  emits: ['close'],
  setup(props) {
    const { showToast } = useToast()
    
    const teamMembers = ref([])
    const recentActivities = ref([])
    const showAddMember = ref(false)

    const loadTeamDetails = async () => {
      if (!props.team?.id) return

      try {
        // Load team members
        const members = await enterpriseService.getTeamMembers(props.team.id)
        teamMembers.value = members.results || members

        // Load recent activities (placeholder)
        recentActivities.value = []
      } catch (error) {
        console.error('Error loading team details:', error)
      }
    }

    const removeMember = async (member) => {
      if (!confirm('Are you sure you want to remove this member from the team?')) return

      try {
        await enterpriseService.removeTeamMember(props.team.id, member.user.id)
        teamMembers.value = teamMembers.value.filter(m => m.id !== member.id)
        showToast('Member removed successfully', 'success')
      } catch (error) {
        showToast('Failed to remove member', 'error')
      }
    }

    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString()
    }

    watch(() => props.show, (show) => {
      if (show && props.team) {
        loadTeamDetails()
      }
    })

    return {
      teamMembers,
      recentActivities,
      showAddMember,
      removeMember,
      formatDate,
      XIcon
    }
  }
}
</script>
</template>