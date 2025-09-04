<template>
  <div class="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900">Log Activity</h1>
      <p class="mt-2 text-gray-600">Track your carbon footprint by logging a new activity</p>
    </div>

    <div class="card">
      <form @submit.prevent="handleSubmit" class="space-y-6">
        <!-- Category Selection -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Category *
          </label>
          <select 
            v-model="form.category" 
            @change="onCategoryChange"
            class="input-field" 
            required
          >
            <option value="">Select a category</option>
            <option 
              v-for="category in categories" 
              :key="category.id" 
              :value="category.id"
            >
              {{ category.name }}
            </option>
          </select>
          <div v-if="errors.category" class="mt-1 text-sm text-red-600">
            {{ errors.category[0] }}
          </div>
        </div>

        <!-- Activity Type -->
        <div v-if="form.category">
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Activity Type *
          </label>
          <select v-model="form.activity_type" class="input-field" required>
            <option value="">Select activity type</option>
            <option 
              v-for="template in filteredTemplates" 
              :key="template.id" 
              :value="template.activity_type"
              @click="selectTemplate(template)"
            >
              {{ template.name }}
            </option>
          </select>
          <div v-if="errors.activity_type" class="mt-1 text-sm text-red-600">
            {{ errors.activity_type[0] }}
          </div>
        </div>

        <!-- Value and Unit -->
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Value *
            </label>
            <input
              v-model.number="form.value"
              type="number"
              step="0.1"
              min="0"
              class="input-field"
              placeholder="0.0"
              required
            />
            <div v-if="errors.value" class="mt-1 text-sm text-red-600">
              {{ errors.value[0] }}
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Unit *
            </label>
            <input
              v-model="form.unit"
              type="text"
              class="input-field"
              placeholder="km, kWh, kg, etc."
              required
            />
            <div v-if="errors.unit" class="mt-1 text-sm text-red-600">
              {{ errors.unit[0] }}
            </div>
          </div>
        </div>

        <!-- Date and Time -->
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Date *
            </label>
            <input
              v-model="form.date"
              type="date"
              class="input-field"
              required
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Time *
            </label>
            <input
              v-model="form.time"
              type="time"
              class="input-field"
              required
            />
          </div>
        </div>

        <!-- Optional: End Date/Time for duration activities -->
        <div v-if="selectedTemplate?.requires_duration" class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              End Date
            </label>
            <input
              v-model="form.end_date"
              type="date"
              class="input-field"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              End Time
            </label>
            <input
              v-model="form.end_time"
              type="time"
              class="input-field"
            />
          </div>
        </div>

        <!-- Location (Optional) -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Location (Optional)
          </label>
          <input
            v-model="form.location_name"
            type="text"
            class="input-field"
            placeholder="City, address, or place name"
          />
          <p class="mt-1 text-xs text-gray-500">
            This helps provide more accurate carbon calculations
          </p>
        </div>

        <!-- Notes -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Notes (Optional)
          </label>
          <textarea
            v-model="form.notes"
            class="input-field"
            rows="3"
            placeholder="Additional details about this activity..."
          ></textarea>
        </div>

        <!-- CO2 Estimate Preview -->
        <div v-if="estimatedCO2 > 0" class="bg-primary-50 border border-primary-200 rounded-lg p-4">
          <div class="flex items-center space-x-3">
            <div class="w-10 h-10 bg-primary-200 rounded-lg flex items-center justify-center">
              <span class="text-primary-700">📊</span>
            </div>
            <div>
              <p class="font-medium text-primary-800">Estimated CO₂ Impact</p>
              <p class="text-sm text-primary-600">
                Approximately <strong>{{ estimatedCO2.toFixed(1) }} kg CO₂e</strong>
              </p>
            </div>
          </div>
        </div>

        <!-- Error Display -->
        <div v-if="errors.non_field_errors" class="bg-red-50 border border-red-200 rounded-lg p-3">
          <div class="text-sm text-red-600">
            {{ errors.non_field_errors[0] }}
          </div>
        </div>

        <!-- Submit Button -->
        <div class="flex space-x-4">
          <button
            type="submit"
            class="flex-1 btn-primary flex items-center justify-center"
            :disabled="isLoading"
          >
            <div v-if="isLoading" class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
            {{ isLoading ? 'Logging Activity...' : 'Log Activity' }}
          </button>
          
          <router-link 
            to="/activities" 
            class="btn-secondary flex items-center justify-center px-6"
          >
            Cancel
          </router-link>
        </div>
      </form>
    </div>

    <!-- Quick Templates -->
    <div v-if="popularTemplates.length" class="mt-8">
      <h3 class="text-lg font-semibold text-gray-900 mb-4">Quick Templates</h3>
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <button
          v-for="template in popularTemplates"
          :key="template.id"
          @click="selectTemplate(template)"
          class="p-4 border border-gray-200 rounded-lg hover:border-primary-300 hover:bg-primary-50 transition-colors text-left"
        >
          <div class="flex items-center space-x-3">
            <span class="text-2xl">{{ getCategoryIcon(template.category.category_type) }}</span>
            <div>
              <p class="font-medium text-gray-900">{{ template.name }}</p>
              <p class="text-sm text-gray-600">{{ template.description }}</p>
              <p class="text-xs text-gray-500 mt-1">
                Default: {{ template.default_value }} {{ template.default_unit }}
              </p>
            </div>
          </div>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useActivitiesStore } from '@/stores/activities'
import { useNotificationStore } from '@/stores/notifications'

const router = useRouter()
const activitiesStore = useActivitiesStore()
const notificationStore = useNotificationStore()

const isLoading = ref(false)
const errors = ref({})
const selectedTemplate = ref(null)
const estimatedCO2 = ref(0)

const form = reactive({
  category: '',
  activity_type: '',
  value: null,
  unit: '',
  date: new Date().toISOString().split('T')[0],
  time: new Date().toTimeString().slice(0, 5),
  end_date: '',
  end_time: '',
  location_name: '',
  notes: ''
})

const categories = computed(() => activitiesStore.categories)
const templates = computed(() => activitiesStore.templates)

const filteredTemplates = computed(() => {
  if (!form.category) return []
  return templates.value.filter(t => t.category === form.category)
})

const popularTemplates = computed(() => {
  return templates.value.slice(0, 6) // Show first 6 templates as popular
})

const getCategoryIcon = (categoryType) => {
  const icons = {
    transportation: '🚗',
    energy: '⚡',
    food: '🍽️',
    consumption: '🛍️',
    waste: '🗑️'
  }
  return icons[categoryType] || '📊'
}

const onCategoryChange = async () => {
  // Reset form fields when category changes
  form.activity_type = ''
  form.value = null
  form.unit = ''
  selectedTemplate.value = null
  
  // Fetch templates for this category
  if (form.category) {
    await activitiesStore.fetchTemplates(form.category)
  }
}

const selectTemplate = (template) => {
  selectedTemplate.value = template
  form.category = template.category
  form.activity_type = template.activity_type
  form.value = template.default_value
  form.unit = template.default_unit
  
  // Estimate CO2 based on template
  estimatedCO2.value = (template.default_value || 0) * 0.2 // Simple estimation
}

const handleSubmit = async () => {
  isLoading.value = true
  errors.value = {}

  try {
    // Construct start timestamp
    const startTimestamp = new Date(`${form.date}T${form.time}:00`).toISOString()
    
    // Construct end timestamp if provided
    let endTimestamp = null
    if (form.end_date && form.end_time) {
      endTimestamp = new Date(`${form.end_date}T${form.end_time}:00`).toISOString()
    }

    const activityData = {
      category: form.category,
      activity_type: form.activity_type,
      value: form.value,
      unit: form.unit,
      start_timestamp: startTimestamp,
      end_timestamp: endTimestamp,
      location_name: form.location_name,
      notes: form.notes
    }

    await activitiesStore.createActivity(activityData)
    
    notificationStore.success('Activity logged successfully! CO₂ impact calculated.')
    router.push('/activities')
    
  } catch (error) {
    if (error.response?.data) {
      errors.value = error.response.data
    } else {
      notificationStore.error('Failed to log activity. Please try again.')
    }
  } finally {
    isLoading.value = false
  }
}

// Watch form changes for CO2 estimation
watch([() => form.value, () => form.unit], () => {
  if (form.value && form.unit) {
    // Simple CO2 estimation - in real app this would call an API
    const baseFactors = {
      km: 0.2,  // kg CO2 per km
      kWh: 0.4, // kg CO2 per kWh
      kg: 5.0   // kg CO2 per kg (for food)
    }
    const factor = baseFactors[form.unit] || 0.1
    estimatedCO2.value = form.value * factor
  } else {
    estimatedCO2.value = 0
  }
})

onMounted(async () => {
  await Promise.all([
    activitiesStore.fetchCategories(),
    activitiesStore.fetchTemplates()
  ])
})
</script>