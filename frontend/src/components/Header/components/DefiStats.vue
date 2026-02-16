<template>
  <div v-if="stats.total_tvl" class="defi-stats">
    <div class="stat-item">
      <span class="stat-label">Global DeFi TVL</span>
      <span class="stat-value">{{ formatTVL(stats.total_tvl) }}</span>
    </div>
    <div class="stat-divider"></div>
    <div class="stat-item">
      <span class="stat-label">Chains</span>
      <span class="stat-value">{{ stats.chain_count }}</span>
    </div>
  </div>
</template>

<script setup>
import '../styles/DefiStats.css'

defineProps({
  stats: {
    type: Object,
    default: () => ({})
  }
})

const formatTVL = (value) => {
  if (!value) return '$0';
  if (value >= 1e9) return '$' + (value / 1e9).toFixed(1) + 'B';
  if (value >= 1e6) return '$' + (value / 1e6).toFixed(0) + 'M';
  return '$' + Math.round(value).toLocaleString();
};
</script>


