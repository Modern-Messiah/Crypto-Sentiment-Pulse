<template>
  <div class="gauge-container">
    <svg viewBox="0 0 200 110" class="gauge-svg">
      <path d="M 20 100 A 80 80 0 0 1 180 100" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="20" stroke-linecap="round" />
      
      <defs>
        <linearGradient id="gaugeGradient" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stop-color="#ff4757" />
          <stop offset="25%" stop-color="#ffa502" />
          <stop offset="50%" stop-color="#eccc68" />
          <stop offset="75%" stop-color="#7bed9f" />
          <stop offset="100%" stop-color="#2ed573" />
        </linearGradient>
      </defs>
      <path d="M 20 100 A 80 80 0 0 1 180 100" fill="none" stroke="url(#gaugeGradient)" stroke-width="20" stroke-linecap="round" />

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
</template>

<script setup>
defineProps({
  value: {
    type: [Number, String],
    required: true
  },
  needleRotation: {
    type: Number,
    required: true
  },
  scoreColor: {
    type: String,
    required: true
  }
})
</script>
