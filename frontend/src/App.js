import { onMounted } from 'vue'
import { useWebSocket } from './composables/useWebSocket'
import { useNavigation } from './composables/useNavigation'
import { usePriceFilters } from './composables/usePriceFilters'
import { useNewsData } from './composables/useNewsData'

export const useApp = () => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const WS_URL = import.meta.env.PROD
        ? `${protocol}//${window.location.host}/ws`
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

    const {
        viewMode,
        viewTransitionName,
        activeTab,
        transitionName,
        tabs,
        setViewMode,
        setTab
    } = useNavigation()

    const {
        filterMode,
        filters,
        hasData,
        globalStats,
        displayPrices,
        displayPricesArray,
        onToggleExpand
    } = usePriceFilters(prices)

    const {
        newsItems,
        isLoadingMoreNews,
        allNewsLoaded,
        loadMoreNews
    } = useNewsData()

    onMounted(() => {
        loadMoreNews()
    })

    return {
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
    }
}
