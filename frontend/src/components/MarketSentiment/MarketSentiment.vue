<template>
  <div class="market-sentiment glass-card">
    <div class="sentiment-header">
      <h3>Market Sentiment</h3>
      <span class="live-update" v-if="timeUntilUpdate">Update in {{ formattedTimeUntil }}</span>
    </div>

    <div class="sentiment-content" v-if="!loading && !error">
      <SentimentGauge 
        :value="value"
        :needle-rotation="needleRotation"
        :score-color="scoreColor"
      />

      <SentimentInfo 
        :classification="classification"
        :score-color="scoreColor"
      />
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
import { useMarketSentiment } from './hooks/useMarketSentiment.js'
import SentimentGauge from './components/SentimentGauge.vue'
import SentimentInfo from './components/SentimentInfo.vue'
import './styles/MarketSentiment.css'

const {
    value,
    classification,
    loading,
    error,
    timeUntilUpdate,
    formattedTimeUntil,
    needleRotation,
    scoreColor
} = useMarketSentiment()
</script>
