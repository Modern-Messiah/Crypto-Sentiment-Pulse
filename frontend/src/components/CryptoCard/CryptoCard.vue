<template>
  <div class="glass-card crypto-card" :class="animationClass">
    <CardHeader 
      :symbol="symbol"
      :change-class="changeClass"
      :formatted-change="formattedChange"
    />

    <CardPrice 
      :formatted-price="formattedPrice"
      :show-chart="showChart"
      @toggle-chart="toggleChart"
    />

    <ChartSection 
      v-if="showChart"
      :current-period="currentPeriod"
      :loading-history="loadingHistory"
      :history="history"
      :chart-color="chartColor"
      @change-period="changePeriod"
    />

    <CardStats 
      :data="data"
      :format-price="formatPrice"
    />
  </div>
</template>

<script setup>
import CardHeader from './components/CardHeader.vue'
import CardPrice from './components/CardPrice.vue'
import CardStats from './components/CardStats.vue'
import ChartSection from './components/ChartSection.vue'
import { useCryptoCard } from './hooks/useCryptoCard.js'
import './styles/CryptoCard.css'

const props = defineProps({
  symbol: {
    type: String,
    required: true,
  },
  data: {
    type: Object,
    required: true,
    default: () => ({
      price: 0,
      change_24h: 0,
      high_24h: 0,
      low_24h: 0,
    }),
  },
});

const {
  animationClass,
  showChart,
  history,
  loadingHistory,
  currentPeriod,
  toggleChart,
  changePeriod,
  formattedPrice,
  formattedChange,
  changeClass,
  chartColor,
  formatPrice
} = useCryptoCard(props);
</script>
