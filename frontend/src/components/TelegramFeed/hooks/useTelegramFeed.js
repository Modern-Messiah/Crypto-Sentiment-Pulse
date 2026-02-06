import { ref, computed, onMounted, onUnmounted } from 'vue'

export function useTelegramFeed(wsUrl) {
    const messages = ref([])
    const isConnected = ref(false)
    const error = ref(null)

    let ws = null
    let reconnectTimeout = null
    let reconnectAttempts = 0
    const maxReconnectAttempts = 10
    const reconnectDelay = 3000

    const connect = () => {
        try {
            ws = new WebSocket(wsUrl)

            ws.onopen = () => {
                console.log('📱 Telegram WS connected')
                isConnected.value = true
                error.value = null
                reconnectAttempts = 0
            }

            ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data)
                    if (data.type === 'update' && data.data?.telegram) {
                        messages.value = data.data.telegram
                    }
                } catch (e) {
                    console.error('Error parsing message:', e)
                }
            }

            ws.onerror = (e) => {
                console.error('❌ Telegram WS error:', e)
                error.value = 'Connection error'
            }

            ws.onclose = () => {
                console.log('📱 Telegram WS closed')
                isConnected.value = false

                if (reconnectAttempts < maxReconnectAttempts) {
                    reconnectAttempts++
                    reconnectTimeout = setTimeout(connect, reconnectDelay)
                }
            }

        } catch (e) {
            error.value = e.message
        }
    }

    const disconnect = () => {
        if (reconnectTimeout) clearTimeout(reconnectTimeout)
        if (ws) {
            ws.close()
            ws = null
        }
    }

    const formatTime = (dateStr) => {
        const date = new Date(dateStr)
        return date.toLocaleTimeString('ru-RU', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        })
    }

    const formatViews = (views) => {
        if (views >= 1000000) return (views / 1000000).toFixed(1) + 'M'
        if (views >= 1000) return (views / 1000).toFixed(1) + 'K'
        return views.toString()
    }

    onMounted(() => connect())
    onUnmounted(() => disconnect())

    return {
        messages,
        isConnected,
        error,
        formatTime,
        formatViews
    }
}
