<template>
  <div class="dashboard-content">
    <div v-if="hasData">
      <div class="toolbar glass-card">
        <SlidingToggle
          :model-value="filterMode"
          @update:model-value="$emit('update:filterMode', $event)"
          :items="filters"
          container-class="filter-group"
          item-class="control-btn"
          indicator-class="filter-indicator"
        />

        <SlidingToggle
          :model-value="viewMode"
          @update:model-value="$emit('set-view-mode', $event)"
          :items="[
            { id: 'grid', label: '⊞', title: 'Grid View' },
            { id: 'table', label: '☰', title: 'Table View' }
          ]"
          container-class="view-group"
          item-class="control-btn icon-btn"
          indicator-class="view-indicator"
        />
      </div>

      <div class="view-container">
        <Transition :name="viewTransitionName">
          <div :key="viewMode" class="view-wrapper">
            <template v-if="viewMode === 'grid'">
              <Transition name="filter-fade" mode="out-in">
                <TransitionGroup 
                  :key="filterMode"
                  name="list" 
                  tag="div" 
                  class="cards-grid"
                >
                  <div 
                    v-for="(coin, index) in displayPrices" 
                    :key="coin.symbol"
                    class="card-wrapper"
                    :style="{ '--i': index }"
                  >
                    <CryptoCard 
                      :symbol="coin.symbol"
                      :data="coin"
                      @toggle-expand="(sym, isOpen) => $emit('toggle-expand', sym, isOpen)"
                    />
                  </div>
                </TransitionGroup>
              </Transition>
            </template>
            
            <div v-else class="table-wrapper">
              <CryptoTable :prices="displayPricesArray" />
            </div>
          </div>
        </Transition>
      </div>
      <ScrollToTop :is-fixed="true" />
    </div>
    
    <div v-else class="loading-state">
      <div class="spinner"></div>
      <p>Connecting to live market data...</p>
    </div>
  </div>
</template>

<script setup>
import CryptoCard from '../../CryptoCard/CryptoCard.vue'
import CryptoTable from '../../CryptoTable/CryptoTable.vue'
import ScrollToTop from '../ScrollToTop/ScrollToTop.vue'
import SlidingToggle from '../SlidingToggle/SlidingToggle.vue'
import './styles/Dashboard.css'

const props = defineProps({
  hasData: Boolean,
  filters: Array,
  filterMode: String,
  viewMode: String,
  viewTransitionName: String,
  displayPrices: Array,
  displayPricesArray: Object
})

defineEmits(['update:filterMode', 'set-view-mode', 'toggle-expand'])
</script>
