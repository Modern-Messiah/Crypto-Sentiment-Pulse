<template>
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
</template>

<script setup>
import '../styles/CardStats.css'

defineProps({
  data: Object,
  formatPrice: Function
})
</script>
