import { ref, onMounted } from 'vue'
import { useSocketConnection } from './socket/useSocketConnection.js'
import { usePriceData } from './socket/usePriceData.js'
import { useTelegramData } from './socket/useTelegramData.js'

export function useWebSocket(url) {
    const lastUpdate = ref(null)

    const {
        prices,
        handlePriceUpdate
    } = usePriceData()

    const {
        telegramMessages,
        handleTelegramUpdate,
        loadMoreMessages,
        isLoadingMore,
        allLoaded
    } = useTelegramData()

    const onMessage = (message) => {
        if (message.type === 'update' && message.data) {
            if (message.data.prices) {
                handlePriceUpdate(message.data.prices)
            }
            lastUpdate.value = new Date()
        }

        if (message.type === 'telegram_update' && message.data) {
            handleTelegramUpdate(message.data)
            lastUpdate.value = new Date()
        }

        if (message.type === 'prices' && message.data) {
            handlePriceUpdate(message.data)
            lastUpdate.value = new Date()
        }
    }

    const {
        isConnected,
        error,
        connect,
        disconnect
    } = useSocketConnection(url, onMessage)

    onMounted(() => {
        loadMoreMessages()
    })

    return {
        prices,
        telegramMessages,
        isConnected,
        error,
        lastUpdate,
        reconnect: connect,
        loadMoreMessages,
        isLoadingMore,
        allLoaded
    }
}
