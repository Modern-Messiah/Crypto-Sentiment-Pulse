<template>
  <div class="app-container">
    <Header 
      :is-connected="isConnected" 
      :last-update="lastUpdate"
      :global-stats="globalStats"
    />
    
    <main class="main-content">
      
      <!-- Ошибка соединения -->
      <div v-if="error" class="error-banner animate-fade-in">
        <div class="error-content">
          <span class="error-icon"></span>
          <p>{{ error }}. Attempting to reconnect...</p>
        </div>
      </div>
      
      <!-- Navigation Tabs -->
      <div class="nav-tabs glass-card" ref="navContainer">
          <div class="sliding-indicator" :style="navIndicatorStyle"></div>
          <button 
            v-for="tab in tabs"
            :key="tab.id"
            class="nav-tab" 
            :class="{ active: activeTab === tab.id }"
            @click="setTab(tab.id)"
          >
            {{ tab.label }}
          </button>
      </div>
      
      <div class="view-container">
        <Transition :name="transitionName">
          <div :key="activeTab" class="view-wrapper">
            <!-- Prices Tab -->
            <div v-if="activeTab === 'prices'" class="dashboard-content">
              <div v-if="hasData">

                <!-- Controls Toolbar -->
                <div class="toolbar glass-card">
                  <div class="filter-group" ref="filterContainer">
                    <div class="sliding-indicator filter-indicator" :style="filterIndicatorStyle"></div>
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

                  <div class="view-group" ref="viewContainer">
                    <div class="sliding-indicator view-indicator" :style="viewIndicatorStyle"></div>
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
                    @toggle-expand="onToggleExpand"
                  />
                </div>
                
                <!-- Table View -->
                <div v-else class="table-wrapper">
                  <CryptoTable :prices="displayPricesArray" />
                </div>
              </div>
              
              <!-- Лоадер при первой загрузке -->
              <div v-else class="loading-state">
                <div class="spinner"></div>
                <p>Connecting to live market data...</p>
              </div>
            </div>
            
            <!-- Telegram Tab -->
            <div v-else-if="activeTab === 'telegram'" class="dashboard-content">
              <TelegramFeed 
                :messages="telegramMessages"
                :is-connected="isConnected"
                :is-loading-more="isLoadingMore"
                :all-loaded="allLoaded"
                @load-more="loadMoreMessages"
              />
            </div>
            
            <!-- News Tab -->
            <div v-else-if="activeTab === 'news'" class="dashboard-content">
              <NewsFeed 
                :news-items="newsItems"
                :is-loading-more="isLoadingMoreNews"
                :all-loaded="allNewsLoaded"
                @load-more="loadMoreNews"
              />
            </div>
          </div>
        </Transition>
      </div>
      
    </main>
  </div>
</template>

<script setup>
import { ref, toRef } from 'vue'
import Header from './components/Header/Header.vue'
import CryptoCard from './components/CryptoCard/CryptoCard.vue'
import CryptoTable from './components/CryptoTable/CryptoTable.vue'
import TelegramFeed from './components/TelegramFeed/TelegramFeed.vue'
import NewsFeed from './components/NewsFeed/NewsFeed.vue'
import MarketSentiment from './components/MarketSentiment/MarketSentiment.vue'
import { useApp } from './App.js'
import { useSlidingIndicator } from './composables/useSlidingIndicator'
import './App.css'

const {
  isConnected,
  lastUpdate,
  error,
  hasData,
  viewMode,
  filterMode,
  activeTab,
  transitionName,
  setTab,
  tabs,
  filters,
  displayPrices,
  displayPricesArray,
  telegramMessages,
  loadMoreMessages,
  isLoadingMore,
  allLoaded,
  newsItems,
  loadMoreNews,
  isLoadingMoreNews,
  allNewsLoaded,
  onToggleExpand,
  globalStats
} = useApp()

const navContainer = ref(null)
const filterContainer = ref(null)
const viewContainer = ref(null)

const { indicatorStyle: navIndicatorStyle } = useSlidingIndicator(
    navContainer, 
    toRef(() => activeTab.value)
)

const { indicatorStyle: filterIndicatorStyle } = useSlidingIndicator(
    filterContainer, 
    toRef(() => filterMode.value)
)

const { indicatorStyle: viewIndicatorStyle } = useSlidingIndicator(
    viewContainer, 
    toRef(() => viewMode.value)
)
</script>

