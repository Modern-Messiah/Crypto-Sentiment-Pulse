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
import { toRefs } from 'vue'
import { useCryptoTableRow } from './CryptoTableRow.js'
import './CryptoTableRow.css'

const props = defineProps({
  coin: {
    type: Object,
    required: true
  }
})

const { coin } = toRefs(props)
const { animationClass, getChangeClass, formatPrice, formatChange, formatVolume } = useCryptoTableRow(coin)
</script>
