<template>
  <span 
    class="status-badge" 
    :class="{ loading: isLoadingMore, live: hasNews }"
  >
    {{ hasNews ? 'Live' : 'Loading...' }}
  </span>
</template>

<script setup>
defineProps({
  isLoadingMore: {
    type: Boolean,
    default: false
  },
  hasNews: {
    type: Boolean,
    default: false
  }
})
</script>
