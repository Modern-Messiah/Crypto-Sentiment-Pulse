<template>
  <div class="telegram-message" :class="{ new: isNew }">
    <div class="message-header">
      <div class="channel-info">
        <div class="channel-avatar">{{ avatarLetter }}</div>
        <div>
          <div class="channel-name">{{ message.channel_title }}</div>
          <div class="channel-username">@{{ message.channel_username }}</div>
        </div>
      </div>
      <div class="message-time">{{ formattedTime }}</div>
    </div>
    
    <div class="message-text">{{ message.text }}</div>
    
    <div class="message-footer">
      <div class="message-stat">
        <span>👁</span>
        <span>{{ formattedViews }}</span>
      </div>
      <div class="message-stat">
        <span>↗</span>
        <span>{{ message.forwards }}</span>
      </div>
      <span v-if="message.is_demo" class="demo-badge">DEMO</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import '../styles/TelegramMessage.css'

const props = defineProps({
  message: {
    type: Object,
    required: true
  },
  isNew: {
    type: Boolean,
    default: false
  }
})

const avatarLetter = computed(() => {
  return props.message.channel_title?.charAt(0)?.toUpperCase() || '?'
})

const formattedTime = computed(() => {
  const date = new Date(props.message.date)
  return date.toLocaleTimeString('ru-RU', { 
    hour: '2-digit', 
    minute: '2-digit' 
  })
})

const formattedViews = computed(() => {
  const views = props.message.views || 0
  if (views >= 1000000) return (views / 1000000).toFixed(1) + 'M'
  if (views >= 1000) return (views / 1000).toFixed(1) + 'K'
  return views.toString()
})
</script>
