<template>
  <tr :class="animationClass">
    <td>
      <div class="coin-cell">
        <span class="coin-symbol">{{ coin.symbol.replace('USDT', '') }}</span>
        <span class="coin-pair">/USDT</span>
      </div>
    </td>
    <td class="text-right font-mono">
      <div class="price-cell">{{ formatPrice(coin.price) }}</div>
    </td>
    <td class="text-right">
      <span class="change-pill" :class="getChangeClass(coin.change_24h)">
        {{ formatChange(coin.change_24h) }}
      </span>
    </td>
    <td class="text-right mobile-hide text-muted">
      {{ formatVolume(coin.volume_24h) }}
    </td>
  </tr>
</template>

<script setup>
import { defineProps, toRefs, ref, watch } from 'vue'

const props = defineProps({
  coin: {
    type: Object,
    required: true
  }
})

const { coin } = toRefs(props)
const animationClass = ref('')
const animationTimeout = ref(null)

// Watch for price changes to trigger animation
watch(() => coin.value.price, (newVal, oldVal) => {
  if (!oldVal) return
  
  // Clear previous timeout
  if (animationTimeout.value) clearTimeout(animationTimeout.value)
  
  // Set new animation class
  if (newVal > oldVal) {
    animationClass.value = 'row-flash-green'
  } else if (newVal < oldVal) {
    animationClass.value = 'row-flash-red'
  }
  
  // Remove class after animation finishes
  animationTimeout.value = setTimeout(() => {
    animationClass.value = ''
  }, 800)
})

function getChangeClass(val) {
  if (val > 0) return 'text-success'
  if (val < 0) return 'text-danger'
  return 'text-muted'
}

function formatPrice(val) {
  if (!val) return '$0.00'
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: val < 1 ? 4 : 2,
    maximumFractionDigits: val < 1 ? 4 : 2
  }).format(val)
}

function formatChange(val) {
  if (val === undefined) return '0.00%'
  return `${val > 0 ? '+' : ''}${val.toFixed(2)}%`
}

function formatVolume(val) {
  if (!val) return '0'
  if (val >= 1000000) {
    return `$${(val / 1000000).toFixed(2)}M`
  }
  if (val >= 1000) {
    return `$${(val / 1000).toFixed(2)}K`
  }
  return `$${val.toFixed(0)}`
}
</script>

<style scoped>
td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  transition: background-color 0.3s ease;
}

tr:last-child td {
  border-bottom: none;
}

tr:hover {
  background: rgba(255, 255, 255, 0.02);
}

/* Row Flash Animations */
.row-flash-green td {
  background: rgba(0, 208, 132, 0.1);
  animation: bgFlashGreen 0.8s ease-out;
}

.row-flash-red td {
  background: rgba(255, 71, 87, 0.1);
  animation: bgFlashRed 0.8s ease-out;
}

@keyframes bgFlashGreen {
  0% { background: rgba(0, 208, 132, 0.2); }
  100% { background: transparent; }
}

@keyframes bgFlashRed {
  0% { background: rgba(255, 71, 87, 0.2); }
  100% { background: transparent; }
}

.coin-cell {
  display: flex;
  align-items: baseline;
  gap: 0.25rem;
}

.coin-symbol {
  font-weight: 600;
  color: var(--text-primary);
}

.coin-pair {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.text-right {
  text-align: right;
}

.font-mono {
  font-family: 'SF Mono', 'Roboto Mono', monospace;
  letter-spacing: -0.02em;
}

.price-cell {
  transition: transform 0.2s;
}

.row-flash-green .price-cell {
  color: var(--success);
  transform: scale(1.05);
}

.row-flash-red .price-cell {
  color: var(--danger);
  transform: scale(1.05);
}

.change-pill {
  font-weight: 500;
}

@media (max-width: 600px) {
  .mobile-hide {
    display: none;
  }
  
  td {
    padding: 0.75rem 0.5rem;
  }
}
</style>
