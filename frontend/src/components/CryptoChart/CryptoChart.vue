<template>
  <div class="chart-container">
    <Line :data="chartData" :options="chartOptions" />
  </div>
</template>

<script setup>
import { onBeforeUnmount } from 'vue'
import { useCryptoChart } from './hooks/useCryptoChart.js'
import './styles/CryptoChart.css'

const props = defineProps({
  history: {
    type: Array,
    required: true
  },
  color: {
    type: String,
    default: '#667eea'
  },
  period: {
    type: String,
    default: '15m'
  }
})

const { Line, chartData, chartOptions, onUnmount } = useCryptoChart(props)

onBeforeUnmount(() => {
  onUnmount()
})
</script>
