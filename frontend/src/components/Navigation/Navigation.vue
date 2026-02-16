<template>
  <div class="nav-tabs glass-card" ref="navContainer">
      <div class="sliding-indicator" :style="indicatorStyle"></div>
      <button 
        v-for="tab in tabs"
        :key="tab.id"
        class="nav-tab" 
        :class="{ active: activeTab === tab.id }"
        @click="$emit('set-tab', tab.id)"
      >
        {{ tab.label }}
      </button>
  </div>
</template>

<script setup>
import { ref, toRef } from 'vue'
import { useSlidingIndicator } from '../../composables/useSlidingIndicator'
import './styles/Navigation.css'

const props = defineProps({
  tabs: {
    type: Array,
    required: true
  },
  activeTab: {
    type: String,
    required: true
  }
})

defineEmits(['set-tab'])

const navContainer = ref(null)

const { indicatorStyle } = useSlidingIndicator(
    navContainer, 
    toRef(() => props.activeTab)
)
</script>
