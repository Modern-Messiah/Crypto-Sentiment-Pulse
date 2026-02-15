<template>
  <div class="card-header">
    <div class="symbol-info">
      <div class="symbol-name-container">
        <h3>{{ symbol.replace("USDT", "") }}</h3>
        <span v-if="isTrending" class="trending-badge" title="Trending on CoinGecko">В тренде</span>
      </div>
      <span class="pair">/USDT</span>
    </div>
    <div class="change-badge" :class="changeClass">
      {{ formattedChange }}
    </div>
  </div>
</template>

<script setup>
import '../styles/CardHeader.css'

defineProps({
  symbol: String,
  changeClass: String,
  formattedChange: String,
  isTrending: Boolean
})
</script>
