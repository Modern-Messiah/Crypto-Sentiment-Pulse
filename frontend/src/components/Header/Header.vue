<template>
  <header class="header" :class="{ hidden: isHidden }">
    <div class="header-content">
      <div class="header-left">
        <Logo />
        <DefiStats :stats="globalStats" />
      </div>
      
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
import DefiStats from './components/DefiStats.vue'
import { useHeader } from './hooks/useHeader.js'
import './styles/Header.css'

const props = defineProps({
  isConnected: Boolean,
  lastUpdate: [Date, null],
  activeTab: String,
  isHidden: Boolean,
  globalStats: {
    type: Object,
    default: () => ({})
  }
})

const { formatTime } = useHeader()
</script>
