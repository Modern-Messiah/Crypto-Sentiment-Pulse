<template>
  <div class="price-container">
    <div class="price">{{ formattedPrice }}</div>
    <button
      class="chart-btn"
      @click.stop="onToggleChart"
      :class="{ active: showChart }"
      title="Toggle Chart"
    >
      <span v-if="!showChart">Chart</span>
      <span v-else>Close</span>
    </button>
  </div>
</template>

<script setup>
import '../styles/CardPrice.css'

defineProps({
  formattedPrice: String,
  showChart: Boolean
})

const emit = defineEmits(['toggle-chart'])
const onToggleChart = () => emit('toggle-chart')
</script>
