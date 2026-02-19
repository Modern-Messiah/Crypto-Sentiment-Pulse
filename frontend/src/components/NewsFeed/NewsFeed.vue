<template>
  <div class="news-feed" :class="{ 'header-hidden': isHeaderHidden }">
    <div class="feed-header">
      <div class="title-group">
        <h2 class="feed-title">
          CryptoPanic News
        </h2>
        <p class="feed-disclaimer">
          Updates every 6 hours (Free Tier). Showing news from yesterday.
        </p>
      </div>
      <span 
        class="status-badge" 
        :class="{ loading: isLoadingMore, live: newsItems.length > 0 }"
      >
        {{ newsItems.length > 0 ? 'Live' : 'Loading...' }}
      </span>
    </div>
    
    <div 
      v-if="newsItems.length > 0" 
      class="news-list"
      ref="scrollContainer"
      @scroll="handleScroll"
    >
      <NewsItem 
        v-for="(item, index) in newsItems" 
        :key="item.id"
        :item="item"
        :is-new="index === 0"
      />
      
      <div v-if="isLoadingMore" class="loading-more">
        <div class="spinner-small"></div>
        <span>Loading more...</span>
      </div>
      
      <div v-if="allLoaded && newsItems.length > 0" class="all-loaded">
        <span>No more news</span>
      </div>

    </div>

    <div v-else class="empty-state glass-card">
      <p>No news yet. Waiting for updates...</p>
    </div>

    <ScrollToTop :target="scrollContainer" />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import NewsItem from './components/NewsItem.vue'
import ScrollToTop from '../UI/ScrollToTop.vue'
import './styles/NewsFeed.css'

const props = defineProps({
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

const emit = defineEmits(['load-more'])

const scrollContainer = ref(null)

const handleScroll = (event) => {
  const el = scrollContainer.value
  if (!el) return
  
  if (el.scrollTop + el.clientHeight >= el.scrollHeight - 50) {
    if (!props.isLoadingMore && !props.allLoaded) {
      emit('load-more')
    }
  }
}
</script>
