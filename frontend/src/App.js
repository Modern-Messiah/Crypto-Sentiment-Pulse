import { computed, ref } from 'vue'
import Header from './components/Header/index.vue'
import CryptoCard from './components/CryptoCard/index.vue'
import CryptoTable from './components/CryptoTable/index.vue'
import { useWebSocket } from './composables/useWebSocket'

export const useApp = () => {
    const WS_URL = import.meta.env.PROD
        ? `ws://${window.location.host}/ws`
        : 'ws://localhost:8080/ws'

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
        return data.sort((a, b) => b.change_24h - a.change_24h)
    })

    const displayPricesArray = computed(() => {
        // А лучше поправим CryptoTable чуть позже, чтобы он был гибче. 
        // Но пока, конвертируем массив в объект для пропса.

        const obj = {}
        displayPrices.value.forEach(c => {
            obj[c.symbol] = c
        })
        return obj
    })

    return {
        isConnected,
        lastUpdate,
        error,
        hasData,
        viewMode,
        filterMode,
        filters,
        displayPrices,
        displayPricesArray
    }
}
