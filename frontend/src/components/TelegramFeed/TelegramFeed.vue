<template>
  <div class="telegram-feed" :class="{ 'header-hidden': isHeaderHidden }">
    <FeedHeader 
      :is-connected="isConnected" 
      :is-demo-mode="isDemoMode" 
    />
    
    <MessageList 
      v-if="messages.length > 0"
      :messages="messages"
      :is-loading-more="isLoadingMore"
      :all-loaded="allLoaded"
      @load-more="$emit('load-more')"
    />

    <EmptyState v-else />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import FeedHeader from './components/FeedHeader.vue'
import MessageList from './components/MessageList.vue'
import EmptyState from './components/EmptyState.vue'
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
  },
  isHeaderHidden: {
    type: Boolean,
    default: false
  }
})

defineEmits(['load-more'])

const isDemoMode = computed(() => {
  return props.messages.some(m => m.is_demo)
})
</script>
