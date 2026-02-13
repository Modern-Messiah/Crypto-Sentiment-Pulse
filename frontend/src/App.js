import { computed, ref, onMounted } from 'vue'
import { useWebSocket } from './composables/useWebSocket'

export const useApp = () => {
    const WS_URL = import.meta.env.PROD
        ? `ws://${window.location.host}/ws`
        : 'ws://localhost:8080/ws'

    const {
        prices,
        telegramMessages,
        isConnected,
        error,
        lastUpdate,
        loadMoreMessages,
        isLoadingMore,
        allLoaded
    } = useWebSocket(WS_URL)

    const viewMode = ref('grid')
    const filterMode = ref('all')
    const activeTab = ref('prices') // 'prices' or 'telegram'

    const tabs = [
        { id: 'prices', label: '📊 Prices', icon: '📊' },
        { id: 'telegram', label: '📱 Telegram', icon: '📱' },
        { id: 'news', label: '📰 News', icon: '📰' }
    ]

    const filters = [
        { id: 'all', label: 'All Assets' },
        { id: 'gainers', label: 'Top Gainers' },
        { id: 'losers', label: 'Top Losers' }
    ]

    const hasData = computed(() => Object.keys(prices.value).length > 0)
    const hasTelegramData = computed(() => telegramMessages.value.length > 0)

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
        const obj = {}
        displayPrices.value.forEach(c => {
            obj[c.symbol] = c
        })
        return obj
    })

    // News state
    const newsItems = ref([])
    const isLoadingMoreNews = ref(false)
    const allNewsLoaded = ref(false)

    const loadMoreNews = async () => {
        if (isLoadingMoreNews.value || allNewsLoaded.value) return

        isLoadingMoreNews.value = true
        try {
            const skip = newsItems.value.length
            const limit = 20

            const apiBase = import.meta.env.PROD ? '' : 'http://localhost:8080'
            const response = await fetch(`${apiBase}/api/v1/news?limit=${limit}&skip=${skip}`)

            if (!response.ok) throw new Error('Failed to fetch news')

            const newItems = await response.json()

            if (newItems.length < limit) {
                allNewsLoaded.value = true
            }

            if (newItems.length > 0) {
                const currentIds = new Set(newsItems.value.map(n => n.id))
                const uniqueNew = newItems.filter(n => !currentIds.has(n.id))
                newsItems.value = [...newsItems.value, ...uniqueNew]
            }
        } catch (e) {
            console.error('Error loading news:', e)
        } finally {
            isLoadingMoreNews.value = false
        }
    }

    // Load initial news on mount
    onMounted(() => {
        loadMoreNews()
    })

    return {
        isConnected,
        lastUpdate,
        error,
        hasData,
        hasTelegramData,
        viewMode,
        filterMode,
        activeTab,
        tabs,
        filters,
        displayPrices,
        displayPricesArray,
        displayPrices,
        displayPricesArray,
        telegramMessages,
        loadMoreMessages,
        isLoadingMore,
        allLoaded,
        newsItems,
        loadMoreNews,
        isLoadingMoreNews,
        allNewsLoaded
    }
}

