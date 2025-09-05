<template>
  <div v-if="show" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full max-w-md">
      <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
        <h3 class="text-lg font-medium text-gray-900 dark:text-white">
          {{ team ? 'Edit Team' : 'Create Team' }}
        </h3>
      </div>
      
      <form @submit.prevent="handleSubmit" class="p-6 space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Team Name *
          </label>
          <input
            v-model="formData.name"
            type="text"
            required
            class="w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 dark:bg-gray-700 dark:border-gray-600"
          />
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Description
          </label>
          <textarea
            v-model="formData.description"
            rows="3"
            class="w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 dark:bg-gray-700 dark:border-gray-600"
          ></textarea>
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Organization *
          </label>
          <select
            v-model="formData.organization_id"
            required
            :disabled="!!team"
            class="w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 dark:bg-gray-700 dark:border-gray-600 disabled:bg-gray-100 disabled:cursor-not-allowed"
          >
            <option value="">Select organization</option>
            <option
              v-for="org in organizations"
              :key="org.id"
              :value="org.id"
            >
              {{ org.name }}
            </option>
          </select>
        </div>
        
        <div class="flex items-center">
          <input
            v-model="formData.is_active"
            type="checkbox"
            class="h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300 rounded"
          />
          <label class="ml-2 block text-sm text-gray-700 dark:text-gray-300">
            Active
          </label>
        </div>
        
        <div class="flex justify-end space-x-3 pt-4">
          <button
            type="button"
            @click="$emit('close')"
            class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
          >
            Cancel
          </button>
          <button
            type="submit"
            :disabled="loading"
            class="px-4 py-2 text-sm font-medium text-white bg-green-600 border border-transparent rounded-md hover:bg-green-700 disabled:opacity-50"
          >
            {{ loading ? 'Saving...' : team ? 'Update' : 'Create' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import { ref, watch } from 'vue'
import { enterpriseService } from '@/services/enterprise'
import { useToast } from '@/composables/useToast'

export default {
  name: 'TeamModal',
  props: {
    show: Boolean,
    team: Object,
    organizations: Array
  },
  emits: ['close', 'created', 'updated'],
  setup(props, { emit }) {
    const { showToast } = useToast()
    const loading = ref(false)
    
    const formData = ref({
      name: '',
      description: '',
      organization_id: '',
      is_active: true
    })

    const resetForm = () => {
      if (props.team) {
        formData.value = {
          name: props.team.name || '',
          description: props.team.description || '',
          organization_id: props.team.organization?.id || '',
          is_active: props.team.is_active !== undefined ? props.team.is_active : true
        }
      } else {
        formData.value = {
          name: '',
          description: '',
          organization_id: '',
          is_active: true
        }
      }
    }

    const handleSubmit = async () => {
      try {
        loading.value = true
        if (props.team) {
          const updated = await enterpriseService.updateTeam(props.team.id, formData.value)
          emit('updated', updated)
        } else {
          const created = await enterpriseService.createTeam(formData.value)
          emit('created', created)
        }
      } catch (error) {
        console.error('Error saving team:', error)
        showToast('Failed to save team', 'error')
      } finally {
        loading.value = false
      }
    }

    watch(() => props.show, (show) => {
      if (show) {
        resetForm()
      }
    })

    return {
      formData,
      loading,
      handleSubmit
    }
  }
}
</script>