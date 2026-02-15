<template>
  <div class="news-feed">
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
        class="news-status-badge" 
        :class="{ loading: isLoadingMore }"
      >
        {{ newsItems.length > 0 ? `${newsItems.length} items` : 'Loading...' }}
      </span>
    </div>
    
    <div 
      v-if="newsItems.length > 0" 
      class="news-list glass-card"
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
      <div class="empty-icon">📰</div>
      <p>No news yet. Waiting for updates...</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import NewsItem from './components/NewsItem.vue'
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
  }
})

const emit = defineEmits(['load-more'])

const scrollContainer = ref(null)

const handleScroll = () => {
  const el = scrollContainer.value
  if (!el) return
  
  if (el.scrollTop + el.clientHeight >= el.scrollHeight - 50) {
    if (!props.isLoadingMore && !props.allLoaded) {
      emit('load-more')
    }
  }
}
</script>
