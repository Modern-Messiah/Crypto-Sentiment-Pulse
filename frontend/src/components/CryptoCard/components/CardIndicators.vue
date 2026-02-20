<template>
  <div class="card-indicators">
    <div v-if="data.tvl" class="tvl-container">
      <div class="tvl-info">
        <span class="tvl-label" title="Total Value Locked - the total amount of assets currently being held in this network or protocol.">TVL</span>
        <div class="tvl-values">
          <span class="tvl-value">{{ formatTvl(data.tvl) }}</span>
          <span v-if="data.tvl_change_1d !== undefined" 
                class="tvl-change" 
                :class="data.tvl_change_1d >= 0 ? 'text-success' : 'text-danger'">
            {{ data.tvl_change_1d >= 0 ? '+' : '' }}{{ data.tvl_change_1d.toFixed(1) }}%
          </span>
        </div>
      </div>

      <div v-if="data.money_flow_24h" class="flow-info">
        <span class="tvl-label">Money Flow (24h)</span>
        <span class="tvl-value" :class="data.money_flow_24h >= 0 ? 'text-success' : 'text-danger'">
          {{ formatMoneyFlow(data.money_flow_24h) }}
        </span>
      </div>
    </div>
    
    <div class="rsi-container" v-if="data.rsi !== undefined && data.rsi !== null">
      <div class="rsi-info">
        <span class="rsi-label" title="Relative Strength Index (14-period) - a momentum oscillator that measures the speed and change of price movements.">RSI (14)</span>
        <span class="rsi-value" :class="getRsiClass(data.rsi)">{{ data.rsi }}</span>
      </div>
      <div class="rsi-track">
        <div 
          class="rsi-bar" 
          :style="{ width: `${data.rsi}%`, backgroundColor: getRsiColor(data.rsi) }"
        ></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { formatTvl, formatMoneyFlow, getRsiColor, getRsiClass } from '../utils/formatters'

defineProps({
  data: {
    type: Object,
    required: true
  }
})
</script>
