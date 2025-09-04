<template>
  <div class="w-full h-full flex items-center">
    <div v-if="!props.data.length" class="w-full text-center text-gray-500">
      <span class="text-4xl mb-2 block">📊</span>
      <p class="text-sm">No emissions data available</p>
    </div>
    <div v-else class="w-full">
      <canvas ref="chartCanvas"></canvas>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from 'vue'
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend
} from 'chart.js'

// Register ChartJS components
ChartJS.register(ArcElement, Tooltip, Legend)

const props = defineProps({
  data: {
    type: Array,
    default: () => []
  }
})

const chartCanvas = ref(null)
let chartInstance = null

const createChart = () => {
  if (chartInstance) {
    chartInstance.destroy()
  }

  if (!chartCanvas.value || !props.data.length) return

  const ctx = chartCanvas.value.getContext('2d')
  
  const labels = props.data.map(item => item.category)
  const values = props.data.map(item => parseFloat(item.value) || 0)
  const colors = props.data.map(item => item.color)
  
  // Generate lighter colors for hover
  const hoverColors = colors.map(color => {
    // Simple way to make color lighter
    return color + '20' // Add some transparency
  })

  chartInstance = new ChartJS(ctx, {
    type: 'doughnut',
    data: {
      labels,
      datasets: [{
        data: values,
        backgroundColor: colors,
        hoverBackgroundColor: hoverColors,
        borderWidth: 0,
        cutout: '65%'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            padding: 20,
            usePointStyle: true,
            pointStyle: 'circle',
            font: {
              size: 12
            },
            color: '#374151',
            generateLabels: function(chart) {
              const data = chart.data
              if (data.labels.length && data.datasets.length) {
                return data.labels.map((label, i) => {
                  const dataset = data.datasets[0]
                  const value = dataset.data[i]
                  const total = dataset.data.reduce((a, b) => a + b, 0)
                  const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : 0
                  
                  return {
                    text: `${label} (${percentage}%)`,
                    fillStyle: dataset.backgroundColor[i],
                    hidden: false,
                    index: i
                  }
                })
              }
              return []
            }
          }
        },
        tooltip: {
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          titleColor: '#ffffff',
          bodyColor: '#ffffff',
          borderColor: '#10b981',
          borderWidth: 1,
          cornerRadius: 8,
          callbacks: {
            label: (context) => {
              const label = context.label || ''
              const value = context.parsed || 0
              const total = context.dataset.data.reduce((a, b) => a + b, 0)
              const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : 0
              return `${label}: ${value.toFixed(1)} kg CO₂e (${percentage}%)`
            }
          }
        }
      },
      interaction: {
        intersect: false
      }
    }
  })
}

onMounted(() => {
  nextTick(() => {
    createChart()
  })
})

watch(() => props.data, () => {
  nextTick(() => {
    createChart()
  })
}, { deep: true })

// Cleanup on unmount
import { onUnmounted } from 'vue'
onUnmounted(() => {
  if (chartInstance) {
    chartInstance.destroy()
  }
})
</script>