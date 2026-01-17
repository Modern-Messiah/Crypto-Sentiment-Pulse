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
import { computed, ref } from 'vue'
import Header from './components/Header.vue'
import CryptoCard from './components/CryptoCard.vue'
import CryptoTable from './components/CryptoTable.vue'
import { useWebSocket } from './composables/useWebSocket'

const WS_URL = import.meta.env.PROD 
  ? `ws://${window.location.host}/ws` 
  : 'ws://localhost:8000/ws'

const { prices, isConnected, error, lastUpdate } = useWebSocket(WS_URL)

const viewMode = ref('grid')
const filterMode = ref('all')

const filters = [
  { id: 'all', label: 'All Assets' },
  { id: 'gainers', label: 'Top Gainers' },
  { id: 'losers', label: 'Top Losers' }
]

const hasData = computed(() => Object.keys(prices.value).length > 0)

// Преобразуем объект в массив для удобной фильтрации
const allPricesArray = computed(() => Object.values(prices.value))

const displayPrices = computed(() => {
  let data = allPricesArray.value
  
  if (filterMode.value === 'gainers') {
    return data.filter(c => c.change_24h > 0).sort((a, b) => b.change_24h - a.change_24h)
  }
  
  if (filterMode.value === 'losers') {
    return data.filter(c => c.change_24h < 0).sort((a, b) => a.change_24h - b.change_24h)
  }
  
  // По умолчанию сортируем по объему или имени, чтобы порядок не скакал
  // Или можно оставить как приходит, но лучше сортировать
  return data.sort((a, b) => b.change_24h - a.change_24h) 
})

// Для таблицы передаем объект (хотя таблица внутри тоже может array принимать, но мы адаптируем)
// CryptoTable ожидает 'prices' как Object для ключей, но мы можем обновить CryptoTable
// В текущей реализации CryptoTable принимает Object. Давайте лучше передадим Object.
// Но постойте, CryptoTable принимает :prices="prices". 
// Лучше адаптировать таблицу на прием массива, или конвертировать обратно.
// В App.vue:CryptoTable принимает prices Object.
// Давайте передадим computed object.

const displayPricesArray = computed(() => {
  // Для таблицы возвращаем массив, но CryptoTable.vue ожидает Object prop "prices"
  // Однако внутри CryptoTable есть computed `pricesArray = Object.values(props.prices)`.
  // Я могу изменить CryptoTable чтобы он принимал Array или Object.
  // Но проще конвертировать Array обратно в Object для совместимости без правки CryptoTable.
  
  // А лучше поправим CryptoTable чуть позже, чтобы он был гибче. 
  // Но пока, конвертируем массив в объект для пропса.
  
  const obj = {}
  displayPrices.value.forEach(c => {
    obj[c.symbol] = c
  })
  return obj
})
</script>

<style scoped>
.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.main-content {
  flex: 1;
  max-width: 1400px;
  width: 100%;
  margin: 0 auto;
  padding: 2rem;
}

.dashboard-content {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

/* Toolbar */
.toolbar {
  display: flex;
  justify-content: space-between;
  padding: 1rem;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.filter-group, .view-group {
  display: flex;
  gap: 0.5rem;
}

.control-btn {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: var(--text-muted);
  padding: 0.5rem 1rem;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all var(--transition-fast);
  font-weight: 500;
}

.control-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  color: var(--text-primary);
}

.control-btn.active {
  background: var(--accent-primary);
  border-color: var(--accent-primary);
  color: white;
  box-shadow: 0 0 15px rgba(102, 126, 234, 0.3);
}

.icon-btn {
  font-size: 1.2rem;
  padding: 0.4rem 0.8rem;
}

.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
  padding-bottom: 2rem;
}

.error-banner {
  background: rgba(255, 71, 87, 0.1);
  border: 1px solid rgba(255, 71, 87, 0.3);
  border-radius: var(--radius-md);
  padding: 1rem;
  margin-bottom: 2rem;
}

.error-content {
  display: flex;
  align-items: center;
  gap: 1rem;
  color: var(--danger);
  font-weight: 500;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 60vh;
  gap: 1.5rem;
  color: var(--text-muted);
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(102, 126, 234, 0.3);
  border-radius: 50%;
  border-top-color: var(--accent-primary);
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@media (max-width: 600px) {
  .main-content {
    padding: 1rem;
  }
  
  .toolbar {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filter-group {
    justify-content: center;
  }
  
  .view-group {
    display: none; /* Hide toggle on mobile, maybe auto-switch to cards? */
  }
}
</style>
