<template>
  <header class="header" :class="{ hidden: isHidden }">
    <div class="header-content">
      <Logo />
      
      <StatusIndicator 
        :is-connected="isConnected" 
        :last-update="lastUpdate"
        :format-time="formatTime"
      />
    </div>
  </header>
</template>

<script setup>
import Logo from './components/Logo.vue'
import StatusIndicator from './components/StatusIndicator.vue'
import { useHeader } from './hooks/useHeader.js'
import { useHeaderVisibility } from './hooks/useHeaderVisibility.js'
import './styles/Header.css'

defineProps({
  isConnected: Boolean,
  lastUpdate: [Date, null]
})

const { formatTime } = useHeader()
const { isHidden } = useHeaderVisibility()
</script>
