<template>
  <div class="chart-wrapper animate-fade-in">
    <div class="chart-controls">
      <button
        v-for="p in ['1m', '5m', '15m', '1h', '4h', '24h']"
        :key="p"
        class="range-btn"
        :class="{ active: currentPeriod === p }"
        @click="$emit('change-period', p)"
      >
        {{ p }}
      </button>
    </div>

    <div v-if="loadingHistory" class="chart-loader">
      <div class="spinner"></div>
    </div>
    <CryptoChart
      v-else-if="history.length > 0"
      :history="history"
      :color="chartColor"
      :period="currentPeriod"
    />
    <div v-else class="chart-loader">
      No history data for {{ currentPeriod }}
    </div>
  </div>
</template>

<script setup>
import CryptoChart from "../../CryptoChart/CryptoChart.vue";
import '../styles/ChartSection.css'

defineProps({
  currentPeriod: String,
  loadingHistory: Boolean,
  history: Array,
  chartColor: String
})

defineEmits(['change-period'])
</script>
