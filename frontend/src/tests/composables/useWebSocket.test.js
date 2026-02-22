import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { defineComponent } from 'vue'
import { useWebSocket } from '../../composables/useWebSocket'

class MockWebSocket {
    constructor(url) {
        this.url = url
        this.readyState = WebSocket.CONNECTING
        setTimeout(() => {
            this.readyState = WebSocket.OPEN
            if (this.onopen) this.onopen()
        }, 10)
    }
    send() { }
    close() {
        this.readyState = WebSocket.CLOSED
        if (this.onclose) this.onclose()
    }
}

global.WebSocket = MockWebSocket

// Mock internal dependencies to avoid real network calls
vi.mock('../../composables/socket/useTelegramData.js', () => ({
    useTelegramData: () => ({
        telegramMessages: { value: [] },
        handleTelegramUpdate: vi.fn(),
        loadMoreMessages: vi.fn(),
        isLoadingMore: { value: false },
        allLoaded: { value: false }
    })
}))

describe('useWebSocket composable', () => {
    it('initializes and connects within a component lifecycle', async () => {
        let wsData

        const TestComponent = defineComponent({
            setup() {
                wsData = useWebSocket('ws://localhost:8080/ws')
                return () => null
            }
        })

        mount(TestComponent)

        expect(wsData.isConnected.value).toBe(false)
        expect(wsData.error.value).toBe(null)

        // Wait for MockWebSocket's 10ms delay
        await new Promise(resolve => setTimeout(resolve, 20))

        expect(wsData.isConnected.value).toBe(true)
    })
})
