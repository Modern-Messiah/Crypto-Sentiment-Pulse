<template>
  <div class="chart-container">
    <Line :data="chartData" :options="chartOptions" />
  </div>
</template>

<script setup>
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
  }
})

const { Line, chartData, chartOptions } = useCryptoChart(props)
</script>
