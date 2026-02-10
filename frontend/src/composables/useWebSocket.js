import { ref, onMounted, onUnmounted } from 'vue'

/**
 * Composable для WebSocket подключения
 * @param {string} url - WebSocket URL
 */
export function useWebSocket(url) {
    const prices = ref({})
    const telegramMessages = ref([])
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
                console.log('WebSocket connected')
                isConnected.value = true
                error.value = null
                reconnectAttempts = 0
            }

            ws.onmessage = (event) => {
                try {
                    const message = JSON.parse(event.data)

                    // Handle new unified format
                    if (message.type === 'update' && message.data) {
                        // Handle prices
                        if (message.data.prices) {
                            const newPrices = message.data.prices

                            for (const [symbol, data] of Object.entries(newPrices)) {
                                const oldPrice = prices.value[symbol]?.price || 0
                                const newPrice = data.price

                                newPrices[symbol].priceDirection = newPrice > oldPrice ? 'up' : newPrice < oldPrice ? 'down' : null
                                newPrices[symbol].priceChanged = newPrice !== oldPrice
                            }

                            prices.value = newPrices
                        }

                        // Handle prices
                        if (message.data.prices) {
                            const newPrices = message.data.prices

                            for (const [symbol, data] of Object.entries(newPrices)) {
                                const oldPrice = prices.value[symbol]?.price || 0
                                const newPrice = data.price

                                newPrices[symbol].priceDirection = newPrice > oldPrice ? 'up' : newPrice < oldPrice ? 'down' : null
                                newPrices[symbol].priceChanged = newPrice !== oldPrice
                            }

                            prices.value = newPrices
                        }

                        lastUpdate.value = new Date()
                    }

                    // Handle instant telegram updates (push)
                    if (message.type === 'telegram_update' && message.data) {
                        const msg = message.data

                        // Ensure media list and URLs are consistent
                        if (!msg.media) msg.media = []

                        // If has_media but no media items in list (push update during album build)
                        if (msg.has_media && msg.media_path && msg.media.length === 0) {
                            msg.media = [{
                                type: msg.media_type,
                                url: `/media/${msg.media_path}`
                            }]
                        }

                        // Ensure media_url exists for fallback
                        if (msg.media.length > 0 && !msg.media_url) {
                            msg.media_url = msg.media[0].url
                        } else if (msg.has_media && msg.media_path && !msg.media_url) {
                            msg.media_url = `/media/${msg.media_path}`
                        }

                        // Check if it's an edit or a new message
                        const index = telegramMessages.value.findIndex(m => m.id === msg.id && m.channel_username === msg.channel_username)

                        if (index !== -1) {
                            // Replace message if it exists (edit or update)
                            // Only replace if certain fields are different to avoid unnecessary UI jitter
                            const existing = telegramMessages.value[index]
                            if (JSON.stringify(existing) !== JSON.stringify(msg)) {
                                telegramMessages.value[index] = msg
                            }
                        } else {
                            // Add new message at the top
                            telegramMessages.value = [msg, ...telegramMessages.value]
                        }
                        lastUpdate.value = new Date()
                    }

                    // Legacy format support
                    if (message.type === 'prices' && message.data) {
                        const newPrices = message.data

                        for (const [symbol, data] of Object.entries(newPrices)) {
                            const oldPrice = prices.value[symbol]?.price || 0
                            const newPrice = data.price

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
                console.error('WebSocket error:', e)
                error.value = 'Connection error'
            }

            ws.onclose = () => {
                console.log('WebSocket closed')
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

    // Pagination logic
    const isLoadingMore = ref(false)
    const allLoaded = ref(false)

    const loadMoreMessages = async () => {
        if (isLoadingMore.value || allLoaded.value) return

        isLoadingMore.value = true
        try {
            const skip = telegramMessages.value.length
            const limit = 20

            // Determine API URL based on environment
            const apiBase = import.meta.env.PROD ? '' : 'http://localhost:8080'
            const response = await fetch(`${apiBase}/api/v1/messages?limit=${limit}&skip=${skip}`)

            if (!response.ok) throw new Error('Failed to fetch messages')

            const newHistory = await response.json()

            if (newHistory.length < limit) {
                allLoaded.value = true
            }

            if (newHistory.length > 0) {
                // Append only if ID and channel combination is not present
                const currentKeys = new Set(telegramMessages.value.map(m => `${m.channel_username}:${m.id}`))
                const uniqueNew = newHistory.filter(m => !currentKeys.has(`${m.channel_username}:${m.id}`))
                telegramMessages.value = [...telegramMessages.value, ...uniqueNew]
            }
        } catch (e) {
            console.error('Error loading history:', e)
        } finally {
            isLoadingMore.value = false
        }
    }

    onMounted(() => {
        connect()
        // Initial load of messages
        loadMoreMessages()
    })

    onUnmounted(() => {
        disconnect()
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

