<template>
  <td class="text-right font-mono">
    <div class="price-cell">{{ formatPrice(price) }}</div>
  </td>
</template>

<script setup>
import { formatPrice } from '@/utils/formatters'

defineProps({
  price: [Number, String]
})
</script>
