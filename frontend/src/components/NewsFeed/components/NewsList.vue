<template>
  <div 
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
    
    <ScrollToTop :target="scrollContainer" />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import NewsItem from './NewsItem.vue'
import ScrollToTop from '../../UI/ScrollToTop/ScrollToTop.vue'

const props = defineProps({
  newsItems: {
    type: Array,
    required: true
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

<style scoped>
@import '../styles/NewsList.css';
</style>
