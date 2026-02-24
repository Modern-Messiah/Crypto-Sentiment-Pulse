<template>
  <Transition name="fade">
    <button 
      v-if="isVisible" 
      class="scroll-to-top-btn"
      :class="{ 'is-fixed': isFixed }"
      @click="scrollToTop"
      aria-label="Scroll to top"
    >
      <span class="arrow-up">↑</span>
    </button>
  </Transition>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import './styles/ScrollToTop.css'

const props = defineProps({
  target: {
    type: [Object, String],
    default: null
  },
  isFixed: {
    type: Boolean,
    default: false
  }
})

const isVisible = ref(false)
const threshold = 150

const getTargetEl = (target) => {
    if (!target) return window
    if (target.value !== undefined) return target.value
    if (typeof target === 'string') return document.querySelector(target)
    return target
}

const handleScroll = (event) => {
    const el = getTargetEl(props.target)
    const scrollTop = el === window ? window.scrollY : el.scrollTop
    isVisible.value = scrollTop > threshold
}

const scrollToTop = () => {
    const el = getTargetEl(props.target)
    if (el === window) {
        window.scrollTo({ top: 0 })
    } else {
        el.scrollTo({ top: 0 })
    }
}

const setupListener = (target) => {
    const el = getTargetEl(target)
    if (!el) return
    el.addEventListener('scroll', handleScroll, { passive: true })
}

const removeListener = (target) => {
    const el = getTargetEl(target)
    if (!el) return
    el.removeEventListener('scroll', handleScroll)
}

watch(() => props.target, (newTarget, oldTarget) => {
    removeListener(oldTarget)
    setupListener(newTarget)
}, { immediate: true, deep: true })

onMounted(() => {
    if (!props.target) {
        setupListener(window)
    }
})

onUnmounted(() => {
    const el = props.target || window
    removeListener(el)
})
</script>
