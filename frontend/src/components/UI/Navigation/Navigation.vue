<template>
  <SlidingToggle
    :model-value="activeTab"
    @update:model-value="$emit('set-tab', $event)"
    :items="tabs"
    container-class="nav-tabs glass-card"
    item-class="nav-tab"
  />
</template>

<script setup>
import SlidingToggle from '../SlidingToggle/SlidingToggle.vue'
import './styles/Navigation.css'

defineProps({
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
</script>
