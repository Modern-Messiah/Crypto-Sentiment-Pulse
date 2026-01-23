<template>
  <div class="glass-card table-container">
    <div class="table-header">
      <h3>Market Overview</h3>
      <div class="search-box">
        <span class="search-icon"></span>
        <input 
          type="text" 
          v-model="searchQuery" 
          placeholder="Search coin..." 
          class="search-input"
        >
      </div>
    </div>
    
    <div class="table-responsive">
      <table>
        <thead>
          <tr>
            <th @click="sortBy('symbol')" class="sortable">
              Asset
              <span class="sort-icon" :class="{ active: sortKey === 'symbol' }">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
            </th>
            <th @click="sortBy('price')" class="sortable text-right">
              Price
              <span class="sort-icon" :class="{ active: sortKey === 'price' }">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
            </th>
            <th @click="sortBy('change_24h')" class="sortable text-right">
              24h Change
              <span class="sort-icon" :class="{ active: sortKey === 'change_24h' }">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
            </th>
            <th @click="sortBy('volume_24h')" class="sortable text-right mobile-hide">
              24h Volume
              <span class="sort-icon" :class="{ active: sortKey === 'volume_24h' }">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
            </th>
          </tr>
        </thead>
        <tbody>
          <CryptoTableRow 
            v-for="coin in sortedPrices" 
            :key="coin.symbol" 
            :coin="coin"
          />
          <tr v-if="sortedPrices.length === 0">
            <td colspan="4" class="empty-state">
              No coins found
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { useCryptoTable } from './CryptoTable.js'
import CryptoTableRow from '../CryptoTableRow/index.vue'
import './CryptoTable.css'

const props = defineProps({
  prices: {
    type: Object,
    required: true
  }
})

const { searchQuery, sortKey, sortOrder, sortedPrices, sortBy } = useCryptoTable(props)
</script>
