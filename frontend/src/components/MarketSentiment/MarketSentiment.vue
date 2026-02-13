<template>
  <div class="market-sentiment glass-card">
    <div class="sentiment-header">
      <h3>Market Sentiment</h3>
      <span class="live-update" v-if="timeUntilUpdate">Update in {{ formattedTimeUntil }}</span>
    </div>

    <div class="sentiment-content" v-if="!loading && !error">
      
      <!-- Speedometer Gauge -->
      <div class="gauge-container">
        <svg viewBox="0 0 200 110" class="gauge-svg">
          <!-- Background Arc -->
          <path d="M 20 100 A 80 80 0 0 1 180 100" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="20" stroke-linecap="round" />
          
          <!-- Colored Segments (Gradient approach) -->
          <defs>
            <linearGradient id="gaugeGradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stop-color="#ff4757" />   <!-- Ext Fear -->
              <stop offset="25%" stop-color="#ffa502" />  <!-- Fear -->
              <stop offset="50%" stop-color="#eccc68" />  <!-- Neutral -->
              <stop offset="75%" stop-color="#7bed9f" />  <!-- Greed -->
              <stop offset="100%" stop-color="#2ed573" /> <!-- Ext Greed -->
            </linearGradient>
          </defs>
          <path d="M 20 100 A 80 80 0 0 1 180 100" fill="none" stroke="url(#gaugeGradient)" stroke-width="20" stroke-linecap="round" />

          <!-- Needle -->
          <line 
            x1="100" y1="100" 
            x2="100" y2="35" 
            stroke="white" 
            stroke-width="4" 
            stroke-linecap="round"
            :transform="`rotate(${needleRotation}, 100, 100)`"
            class="gauge-needle"
          />
          <circle cx="100" cy="100" r="6" fill="white" />
        </svg>
        
        <div class="score-display" :style="{ color: scoreColor }">
          <span class="score-value">{{ value }}</span>
        </div>
      </div>

      <div class="sentiment-info">
        <div class="sentiment-label" :style="{ color: scoreColor }">
          {{ classification }}
        </div>
        <div class="sentiment-desc">
          Fear & Greed Index
        </div>
      </div>

    </div>

    <div v-if="loading" class="loading-state-mini">
      <div class="spinner-mini"></div>
    </div>

    <div v-if="error" class="error-mini">
      Unknown
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, onUnmounted } from 'vue'
import './MarketSentiment.css'

const value = ref(50)
const classification = ref('Neutral')
const loading = ref(true)
const error = ref(null)
const timeUntilUpdate = ref(null) // seconds string from API or calculated

const API_URL = import.meta.env.VITE_API_URL || '/api/v1'

const fetchData = async () => {
    try {
        loading.value = true
        const res = await fetch(`${API_URL}/sentiment/fear-greed`)
        const data = await res.json()
        
        if (data.error) {
            throw new Error(data.error)
        }
        
        value.value = data.value
        classification.value = data.value_classification
        timeUntilUpdate.value = data.time_until_update // API might return explicit time or we calc it
        
        // If API returns seconds until update, good. If not, ignore.
        
    } catch (e) {
        error.value = e.message
        console.error("Sentiment fetch error:", e)
    } finally {
        loading.value = false
    }
}

// Calculate needle rotation: 0 to 100 -> -90deg to 90deg
const needleRotation = computed(() => {
    const deg = (value.value / 100) * 180 - 90
    return Math.max(-90, Math.min(90, deg))
})

// Color based on value
const scoreColor = computed(() => {
    const v = value.value
    if (v < 25) return '#ff4757' // Ext Fear
    if (v < 45) return '#ffa502' // Fear
    if (v < 55) return '#eccc68' // Neutral
    if (v < 75) return '#7bed9f' // Greed
    return '#2ed573' // Ext Greed
})

const formattedTimeUntil = computed(() => {
    if (!timeUntilUpdate.value) return ''
    const sec = parseInt(timeUntilUpdate.value)
    if (isNaN(sec)) return ''
    const h = Math.floor(sec / 3600)
    const m = Math.floor((sec % 3600) / 60)
    return `${h}h ${m}m`
})

onMounted(() => {
    fetchData()
    // Refresh every 5 min
    const interval = setInterval(fetchData, 5 * 60 * 1000)
    onUnmounted(() => clearInterval(interval))
})
</script>
