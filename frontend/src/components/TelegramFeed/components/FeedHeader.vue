<template>
  <div class="feed-header">
    <div class="title-group">
      <h2 class="feed-title">
        Telegram Feed
      </h2>
      <p class="feed-disclaimer">
        Real-time updates. New messages appear instantly as they are received.
      </p>
    </div>
    <FeedStatusBadge
      :is-connected="isConnected"
      :is-demo-mode="isDemoMode"
    />
  </div>
</template>

<script setup>
import FeedStatusBadge from './FeedStatusBadge.vue'

defineProps({
  isConnected: {
    type: Boolean,
    default: false
  },
  isDemoMode: {
    type: Boolean,
    default: false
  }
})
</script>
