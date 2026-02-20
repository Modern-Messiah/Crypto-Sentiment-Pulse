<template>
  <div class="sentiment-info">
    <div class="sentiment-label" :style="{ color: scoreColor }">
      {{ classification }}
    </div>
    <div class="sentiment-desc">
      Fear & Greed Index
    </div>
  </div>
</template>

<script setup>
defineProps({
  classification: {
    type: String,
    required: true
  },
  scoreColor: {
    type: String,
    required: true
  }
})
</script>
