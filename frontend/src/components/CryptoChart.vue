<template>
  <div class="chart-container">
    <Line :data="chartData" :options="chartOptions" />
  </div>
</template>

<script setup>
import { computed } from 'vue'
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
  history: {
    type: Array,
    required: true
  },
  color: {
    type: String,
    default: '#667eea'
  }
})

const chartData = computed(() => {
  return {
    labels: props.history.map(h => new Date(h.time).toLocaleTimeString()),
    datasets: [
      {
        label: 'Price',
        backgroundColor: (context) => {
          const ctx = context.chart.ctx;
          const gradient = ctx.createLinearGradient(0, 0, 0, 200);
          gradient.addColorStop(0, hexToRgba(props.color, 0.5));
          gradient.addColorStop(1, hexToRgba(props.color, 0));
          return gradient;
        },
        borderColor: props.color,
        borderWidth: 2,
        pointRadius: 0, // Hide points for clean look
        pointHoverRadius: 4,
        data: props.history.map(h => h.price),
        fill: true,
        tension: 0.4 // Smooth curve
      }
    ]
  }
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    tooltip: {
      mode: 'index',
      intersect: false,
      callbacks: {
        label: (context) => `$${context.raw.toFixed(2)}`
      }
    }
  },
  scales: {
    x: { display: false }, // Hide X axis
    y: { display: false }  // Hide Y axis
  },
  interaction: {
    mode: 'nearest',
    axis: 'x',
    intersect: false
  }
}

// Helper to convert hex to rgba
const hexToRgba = (hex, alpha) => {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}
</script>

<style scoped>
.chart-container {
  height: 100px; /* Sparkline height */
  width: 100%;
}
</style>
