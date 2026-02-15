<template>
  <div class="telegram-feed">
    <div class="feed-header">
      <div class="title-group">
        <h2 class="feed-title">
          Telegram Feed
        </h2>
        <p class="feed-disclaimer">
          Real-time updates. New messages appear instantly as they are received.
        </p>
      </div>
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
    </div>
    
    <div 
      v-if="messages.length > 0" 
      class="messages-list glass-card"
      ref="scrollContainer"
      @scroll="handleScroll"
    >
      <TelegramMessage 
        v-for="(msg, index) in messages" 
        :key="`${msg.channel_username}-${msg.id}`"
        :message="msg"
        :is-new="index === 0"
      />
      
      <div v-if="isLoadingMore" class="loading-more">
        <div class="spinner-small"></div>
        <span>Loading more...</span>
      </div>
      
      <div v-if="allLoaded && messages.length > 0" class="all-loaded">
        <span>No more messages</span>
      </div>
    </div>
    
    <div v-else class="empty-state glass-card">
      <div class="empty-icon"></div>
      <p>No messages yet. Waiting for updates...</p>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted, onUnmounted } from 'vue'
import TelegramMessage from './components/TelegramMessage.vue'
import './styles/TelegramFeed.css'

const props = defineProps({
  messages: {
    type: Array,
    default: () => []
  },
  isConnected: {
    type: Boolean,
    default: false
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

const isDemoMode = computed(() => {
  return props.messages.some(m => m.is_demo)
})

const statusText = computed(() => {
  if (!props.isConnected) return 'Disconnected'
  if (isDemoMode.value) return 'Demo Mode'
  return 'Live'
})

const handleScroll = () => {
  const el = scrollContainer.value
  if (!el) return
  
  // Check if scrolled to bottom (with 50px threshold)
  if (el.scrollTop + el.clientHeight >= el.scrollHeight - 50) {
    if (!props.isLoadingMore && !props.allLoaded) {
      emit('load-more')
    }
  }
}
</script>
