<template>
  <div class="glass-card table-container">
    <div class="table-header">
      <h3>Market Overview</h3>
      <TableSearch v-model="searchQuery" />
    </div>
    
    <div class="table-responsive">
      <table>
        <TableHeader 
          :sort-key="sortKey" 
          :sort-order="sortOrder" 
          @sort="sortBy"
        />
        <TransitionGroup tag="tbody" name="table-row">
          <CryptoTableRow 
            v-for="coin in sortedPrices" 
            :key="coin.symbol" 
            :coin="coin"
          />
          <tr v-if="sortedPrices.length === 0" key="empty-state">
            <td colspan="6" class="empty-state">
              No coins found
            </td>
          </tr>
        </TransitionGroup>
      </table>
    </div>
  </div>
</template>

<script setup>
import { useCryptoTable } from './hooks/useCryptoTable.js'
import TableHeader from './components/TableHeader.vue'
import TableSearch from './components/TableSearch.vue'
import CryptoTableRow from '../CryptoTableRow/CryptoTableRow.vue'
import './styles/CryptoTable.css'

const props = defineProps({
  prices: {
    type: Object,
    required: true
  }
})

const { searchQuery, sortKey, sortOrder, sortedPrices, sortBy } = useCryptoTable(props)
</script>
