<template>
  <div class="glass-card crypto-card" :class="animationClass">
    <div class="card-header">
      <div class="symbol-info">
        <h3>{{ symbol.replace('USDT', '') }}</h3>
        <span class="pair">/USDT</span>
      </div>
      <div class="change-badge" :class="changeClass">
        {{ formattedChange }}
      </div>
    </div>
    
    <div class="price-container">
      <div class="price">{{ formattedPrice }}</div>
      <button 
        class="chart-btn" 
        @click.stop="toggleChart" 
        :class="{ active: showChart }"
        title="Toggle Chart"
      >
        <span v-if="!showChart">Chart</span>
        <span v-else>Close</span>
      </button>
    </div>
    
    <!-- Chart Section -->
    <div v-if="showChart" class="chart-wrapper animate-fade-in">
      <div class="chart-controls">
        <button 
          v-for="p in ['15m', '1h', '4h', '24h']" 
          :key="p"
          class="range-btn"
          :class="{ active: currentPeriod === p }"
          @click="changePeriod(p)"
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
      />
      <div v-else class="chart-loader">
        No history data for {{ currentPeriod }}
      </div>
    </div>
    
    <div class="card-footer">
      <div class="stat">
        <span class="label">High</span>
        <span class="value">{{ formatPrice(data.high_24h) }}</span>
      </div>
      <div class="stat">
        <span class="label">Low</span>
        <span class="value">{{ formatPrice(data.low_24h) }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, defineProps, toRefs, ref, watch } from 'vue'
import CryptoChart from './CryptoChart.vue'

const props = defineProps({
  symbol: {
    type: String,
    required: true
  },
  data: {
    type: Object,
    required: true,
    default: () => ({
      price: 0,
      change_24h: 0,
      high_24h: 0,
      low_24h: 0
    })
  }
})

const { data } = toRefs(props)
const animationClass = ref('')
const animationTimeout = ref(null)

const showChart = ref(false)
const history = ref([])
const loadingHistory = ref(false)
const currentPeriod = ref('15m')

const fetchHistory = async () => {
  loadingHistory.value = true
  try {
    const WS_URL = import.meta.env.PROD ? '' : 'http://localhost:8000'
    const res = await fetch(`${WS_URL}/api/history/${props.symbol}?period=${currentPeriod.value}`)
    const json = await res.json()
    if (json.history) {
      history.value = json.history
    }
  } catch (e) {
    console.error('Failed to fetch history', e)
  } finally {
    loadingHistory.value = false
  }
}

const toggleChart = async () => {
  showChart.value = !showChart.value
  if (showChart.value && history.value.length === 0) {
    await fetchHistory()
  }
}

const changePeriod = async (period) => {
  currentPeriod.value = period
  await fetchHistory()
}

// Watch for price changes to update history if chart is visible and on 15m period
watch(() => data.value.price, (newVal) => {
  if (showChart.value && newVal && currentPeriod.value === '15m') {
    history.value.push({
      time: Date.now(),
      price: newVal
    })
    if (history.value.length > 100) history.value.shift()
  }
})

// Watch for price changes to trigger animation
watch(() => data.value.price, (newVal, oldVal) => {
  if (!oldVal) return
  
  // Clear previous timeout
  if (animationTimeout.value) clearTimeout(animationTimeout.value)
  
  // Set new animation class
  if (newVal > oldVal) {
    animationClass.value = 'price-up-trigger'
  } else if (newVal < oldVal) {
    animationClass.value = 'price-down-trigger'
  }
  
  // Remove class after animation finishes
  animationTimeout.value = setTimeout(() => {
    animationClass.value = ''
  }, 1000)
})

const formattedPrice = computed(() => {
  return formatPrice(data.value.price)
})

const formattedChange = computed(() => {
  const val = data.value.change_24h
  return `${val > 0 ? '+' : ''}${val.toFixed(2)}%`
})

const changeClass = computed(() => {
  const val = data.value.change_24h
  if (val > 0) return 'text-success bg-success-dim'
  if (val < 0) return 'text-danger bg-danger-dim'
  return 'text-muted'
})

const chartColor = computed(() => {
   return data.value.change_24h >= 0 ? '#00d084' : '#ff4757'
})

function formatPrice(val) {
  if (!val) return '0.00'
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: val < 1 ? 4 : 2,
    maximumFractionDigits: val < 1 ? 4 : 2
  }).format(val)
}
</script>

<style scoped>
.crypto-card {
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  height: fit-content; /* Allow expansion */
}

/* Chart Styles */
.chart-wrapper {
  margin-top: 1rem;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  padding-top: 1rem;
  height: 160px; /* Increased for controls */
}

.chart-controls {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
  justify-content: center;
}

.range-btn {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.05);
  color: var(--text-muted);
  font-size: 0.7rem;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.range-btn:hover {
  background: rgba(255, 255, 255, 0.08);
  color: var(--text-primary);
}

.range-btn.active {
  background: var(--accent-primary);
  color: white;
  border-color: var(--accent-primary);
}

.chart-loader {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100px;
  color: var(--text-muted);
  font-size: 0.8rem;
}

.spinner {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255, 255, 255, 0.1);
  border-top-color: var(--accent-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.chart-btn {
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  transition: all 0.2s;
  font-size: 0.8rem;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.chart-btn:hover {
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-primary);
}

.chart-btn.active {
  color: var(--accent-primary);
  background: rgba(102, 126, 234, 0.1);
}

.crypto-card::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  z-index: 0;
  opacity: 0;
  transition: opacity 0.5s ease;
}

/* Updated Animation Logic */
.price-up-trigger::after {
  background: radial-gradient(circle at center, var(--success-bg) 0%, transparent 70%);
  animation: flash 0.8s ease-out forwards;
}

.price-down-trigger::after {
  background: radial-gradient(circle at center, var(--danger-bg) 0%, transparent 70%);
  animation: flash 0.8s ease-out forwards;
}

@keyframes flash {
  0% { opacity: 1; transform: scale(0.8); }
  100% { opacity: 0; transform: scale(1.5); }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  z-index: 1;
}

.symbol-info {
  display: flex;
  align-items: baseline;
  gap: 0.25rem;
}

.symbol-info h3 {
  font-size: 1.25rem;
  font-weight: 700;
}

.pair {
  font-size: 0.75rem;
  color: var(--text-muted);
  font-weight: 500;
}

.change-badge {
  font-size: 0.875rem;
  font-weight: 600;
  padding: 0.25rem 0.5rem;
  border-radius: var(--radius-sm);
}

.bg-success-dim {
  background: rgba(0, 208, 132, 0.1);
  color: var(--success);
}

.bg-danger-dim {
  background: rgba(255, 71, 87, 0.1);
  color: var(--danger);
}

.price-container {
  z-index: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.price {
  font-size: 2rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  transition: color 0.3s;
}

/* Text color feedback during update */
.price-up-trigger .price {
  color: var(--success);
  text-shadow: 0 0 20px rgba(0, 208, 132, 0.3);
}

.price-down-trigger .price {
  color: var(--danger);
  text-shadow: 0 0 20px rgba(255, 71, 87, 0.3);
}

.card-footer {
  display: flex;
  justify-content: space-between;
  padding-top: 1rem;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  margin-top: auto;
  z-index: 1;
}

.stat {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.stat .label {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.stat .value {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-secondary);
}
</style>
