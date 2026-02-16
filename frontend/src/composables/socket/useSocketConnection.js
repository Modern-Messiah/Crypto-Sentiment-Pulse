import { ref, onMounted, onUnmounted } from 'vue'

export function useSocketConnection(url, onMessage) {
    const isConnected = ref(false)
    const error = ref(null)
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
                    onMessage(message)
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
        isConnected,
        error,
        connect,
        disconnect
    }
}
