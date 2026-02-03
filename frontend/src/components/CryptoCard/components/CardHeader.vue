<template>
  <div class="card-header">
    <div class="symbol-info">
      <h3>{{ symbol.replace("USDT", "") }}</h3>
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
  formattedChange: String
})
</script>
