<template>
  <div class="chart-container">
    <Line :data="chartData" :options="chartOptions" />
  </div>
</template>

<script setup>
import { useChartSetup } from './CryptoChart.js'
import './CryptoChart.css'

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

const { Line, chartData, chartOptions } = useChartSetup(props)
</script>
