<template>
  <div class="feed-header">
    <div class="title-group">
      <h2 class="feed-title">
        CryptoPanic News
      </h2>
      <p class="feed-disclaimer">
        Updates every 6 hours (Free Tier). Showing news from yesterday.
      </p>
    </div>
    <NewsStatusBadge
      :is-loading-more="isLoadingMore"
      :has-news="hasNews"
    />
  </div>
</template>

<script setup>
import NewsStatusBadge from './NewsStatusBadge.vue'

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
