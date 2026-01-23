<template>
  <div class="app-container">
    <Header 
      :is-connected="isConnected" 
      :last-update="lastUpdate"
    />
    
    <main class="main-content">
      
      <!-- Ошибка соединения -->
      <div v-if="error" class="error-banner animate-fade-in">
        <div class="error-content">
          <span class="error-icon"></span>
          <p>{{ error }}. Attempting to reconnect...</p>
        </div>
      </div>
      
      <!-- Основной контент -->
      <div v-if="hasData" class="dashboard-content animate-fade-in">
        
        <!-- Controls Toolbar -->
        <div class="toolbar glass-card">
          <div class="filter-group">
            <button 
              v-for="f in filters" 
              :key="f.id"
              class="control-btn"
              :class="{ active: filterMode === f.id }"
              @click="filterMode = f.id"
            >
              {{ f.label }}
            </button>
          </div>
          
          <div class="view-group">
            <button 
              class="control-btn icon-btn"
              :class="{ active: viewMode === 'grid' }"
              @click="viewMode = 'grid'"
              title="Grid View"
            >
              ⊞
            </button>
            <button 
              class="control-btn icon-btn"
              :class="{ active: viewMode === 'table' }"
              @click="viewMode = 'table'"
              title="Table View"
            >
              ☰
            </button>
          </div>
        </div>

        <!-- Grid View -->
        <div v-if="viewMode === 'grid'" class="cards-grid">
          <CryptoCard 
            v-for="coin in displayPrices" 
            :key="coin.symbol"
            :symbol="coin.symbol"
            :data="coin"
          />
        </div>
        
        <!-- Table View -->
        <div v-else class="table-container">
          <CryptoTable :prices="displayPricesArray" />
        </div>
        
      </div>
      
      <!-- Лоадер при первой загрузке -->
      <div v-else class="loading-state">
        <div class="spinner"></div>
        <p>Connecting to live market data...</p>
      </div>
      
    </main>
  </div>
</template>

<script setup>
import Header from './components/Header/index.vue'
import CryptoCard from './components/CryptoCard/index.vue'
import CryptoTable from './components/CryptoTable/index.vue'
import { useApp } from './App.js'
import './App.css'

const {
  isConnected,
  lastUpdate,
  error,
  hasData,
  viewMode,
  filterMode,
  filters,
  displayPrices,
  displayPricesArray
} = useApp()
</script>
