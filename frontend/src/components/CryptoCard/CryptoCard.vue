<template>
  <div class="glass-card crypto-card" :class="animationClass">
    <CardHeader 
      :symbol="symbol"
      :change-class="changeClass"
      :formatted-change="formattedChange"
      :is-trending="data.is_trending"
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
    
    <!-- RSI / Momentum Indicator -->
    <div class="rsi-container" v-if="data.rsi !== undefined && data.rsi !== null">
      <div class="rsi-info">
        <span class="rsi-label">RSI (14)</span>
        <span class="rsi-value" :class="getRsiClass(data.rsi)">{{ data.rsi }}</span>
      </div>
      <div class="rsi-track">
        <div 
          class="rsi-bar" 
          :style="{ width: `${data.rsi}%`, backgroundColor: getRsiColor(data.rsi) }"
        ></div>
      </div>
    </div>
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

const emit = defineEmits(['toggle-expand']);

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
} = useCryptoCard(props, emit);

const getRsiColor = (rsi) => {
  if (rsi >= 70) return '#ff4757'; // Overbought (Red/Sell risk)
  if (rsi <= 30) return '#2ed573'; // Oversold (Green/Buy opp)
  return '#eccc68'; // Neutral
}

const getRsiClass = (rsi) => {
  if (rsi >= 70) return 'text-danger';
  if (rsi <= 30) return 'text-success';
  return 'text-warning';
}
</script>
