import { ref } from 'vue'

export function useNewsData() {
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

    return {
        newsItems,
        isLoadingMoreNews,
        allNewsLoaded,
        loadMoreNews
    }
}
