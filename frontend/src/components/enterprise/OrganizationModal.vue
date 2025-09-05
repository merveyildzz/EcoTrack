<template>
  <div v-if="show" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full max-w-md">
      <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
        <h3 class="text-lg font-medium text-gray-900 dark:text-white">
          {{ organization ? 'Edit Organization' : 'Create Organization' }}
        </h3>
      </div>
      
      <form @submit.prevent="handleSubmit" class="p-6 space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Organization Name *
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
            Domain *
          </label>
          <input
            v-model="formData.domain"
            type="text"
            required
            class="w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 dark:bg-gray-700 dark:border-gray-600"
          />
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Industry
          </label>
          <input
            v-model="formData.industry"
            type="text"
            class="w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 dark:bg-gray-700 dark:border-gray-600"
          />
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Company Size
          </label>
          <select
            v-model="formData.size"
            class="w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 dark:bg-gray-700 dark:border-gray-600"
          >
            <option value="">Select size</option>
            <option value="1-10">1-10 employees</option>
            <option value="11-50">11-50 employees</option>
            <option value="51-200">51-200 employees</option>
            <option value="201-1000">201-1000 employees</option>
            <option value="1000+">1000+ employees</option>
          </select>
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Plan
          </label>
          <select
            v-model="formData.plan"
            class="w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 dark:bg-gray-700 dark:border-gray-600"
          >
            <option value="basic">Basic</option>
            <option value="professional">Professional</option>
            <option value="enterprise">Enterprise</option>
          </select>
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
            class="px-4 py-2 text-sm font-medium text-white bg-green-600 border border-transparent rounded-md hover:bg-green-700"
          >
            {{ organization ? 'Update' : 'Create' }}
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
  name: 'OrganizationModal',
  props: {
    show: Boolean,
    organization: Object
  },
  emits: ['close', 'created', 'updated'],
  setup(props, { emit }) {
    const { showToast } = useToast()
    
    const formData = ref({
      name: '',
      domain: '',
      industry: '',
      size: '',
      plan: 'basic',
      is_active: true
    })

    const resetForm = () => {
      if (props.organization) {
        formData.value = { ...props.organization }
      } else {
        formData.value = {
          name: '',
          domain: '',
          industry: '',
          size: '',
          plan: 'basic',
          is_active: true
        }
      }
    }

    const handleSubmit = async () => {
      try {
        if (props.organization) {
          const updated = await enterpriseService.updateOrganization(
            props.organization.id,
            formData.value
          )
          emit('updated', updated)
        } else {
          const created = await enterpriseService.createOrganization(formData.value)
          emit('created', created)
        }
      } catch (error) {
        console.error('Error saving organization:', error)
        showToast('Failed to save organization', 'error')
      }
    }

    watch(() => props.show, (show) => {
      if (show) {
        resetForm()
      }
    })

    return {
      formData,
      handleSubmit
    }
  }
}
</script>