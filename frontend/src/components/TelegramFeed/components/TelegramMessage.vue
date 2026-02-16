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
    
    <div class="message-text" v-html="formattedText"></div>
    
    <div v-if="message.has_media || (message.media && message.media.length > 0)" class="message-media-preview" @click="showMedia = true">
      <div class="media-badge">
        <template v-if="message.media && message.media.length > 1">
          <span>📚 Album ({{ message.media.length }})</span>
        </template>
        <template v-else>
          <span v-if="displayMediaType === 'photo'">🖼 Photo</span>
          <span v-else-if="displayMediaType === 'video'">🎥 Video</span>
          <span v-else-if="displayMediaType === 'gif'">🎬 GIF</span>
        </template>
      </div>
    </div>
    
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

    <MediaModal 
      :show="showMedia" 
      :media-list="message.media || []"
      :initial-media-url="message.media_url" 
      :initial-media-type="message.media_type" 
      @close="showMedia = false"
    />
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import MediaModal from './MediaModal.vue'
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

const showMedia = ref(false)

const avatarLetter = computed(() => {
  return props.message.channel_title?.charAt(0)?.toUpperCase() || '?'
})

const formattedTime = computed(() => {
  const date = new Date(props.message.date)
  return date.toLocaleTimeString('ru-RU', { 
    hour: '2-digit', 
    minute: '2-digit',
    second: '2-digit'
  })
})

const formattedViews = computed(() => {
  const views = props.message.views || 0
  if (views >= 1000000) return (views / 1000000).toFixed(1) + 'M'
  if (views >= 1000) return (views / 1000).toFixed(1) + 'K'
  return views.toString()
})

const formattedText = computed(() => {
  if (!props.message.text) return ''
  
  let text = props.message.text
  text = text.replace(/\[([^\]]+)\]\(tg:\/\/search_hashtag[^\s)]*\)/g, '$1')
  text = text.replace(/\*{3,}/g, '')
  text = text.replace(/-{3,}/g, '')
  text = text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
  text = text.replace(/\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g, (match, linkText, url) => {
    return `<a href="${url}" target="_blank" rel="noopener noreferrer">${linkText}</a>`
  })

  const urlRegex = /(?<![\]\(]|href=")(https?:\/\/[^\s<]+)(?![^<]*?<\/a>)/g
  text = text.replace(urlRegex, (url) => {
    return `<a href="${url}" target="_blank" rel="noopener noreferrer">${url}</a>`
  })

  text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
  text = text.replace(/#\s+/g, '#')
  text = text.replace(/(^|\s)(#[\w\u0400-\u04FF]+)/g, '$1<span class="hashtag">$2</span>')
  text = text.replace(/\n{3,}/g, '\n\n')
  text = text.replace(/\n/g, '<br>')
  
  return text
})

const displayMediaType = computed(() => {
  if (props.message.media && props.message.media.length > 0) {
    return props.message.media[0].type
  }
  return props.message.media_type
})
</script>
