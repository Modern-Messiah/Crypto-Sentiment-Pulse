<template>
  <td>
    <div class="coin-cell">
      <span class="coin-symbol">{{ symbol.replace('USDT', '') }}</span>
      <span class="coin-pair">/USDT</span>
    </div>
  </td>
</template>

<script setup>
defineProps({
  symbol: {
    type: String,
    required: true
  }
})
</script>
