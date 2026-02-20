<template>
  <thead>
    <tr>
      <th @click="$emit('sort', 'symbol')" class="sortable">
        Asset
        <span class="sort-icon" :class="{ active: sortKey === 'symbol' }">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
      </th>
      <th @click="$emit('sort', 'price')" class="sortable text-right">
        Price
        <span class="sort-icon" :class="{ active: sortKey === 'price' }">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
      </th>
      <th @click="$emit('sort', 'change_24h')" class="sortable text-right">
        24h Change
        <span class="sort-icon" :class="{ active: sortKey === 'change_24h' }">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
      </th>
      <th @click="$emit('sort', 'rsi')" class="sortable text-right">
        RSI (14)
        <span class="sort-icon" :class="{ active: sortKey === 'rsi' }">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
      </th>
      <th @click="$emit('sort', 'tvl')" class="sortable text-right mobile-hide">
        TVL
        <span class="sort-icon" :class="{ active: sortKey === 'tvl' }">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
      </th>
      <th @click="$emit('sort', 'volume_24h')" class="sortable text-right mobile-hide">
        24h Volume
        <span class="sort-icon" :class="{ active: sortKey === 'volume_24h' }">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
      </th>
    </tr>
  </thead>
</template>

<script setup>
defineProps({
  sortKey: String,
  sortOrder: String
})

defineEmits(['sort'])
</script>
