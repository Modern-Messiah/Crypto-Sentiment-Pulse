<template>
  <Teleport to="body">
    <Transition name="fade">
      <div v-if="show" class="media-modal-overlay" @click.self="$emit('close')">
        <button class="close-btn" @click="$emit('close')" aria-label="Close">×</button>
        
        <div class="media-container" @click.stop>
          <button 
            v-if="hasMultiple" 
            class="nav-btn prev" 
            @click="prevMedia"
            aria-label="Previous"
          >
            ‹
          </button>

          <div class="media-wrapper">
            <img 
              v-if="currentMedia.type === 'photo'" 
              :src="getMediaUrl(currentMedia.url)" 
              class="media-content"
              alt="Telegram Media Content"
            />
            <video 
              v-else-if="currentMedia.type === 'video' || currentMedia.type === 'gif'"
              :src="getMediaUrl(currentMedia.url)"
              class="media-content"
              controls
              :autoplay="currentMedia.type === 'gif'"
              :loop="currentMedia.type === 'gif'"
              :muted="currentMedia.type === 'gif'"
              playsinline
            ></video>
          </div>

          <button 
            v-if="hasMultiple" 
            class="nav-btn next" 
            @click="nextMedia"
            aria-label="Next"
          >
            ›
          </button>

          <div v-if="hasMultiple" class="media-counter">
            {{ currentIndex + 1 }} / {{ items.length }}
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { computed, ref, watch, onMounted, onUnmounted } from 'vue'
import '../styles/MediaModal.css'

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  mediaList: {
    type: Array,
    default: () => []
  },
  initialMediaUrl: {
    type: String,
    default: ''
  },
  initialMediaType: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['close'])

const currentIndex = ref(0)

const items = computed(() => {
  if (props.mediaList && props.mediaList.length > 0) {
    return props.mediaList
  }
  if (props.initialMediaUrl) {
    return [{
      url: props.initialMediaUrl,
      type: props.initialMediaType
    }]
  }
  return []
})

const currentMedia = computed(() => {
  return items.value[currentIndex.value] || { url: '', type: '' }
})

const hasMultiple = computed(() => items.value.length > 1)

const nextMedia = () => {
  if (currentIndex.value < items.value.length - 1) {
    currentIndex.value++
  } else {
    currentIndex.value = 0
  }
}

const prevMedia = () => {
  if (currentIndex.value > 0) {
    currentIndex.value--
  } else {
    currentIndex.value = items.value.length - 1
  }
}

const getMediaUrl = (url) => {
  if (!url) return ''
  if (url.startsWith('http')) return url
  if (import.meta.env.PROD) return url
  const apiBase = 'http://localhost:8080'
  return `${apiBase}${url}`
}

watch(() => props.show, (newVal) => {
  if (newVal) {
    currentIndex.value = 0
    document.addEventListener('keydown', handleKeyDown)
  } else {
    document.removeEventListener('keydown', handleKeyDown)
  }
})

const handleKeyDown = (e) => {
  if (e.key === 'ArrowRight') nextMedia()
  if (e.key === 'ArrowLeft') prevMedia()
  if (e.key === 'Escape') emit('close')
}

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeyDown)
})
</script>
