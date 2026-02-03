<template>
  <div class="status">
    <div class="status-indicator" :class="{ connected: isConnected }">
      <span class="dot"></span>
      <span class="status-text">{{ isConnected ? 'Live' : 'Connecting...' }}</span>
    </div>
    <div v-if="lastUpdate" class="last-update">
      Updated: {{ formatTime(lastUpdate) }}
    </div>
  </div>
</template>

<script setup>
import '../styles/StatusIndicator.css'

defineProps({
  isConnected: Boolean,
  lastUpdate: [Date, null],
  formatTime: Function
})
</script>
