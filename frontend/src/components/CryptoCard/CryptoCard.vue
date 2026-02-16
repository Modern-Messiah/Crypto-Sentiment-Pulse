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

    <div v-if="data.tvl" class="tvl-container">
      <div class="tvl-info">
        <span class="tvl-label" title="Total Value Locked - the total amount of assets currently being held in this network or protocol.">TVL</span>
        <div class="tvl-values">
          <span class="tvl-value">{{ formatTVL(data.tvl) }}</span>
          <span v-if="data.tvl_change_1d !== undefined" 
                class="tvl-change" 
                :class="data.tvl_change_1d >= 0 ? 'text-success' : 'text-danger'">
            {{ data.tvl_change_1d >= 0 ? '+' : '' }}{{ data.tvl_change_1d.toFixed(1) }}%
          </span>
        </div>
      </div>

      <div v-if="data.money_flow_24h" class="flow-info">
        <span class="tvl-label">Money Flow (24h)</span>
        <span class="tvl-value" :class="data.money_flow_24h >= 0 ? 'text-success' : 'text-danger'">
          {{ formatMoneyFlow(data.money_flow_24h) }}
        </span>
      </div>
    </div>
    
    <div class="rsi-container" v-if="data.rsi !== undefined && data.rsi !== null">
      <div class="rsi-info">
        <span class="rsi-label" title="Relative Strength Index (14-period) - a momentum oscillator that measures the speed and change of price movements.">RSI (14)</span>
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
  if (rsi >= 70) return '#ff4757';
  if (rsi <= 30) return '#2ed573';
  return '#eccc68';
}

const getRsiClass = (rsi) => {
  if (rsi >= 70) return 'text-danger';
  if (rsi <= 30) return 'text-success';
  return 'text-warning';
}

const formatTVL = (value) => {
  if (!value) return '$0';
  if (value >= 1e9) return '$' + (value / 1e9).toFixed(2) + 'B';
  if (value >= 1e6) return '$' + (value / 1e6).toFixed(1) + 'M';
  return '$' + value.toLocaleString();
};

const formatMoneyFlow = (value) => {
  if (value === undefined || value === null) return '';
  const prefix = value >= 0 ? '+$' : '-$';
  const absValue = Math.abs(value);
  if (absValue >= 1e9) return prefix + (absValue / 1e9).toFixed(1) + 'B';
  if (absValue >= 1e6) return prefix + (absValue / 1e6).toFixed(1) + 'M';
  return prefix + absValue.toLocaleString();
};
</script>
