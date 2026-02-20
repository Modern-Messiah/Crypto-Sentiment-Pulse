<template>
  <td class="text-right">
    <span class="change-pill" :class="getChangeClass(change)">
      {{ formatChange(change) }}
    </span>
  </td>
</template>

<script setup>
import { formatChange, getChangeClass } from '@/utils/formatters'

defineProps({
  change: {
    type: [Number, String],
    required: true
  }
})
</script>
