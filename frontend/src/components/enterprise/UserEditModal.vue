<template>
  <div v-if="show" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full max-w-md">
      <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
        <h3 class="text-lg font-medium text-gray-900 dark:text-white">
          Edit User
        </h3>
      </div>
      
      <form @submit.prevent="handleSubmit" class="p-6 space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Email Address
          </label>
          <input
            v-model="formData.email"
            type="email"
            disabled
            class="w-full border-gray-300 rounded-md shadow-sm bg-gray-100 dark:bg-gray-600 dark:border-gray-600"
          />
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Role
          </label>
          <select
            v-model="formData.role"
            class="w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 dark:bg-gray-700 dark:border-gray-600"
          >
            <option value="member">Member</option>
            <option value="manager">Manager</option>
            <option value="admin">Admin</option>
          </select>
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Status
          </label>
          <select
            v-model="formData.status"
            class="w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 dark:bg-gray-700 dark:border-gray-600"
          >
            <option value="active">Active</option>
            <option value="suspended">Suspended</option>
            <option value="invited">Invited</option>
          </select>
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Job Title
          </label>
          <input
            v-model="formData.job_title"
            type="text"
            class="w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 dark:bg-gray-700 dark:border-gray-600"
          />
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Department
          </label>
          <input
            v-model="formData.department"
            type="text"
            class="w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 dark:bg-gray-700 dark:border-gray-600"
          />
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
            {{ loading ? 'Updating...' : 'Update User' }}
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
  name: 'UserEditModal',
  props: {
    show: Boolean,
    user: Object,
    organizations: Array
  },
  emits: ['close', 'updated'],
  setup(props, { emit }) {
    const { showToast } = useToast()
    const loading = ref(false)
    
    const formData = ref({
      email: '',
      role: 'member',
      status: 'active',
      job_title: '',
      department: ''
    })

    const resetForm = () => {
      if (props.user) {
        formData.value = {
          email: props.user.email || '',
          role: props.user.role || 'member',
          status: props.user.status || 'active',
          job_title: props.user.job_title || '',
          department: props.user.department || ''
        }
      }
    }

    const handleSubmit = async () => {
      try {
        loading.value = true
        const updated = await enterpriseService.updateUser(props.user.id, formData.value)
        emit('updated', updated)
      } catch (error) {
        console.error('Error updating user:', error)
        showToast('Failed to update user', 'error')
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
</template>