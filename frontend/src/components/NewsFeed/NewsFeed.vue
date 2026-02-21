<template>
  <div class="news-feed" :class="{ 'header-hidden': isHeaderHidden }">
    <NewsFeedHeader 
      :is-loading-more="isLoadingMore" 
      :has-news="newsItems.length > 0" 
    />
    
    <NewsList 
      v-if="newsItems.length > 0"
      :news-items="newsItems"
      :is-loading-more="isLoadingMore"
      :all-loaded="allLoaded"
      @load-more="$emit('load-more')"
    />

    <EmptyState v-else />
  </div>
</template>

<script setup>
import NewsFeedHeader from './components/NewsFeedHeader.vue'
import NewsList from './components/NewsList.vue'
import EmptyState from './components/EmptyState.vue'
import './styles/NewsFeed.css'

defineProps({
  newsItems: {
    type: Array,
    default: () => []
  },
  isLoadingMore: {
    type: Boolean,
    default: false
  },
  allLoaded: {
    type: Boolean,
    default: false
  },
  isHeaderHidden: {
    type: Boolean,
    default: false
  }
})

defineEmits(['load-more'])
</script>
