<template>
  <td class="text-right font-mono">
    <span :class="getRsiClass(rsi)">
      {{ formatRsi(rsi) }}
    </span>
  </td>
</template>

<script setup>
import { formatRsi, getRsiClass } from '@/utils/formatters'

defineProps({
  rsi: [Number, String]
})
</script>
