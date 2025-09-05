<template>
  <div v-if="show" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full max-w-lg">
      <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
        <h3 class="text-lg font-medium text-gray-900 dark:text-white">
          Bulk Import {{ type.charAt(0).toUpperCase() + type.slice(1) }}
        </h3>
      </div>
      
      <div class="p-6 space-y-4">
        <!-- Download Template -->
        <div class="bg-blue-50 dark:bg-blue-900 p-4 rounded-lg">
          <div class="flex items-center justify-between">
            <div>
              <h4 class="text-sm font-medium text-blue-900 dark:text-blue-100">
                Download Template
              </h4>
              <p class="text-sm text-blue-700 dark:text-blue-200 mt-1">
                Download the CSV template with the required columns
              </p>
            </div>
            <button
              @click="downloadTemplate"
              class="px-3 py-2 text-sm font-medium text-blue-600 bg-white border border-blue-300 rounded-md hover:bg-blue-50"
            >
              Download
            </button>
          </div>
        </div>

        <!-- File Upload -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Upload CSV File
          </label>
          <div class="flex items-center justify-center w-full">
            <label
              class="flex flex-col items-center justify-center w-full h-32 border-2 border-gray-300 border-dashed rounded-lg cursor-pointer bg-gray-50 hover:bg-gray-100 dark:bg-gray-700 dark:border-gray-600 dark:hover:bg-gray-600"
            >
              <div class="flex flex-col items-center justify-center pt-5 pb-6">
                <UploadIcon class="w-8 h-8 mb-2 text-gray-400" />
                <p class="mb-2 text-sm text-gray-500 dark:text-gray-400">
                  <span class="font-semibold">Click to upload</span> or drag and drop
                </p>
                <p class="text-xs text-gray-500 dark:text-gray-400">CSV files only</p>
              </div>
              <input
                ref="fileInput"
                type="file"
                accept=".csv"
                @change="handleFileSelect"
                class="hidden"
              />
            </label>
          </div>
          
          <div v-if="selectedFile" class="mt-2 p-2 bg-green-50 dark:bg-green-900 rounded text-sm">
            Selected: {{ selectedFile.name }} ({{ formatFileSize(selectedFile.size) }})
          </div>
        </div>

        <!-- Import Options -->
        <div class="space-y-3">
          <div class="flex items-center">
            <input
              v-model="options.skipFirstRow"
              type="checkbox"
              class="h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300 rounded"
            />
            <label class="ml-2 block text-sm text-gray-700 dark:text-gray-300">
              Skip first row (headers)
            </label>
          </div>
          
          <div class="flex items-center">
            <input
              v-model="options.updateExisting"
              type="checkbox"
              class="h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300 rounded"
            />
            <label class="ml-2 block text-sm text-gray-700 dark:text-gray-300">
              Update existing records
            </label>
          </div>
        </div>

        <!-- Progress -->
        <div v-if="uploading" class="space-y-2">
          <div class="flex justify-between text-sm text-gray-600 dark:text-gray-400">
            <span>Uploading...</span>
            <span>{{ uploadProgress }}%</span>
          </div>
          <div class="w-full bg-gray-200 rounded-full h-2">
            <div
              class="bg-green-600 h-2 rounded-full transition-all duration-300"
              :style="{ width: uploadProgress + '%' }"
            ></div>
          </div>
        </div>

        <!-- Results -->
        <div v-if="results" class="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
          <h4 class="text-sm font-medium text-gray-900 dark:text-white mb-2">
            Import Results
          </h4>
          <div class="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span class="text-green-600">✓ Success:</span>
              <span class="font-medium">{{ results.success }}</span>
            </div>
            <div>
              <span class="text-red-600">✗ Errors:</span>
              <span class="font-medium">{{ results.errors }}</span>
            </div>
          </div>
          
          <div v-if="results.errorDetails?.length" class="mt-3">
            <button
              @click="showErrors = !showErrors"
              class="text-sm text-blue-600 hover:text-blue-800"
            >
              {{ showErrors ? 'Hide' : 'Show' }} Error Details
            </button>
            <div v-if="showErrors" class="mt-2 max-h-32 overflow-y-auto">
              <div
                v-for="(error, index) in results.errorDetails"
                :key="index"
                class="text-xs text-red-600 dark:text-red-400 mb-1"
              >
                Row {{ error.row }}: {{ error.message }}
              </div>
            </div>
          </div>
        </div>
        
        <div class="flex justify-end space-x-3 pt-4">
          <button
            type="button"
            @click="$emit('close')"
            class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
          >
            {{ results ? 'Close' : 'Cancel' }}
          </button>
          <button
            v-if="!results"
            @click="handleImport"
            :disabled="!selectedFile || uploading"
            class="px-4 py-2 text-sm font-medium text-white bg-green-600 border border-transparent rounded-md hover:bg-green-700 disabled:opacity-50"
          >
            {{ uploading ? 'Importing...' : 'Import' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { UploadIcon } from '@heroicons/vue/outline'
import { enterpriseService } from '@/services/enterprise'
import { useToast } from '@/composables/useToast'

export default {
  name: 'BulkImportModal',
  props: {
    show: Boolean,
    type: {
      type: String,
      required: true
    }
  },
  emits: ['close', 'imported'],
  setup(props, { emit }) {
    const { showToast } = useToast()
    
    const selectedFile = ref(null)
    const uploading = ref(false)
    const uploadProgress = ref(0)
    const results = ref(null)
    const showErrors = ref(false)
    const options = ref({
      skipFirstRow: true,
      updateExisting: false
    })

    const handleFileSelect = (event) => {
      const file = event.target.files[0]
      if (file && file.type === 'text/csv') {
        selectedFile.value = file
        results.value = null
      } else {
        showToast('Please select a CSV file', 'error')
      }
    }

    const formatFileSize = (bytes) => {
      const sizes = ['Bytes', 'KB', 'MB', 'GB']
      if (bytes === 0) return '0 Byte'
      const i = parseInt(Math.floor(Math.log(bytes) / Math.log(1024)))
      return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i]
    }

    const downloadTemplate = async () => {
      try {
        const blob = await enterpriseService.downloadTemplate(props.type)
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `${props.type}-template.csv`
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        window.URL.revokeObjectURL(url)
        showToast('Template downloaded successfully', 'success')
      } catch (error) {
        showToast('Failed to download template', 'error')
      }
    }

    const handleImport = async () => {
      if (!selectedFile.value) return

      try {
        uploading.value = true
        uploadProgress.value = 0

        // Simulate progress
        const progressInterval = setInterval(() => {
          if (uploadProgress.value < 90) {
            uploadProgress.value += 10
          }
        }, 200)

        const response = await enterpriseService.bulkImport(
          props.type,
          selectedFile.value,
          options.value
        )

        clearInterval(progressInterval)
        uploadProgress.value = 100

        results.value = response
        emit('imported', response)
        
        if (response.errors === 0) {
          showToast('Import completed successfully', 'success')
        } else {
          showToast(`Import completed with ${response.errors} errors`, 'warning')
        }
      } catch (error) {
        console.error('Import error:', error)
        showToast('Import failed', 'error')
      } finally {
        uploading.value = false
      }
    }

    return {
      selectedFile,
      uploading,
      uploadProgress,
      results,
      showErrors,
      options,
      handleFileSelect,
      formatFileSize,
      downloadTemplate,
      handleImport,
      UploadIcon
    }
  }
}
</script>
</template>