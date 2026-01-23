<template>
  <header class="header">
    <div class="header-content">
      <div class="logo">
        <div class="logo-icon">₿</div>
        <div class="logo-text">
          <h1>Crypto<span class="gradient-text">Pulse</span></h1>
          <p class="tagline">Real-time prices</p>
        </div>
      </div>
      
      <div class="status">
        <div class="status-indicator" :class="{ connected: isConnected }">
          <span class="dot"></span>
          <span class="status-text">{{ isConnected ? 'Live' : 'Connecting...' }}</span>
        </div>
        <div v-if="lastUpdate" class="last-update">
          Updated: {{ formatTime(lastUpdate) }}
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
import { useHeader } from './Header.js'
import './Header.css'

defineProps({
  isConnected: Boolean,
  lastUpdate: Date
})

const { formatTime } = useHeader()
</script>
