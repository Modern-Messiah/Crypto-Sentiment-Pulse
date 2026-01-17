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
import { defineProps } from 'vue'

const props = defineProps({
  isConnected: Boolean,
  lastUpdate: Date
})

const formatTime = (date) => {
  if (!date) return ''
  return date.toLocaleTimeString('ru-RU', { 
    hour: '2-digit', 
    minute: '2-digit',
    second: '2-digit'
  })
}
</script>

<style scoped>
.header {
  position: sticky;
  top: 0;
  z-index: 100;
  padding: 1rem 2rem;
  background: rgba(15, 15, 26, 0.8);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.logo-icon {
  width: 48px;
  height: 48px;
  background: var(--gradient-primary);
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  font-weight: 700;
  box-shadow: var(--shadow-glow);
}

.logo-text h1 {
  font-size: 1.5rem;
  font-weight: 700;
  line-height: 1.2;
}

.tagline {
  font-size: 0.75rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

.status {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: rgba(255, 71, 87, 0.1);
  border: 1px solid rgba(255, 71, 87, 0.3);
  border-radius: var(--radius-xl);
  transition: all var(--transition-normal);
}

.status-indicator.connected {
  background: rgba(0, 208, 132, 0.1);
  border-color: rgba(0, 208, 132, 0.3);
}

.dot {
  width: 8px;
  height: 8px;
  background: var(--danger);
  border-radius: 50%;
  animation: pulse 2s ease-in-out infinite;
}

.status-indicator.connected .dot {
  background: var(--success);
}

.status-text {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--danger);
}

.status-indicator.connected .status-text {
  color: var(--success);
}

.last-update {
  font-size: 0.75rem;
  color: var(--text-muted);
}

@media (max-width: 768px) {
  .header {
    padding: 1rem;
  }
  
  .header-content {
    flex-direction: column;
    gap: 1rem;
  }
  
  .status {
    width: 100%;
    justify-content: center;
  }
}
</style>
