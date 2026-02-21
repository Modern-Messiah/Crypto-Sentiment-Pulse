<template>
  <span 
    class="status-badge" 
    :class="{ 
      connected: isConnected && !isDemoMode, 
      live: isConnected && !isDemoMode,
      demo: isDemoMode,
      disconnected: !isConnected 
    }"
  >
    {{ statusText }}
  </span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  isConnected: {
    type: Boolean,
    default: false
  },
  isDemoMode: {
    type: Boolean,
    default: false
  }
})

const statusText = computed(() => {
  if (!props.isConnected) return 'Disconnected'
  if (props.isDemoMode) return 'Demo Mode'
  return 'Live'
})
</script>


