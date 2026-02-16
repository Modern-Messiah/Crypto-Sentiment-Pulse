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

<style scoped>
.defi-stats {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  padding: 0 0.5rem;
  font-size: 0.8rem;
}

.stat-item {
  display: flex;
  align-items: baseline;
  gap: 0.4rem;
}

.stat-label {
  font-size: 0.65rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  white-space: nowrap;
}

.stat-value {
  font-weight: 600;
  color: var(--text-primary);
  font-family: var(--font-mono, monospace);
}

.stat-divider {
  width: 1px;
  height: 12px;
  background: rgba(255, 255, 255, 0.1);
}

@media (max-width: 600px) {
  .defi-stats {
    display: none;
  }
}
</style>
