<template>
  <td class="text-right font-mono mobile-hide">
    <div class="tvl-content">
      <span class="tvl-value">{{ formatTvl(tvl) }}</span>
      <span class="tvl-change" :class="getTvlChangeClass(change)">
        {{ formatTvlChange(change) }}
      </span>
    </div>
  </td>
</template>

<script setup>
import { formatTvl, formatTvlChange, getTvlChangeClass } from '@/utils/formatters'

defineProps({
  tvl: [Number, String],
  change: [Number, String]
})
</script>
