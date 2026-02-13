<template>
  <div class="news-item" :class="{ new: isNew }">
    <div class="news-header">
      <div class="source-info">
        <div class="source-avatar">{{ avatarLetter }}</div>
        <div>
          <div class="source-name">{{ displaySource }}</div>
          <span class="kind-badge">{{ item.kind }}</span>
        </div>
      </div>
      <div class="news-time">{{ formattedTime }}</div>
    </div>
    
    <div class="news-title">{{ item.title }}</div>
    
    <div v-if="item.description" class="news-description">
      {{ item.description }}
    </div>
    
    <div class="news-footer">
      <a 
        v-if="item.url" 
        :href="item.url" 
        target="_blank" 
        rel="noopener noreferrer"
        class="read-more-link"
      >
        Read more →
      </a>
      <div class="news-date">{{ formattedDate }}</div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import '../styles/NewsItem.css'

const props = defineProps({
  item: {
    type: Object,
    required: true
  },
  isNew: {
    type: Boolean,
    default: false
  }
})

const avatarLetter = computed(() => {
  if (props.item.source_title) {
    return props.item.source_title.charAt(0).toUpperCase()
  }
  return '📰'
})

const displaySource = computed(() => {
  return props.item.source_title || 'CryptoPanic'
})

const formattedTime = computed(() => {
  const date = new Date(props.item.published_at)
  return date.toLocaleTimeString('en-US', { 
    hour: '2-digit', 
    minute: '2-digit'
  })
})

const formattedDate = computed(() => {
  const date = new Date(props.item.published_at)
  return date.toLocaleDateString('en-US', {
    day: 'numeric',
    month: 'short'
  })
})
</script>
