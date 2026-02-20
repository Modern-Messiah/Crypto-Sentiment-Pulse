<template>
  <div class="app-container" :class="{ 'fixed-layout': activeTab === 'telegram' || activeTab === 'news' }">
    <Header 
      :is-connected="isConnected" 
      :last-update="lastUpdate"
      :global-stats="globalStats"
      :active-tab="activeTab"
      :is-hidden="isHeaderHidden"
    />
    
    <main class="main-content" :class="{ 'header-hidden': isHeaderHidden, 'prices-layout': activeTab === 'prices' }">
      
      <div v-if="error" class="error-banner animate-fade-in">
        <div class="error-content">
          <span class="error-icon"></span>
          <p>{{ error }}. Attempting to reconnect...</p>
        </div>
      </div>
      
      <Navigation 
        :tabs="tabs" 
        :active-tab="activeTab" 
        @set-tab="setTab"
      />
      
      <div class="view-container">
        <div v-if="activeTab === 'prices'" class="view-wrapper">
          <Dashboard 
            :has-data="hasData"
            :filters="filters"
            :filter-mode="filterMode"
            :view-mode="viewMode"
            :view-transition-name="viewTransitionName"
            :display-prices="displayPrices"
            :display-prices-array="displayPricesArray"
            @update:filter-mode="filterMode = $event"
            @set-view-mode="setViewMode"
            @toggle-expand="onToggleExpand"
          />
        </div>

        <div v-if="activeTab === 'telegram'" class="view-wrapper">
          <div class="dashboard-content">
              <TelegramFeed 
                :messages="telegramMessages"
                :is-connected="isConnected"
                :is-loading-more="isLoadingMore"
                :all-loaded="allLoaded"
                :is-header-hidden="isHeaderHidden"
                @load-more="loadMoreMessages"
              />
          </div>
        </div>

        <div v-if="activeTab === 'news'" class="view-wrapper">
          <div class="dashboard-content">
              <NewsFeed 
                :news-items="newsItems"
                :is-loading-more="isLoadingMoreNews"
                :all-loaded="allNewsLoaded"
                :is-header-hidden="isHeaderHidden"
                @load-more="loadMoreNews"
              />
          </div>
        </div>
      </div>
      
    </main>
  </div>
</template>

<script setup>
import Header from './components/Header/Header.vue'
import Navigation from './components/Navigation/Navigation.vue'
import Dashboard from './components/Dashboard/Dashboard.vue'
import TelegramFeed from './components/TelegramFeed/TelegramFeed.vue'
import NewsFeed from './components/NewsFeed/NewsFeed.vue'
import { useApp } from './App.js'
import { useHeaderVisibility } from './components/Header/hooks/useHeaderVisibility.js'
import { toRef } from 'vue'
import './App.css'

const {
  isConnected,
  lastUpdate,
  error,
  hasData,
  viewMode,
  setViewMode,
  viewTransitionName,
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

const { isHidden: isHeaderHidden } = useHeaderVisibility(null, activeTab)
</script>
