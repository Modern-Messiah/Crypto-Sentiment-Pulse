import { ref } from 'vue'

export function useTelegramData() {
    const telegramMessages = ref([])
    const isLoadingMore = ref(false)
    const allLoaded = ref(false)

    const processTelegramMessage = (msg) => {
        if (!msg.media) msg.media = []

        if (msg.has_media && msg.media_path && msg.media.length === 0) {
            msg.media = [{
                type: msg.media_type,
                url: `/media/${msg.media_path}`
            }]
        }

        if (msg.media.length > 0 && !msg.media_url) {
            msg.media_url = msg.media[0].url
        } else if (msg.has_media && msg.media_path && !msg.media_url) {
            msg.media_url = `/media/${msg.media_path}`
        }

        return msg
    }

    const handleTelegramUpdate = (rawData) => {
        const msg = processTelegramMessage(rawData)

        const index = telegramMessages.value.findIndex(m => m.id === msg.id && m.channel_username === msg.channel_username)

        if (index !== -1) {
            const existing = telegramMessages.value[index]
            if (JSON.stringify(existing) !== JSON.stringify(msg)) {
                telegramMessages.value[index] = msg
            }
        } else {
            telegramMessages.value = [msg, ...telegramMessages.value]
        }
    }

    const loadMoreMessages = async () => {
        if (isLoadingMore.value || allLoaded.value) return

        isLoadingMore.value = true
        try {
            const skip = telegramMessages.value.length
            const limit = 20

            const apiBase = import.meta.env.PROD ? '' : 'http://localhost:8080'
            const response = await fetch(`${apiBase}/api/v1/messages?limit=${limit}&skip=${skip}`)

            if (!response.ok) throw new Error('Failed to fetch messages')

            const newHistory = await response.json()

            if (newHistory.length < limit) {
                allLoaded.value = true
            }

            if (newHistory.length > 0) {
                const processedHistory = newHistory.map(processTelegramMessage)

                const currentKeys = new Set(telegramMessages.value.map(m => `${m.channel_username}:${m.id}`))
                const uniqueNew = processedHistory.filter(m => !currentKeys.has(`${m.channel_username}:${m.id}`))
                telegramMessages.value = [...telegramMessages.value, ...uniqueNew]
            }
        } catch (e) {
            console.error('Error loading history:', e)
        } finally {
            isLoadingMore.value = false
        }
    }

    return {
        telegramMessages,
        isLoadingMore,
        allLoaded,
        handleTelegramUpdate,
        loadMoreMessages
    }
}
