<template>
  <div class="dashboard-content">
    <div v-if="hasData">
      <div class="toolbar glass-card">
        <div class="filter-group" ref="filterContainer">
          <div class="sliding-indicator filter-indicator" :style="filterIndicatorStyle"></div>
          <button 
            v-for="f in filters" 
            :key="f.id"
            class="control-btn"
            :class="{ active: filterMode === f.id }"
            @click="$emit('update:filterMode', f.id)"
          >
            {{ f.label }}
          </button>
        </div>

        <div class="view-group" ref="viewContainer">
          <div class="sliding-indicator view-indicator" :style="viewIndicatorStyle"></div>
          <button 
            class="control-btn icon-btn"
            :class="{ active: viewMode === 'grid' }"
            @click="$emit('set-view-mode', 'grid')"
            title="Grid View"
          >
            ⊞
          </button>
          <button 
            class="control-btn icon-btn"
            :class="{ active: viewMode === 'table' }"
            @click="$emit('set-view-mode', 'table')"
            title="Table View"
          >
            ☰
          </button>
        </div>
      </div>

      <div class="view-container">
        <Transition :name="viewTransitionName">
          <div :key="viewMode" class="view-wrapper">
            <TransitionGroup 
              name="list" 
              tag="div" 
              class="cards-grid"
              v-if="viewMode === 'grid'"
            >
              <div 
                v-for="coin in displayPrices" 
                :key="coin.symbol"
                class="card-wrapper"
              >
                <CryptoCard 
                  :symbol="coin.symbol"
                  :data="coin"
                  @toggle-expand="(sym, isOpen) => $emit('toggle-expand', sym, isOpen)"
                />
              </div>
            </TransitionGroup>
            
            <div v-else class="table-wrapper">
              <CryptoTable :prices="displayPricesArray" />
            </div>
          </div>
        </Transition>
      </div>
    </div>
    
    <div v-else class="loading-state">
      <div class="spinner"></div>
      <p>Connecting to live market data...</p>
    </div>
  </div>
</template>

<script setup>
import { ref, toRef } from 'vue'
import CryptoCard from '../CryptoCard/CryptoCard.vue'
import CryptoTable from '../CryptoTable/CryptoTable.vue'
import { useSlidingIndicator } from '../../composables/useSlidingIndicator'
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

const filterContainer = ref(null)
const viewContainer = ref(null)

const { indicatorStyle: filterIndicatorStyle } = useSlidingIndicator(
    filterContainer, 
    toRef(() => props.filterMode)
)

const { indicatorStyle: viewIndicatorStyle } = useSlidingIndicator(
    viewContainer, 
    toRef(() => props.viewMode)
)
</script>
