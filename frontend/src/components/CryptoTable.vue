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
          <!-- Use a component for row to handle individual watchers -->
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
import { ref, computed, defineProps } from 'vue'
import CryptoTableRow from './CryptoTableRow.vue'

const props = defineProps({
  prices: {
    type: Object,
    required: true
  }
})

const searchQuery = ref('')
const sortKey = ref('change_24h')
const sortOrder = ref('desc')

const pricesArray = computed(() => {
  return Object.values(props.prices)
})

const filteredPrices = computed(() => {
  const query = searchQuery.value.toLowerCase().trim()
  if (!query) return pricesArray.value
  
  return pricesArray.value.filter(coin => 
    coin.symbol.toLowerCase().includes(query)
  )
})

const sortedPrices = computed(() => {
  return [...filteredPrices.value].sort((a, b) => {
    let modifier = sortOrder.value === 'asc' ? 1 : -1
    
    if (sortKey.value === 'symbol') {
      return a.symbol.localeCompare(b.symbol) * modifier
    }
    
    return (a[sortKey.value] - b[sortKey.value]) * modifier
  })
})

function sortBy(key) {
  if (sortKey.value === key) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortKey.value = key
    sortOrder.value = 'desc'
  }
}
</script>

<style scoped>
.table-container {
  padding: 1.5rem;
  overflow: hidden;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.table-header h3 {
  font-size: 1.25rem;
  margin: 0;
}

.search-box {
  position: relative;
  width: 250px;
}

.search-input {
  width: 100%;
  padding: 0.5rem 1rem 0.5rem 2.5rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: var(--radius-md);
  color: var(--text-primary);
  font-family: inherit;
  transition: all var(--transition-fast);
}

.search-input:focus {
  outline: none;
  border-color: var(--accent-primary);
  background: rgba(255, 255, 255, 0.08);
}

.search-icon {
  position: absolute;
  left: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  font-size: 0.9rem;
  opacity: 0.5;
}

.table-responsive {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-muted);
  font-weight: 600;
  cursor: pointer;
  user-select: none;
  transition: color var(--transition-fast);
}

th:hover {
  color: var(--text-primary);
}

.sortable {
  position: relative;
}

.sort-icon {
  display: inline-block;
  opacity: 0;
  transition: opacity 0.2s;
  font-size: 0.7rem;
  margin-left: 4px;
}

.sort-icon.active {
  opacity: 1;
}

.empty-state {
  text-align: center;
  padding: 2rem;
  color: var(--text-muted);
}

@media (max-width: 600px) {
  .mobile-hide {
    display: none;
  }
  
  .table-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .search-box {
    width: 100%;
  }
  
  th {
    padding: 0.75rem 0.5rem;
  }
}
</style>
