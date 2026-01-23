import { ref, onMounted, onUnmounted } from 'vue'

/**
 * Composable для WebSocket подключения
 * @param {string} url - WebSocket URL
 */
export function useWebSocket(url) {
    const prices = ref({})
    const isConnected = ref(false)
    const error = ref(null)
    const lastUpdate = ref(null)

    let ws = null
    let reconnectTimeout = null
    let reconnectAttempts = 0
    const maxReconnectAttempts = 10
    const reconnectDelay = 3000

    const connect = () => {
        try {
            ws = new WebSocket(url)

            ws.onopen = () => {
                console.log('🔌 WebSocket connected')
                isConnected.value = true
                error.value = null
                reconnectAttempts = 0
            }

            ws.onmessage = (event) => {
                try {
                    const message = JSON.parse(event.data)
                    console.log('WS Message:', message.type, Object.keys(message.data || {}).length)
                    if (message.type === 'prices' && message.data) {
                        // Отслеживаем изменения цен для анимации
                        const newPrices = message.data

                        for (const [symbol, data] of Object.entries(newPrices)) {
                            const oldPrice = prices.value[symbol]?.price || 0
                            const newPrice = data.price

                            // Добавляем флаг направления изменения
                            newPrices[symbol].priceDirection = newPrice > oldPrice ? 'up' : newPrice < oldPrice ? 'down' : null
                            newPrices[symbol].priceChanged = newPrice !== oldPrice
                        }

                        prices.value = newPrices
                        lastUpdate.value = new Date()
                    }
                } catch (e) {
                    console.error('Error parsing message:', e)
                }
            }

            ws.onerror = (e) => {
                console.error('❌ WebSocket error:', e)
                error.value = 'Connection error'
            }

            ws.onclose = () => {
                console.log('🔌 WebSocket closed')
                isConnected.value = false

                // Auto-reconnect
                if (reconnectAttempts < maxReconnectAttempts) {
                    reconnectAttempts++
                    console.log(`Reconnecting... (attempt ${reconnectAttempts}/${maxReconnectAttempts})`)
                    reconnectTimeout = setTimeout(connect, reconnectDelay)
                } else {
                    error.value = 'Connection failed after multiple attempts'
                }
            }

        } catch (e) {
            console.error('Failed to create WebSocket:', e)
            error.value = e.message
        }
    }

    const disconnect = () => {
        if (reconnectTimeout) {
            clearTimeout(reconnectTimeout)
        }
        if (ws) {
            ws.close()
            ws = null
        }
    }

    onMounted(() => {
        connect()
    })

    onUnmounted(() => {
        disconnect()
    })

    return {
        prices,
        isConnected,
        error,
        lastUpdate,
        reconnect: connect
    }
}
