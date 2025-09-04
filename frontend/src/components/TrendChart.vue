<template>
  <div class="w-full h-full">
    <canvas ref="chartCanvas"></canvas>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from 'vue'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'
import { Line } from 'vue-chartjs'

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

const props = defineProps({
  data: {
    type: Array,
    default: () => []
  },
  period: {
    type: String,
    default: '7D'
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
  
  const labels = props.data.map(item => {
    const date = new Date(item.date)
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric' 
    })
  })

  const values = props.data.map(item => item.co2)

  chartInstance = new ChartJS(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [{
        label: 'CO₂ Emissions (kg)',
        data: values,
        borderColor: '#10b981',
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        borderWidth: 3,
        fill: true,
        tension: 0.4,
        pointBackgroundColor: '#10b981',
        pointBorderColor: '#ffffff',
        pointBorderWidth: 2,
        pointRadius: 5,
        pointHoverRadius: 7,
        pointHoverBackgroundColor: '#059669',
        pointHoverBorderColor: '#ffffff',
        pointHoverBorderWidth: 2
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        intersect: false,
        mode: 'index'
      },
      plugins: {
        legend: {
          display: false
        },
        tooltip: {
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          titleColor: '#ffffff',
          bodyColor: '#ffffff',
          borderColor: '#10b981',
          borderWidth: 1,
          cornerRadius: 8,
          displayColors: false,
          callbacks: {
            title: (context) => {
              return `${context[0].label}`
            },
            label: (context) => {
              return `${context.parsed.y.toFixed(1)} kg CO₂e`
            }
          }
        }
      },
      scales: {
        x: {
          grid: {
            display: false
          },
          border: {
            display: false
          },
          ticks: {
            color: '#6b7280',
            font: {
              size: 12
            }
          }
        },
        y: {
          beginAtZero: true,
          grid: {
            color: 'rgba(107, 114, 128, 0.1)',
            drawBorder: false
          },
          border: {
            display: false
          },
          ticks: {
            color: '#6b7280',
            font: {
              size: 12
            },
            callback: (value) => `${value} kg`
          }
        }
      },
      elements: {
        point: {
          hoverRadius: 8
        }
      }
    }
  })
}

onMounted(() => {
  nextTick(() => {
    createChart()
  })
})

watch([() => props.data, () => props.period], () => {
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