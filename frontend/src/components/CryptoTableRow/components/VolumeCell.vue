<template>
  <td class="text-right mobile-hide text-muted">
    {{ formatVolume(volume) }}
  </td>
</template>

<script setup>
import { formatVolume } from '@/utils/formatters'

defineProps({
  volume: [Number, String]
})
</script>
