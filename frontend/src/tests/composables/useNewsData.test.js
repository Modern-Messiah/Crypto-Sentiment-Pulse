import { describe, it, expect, vi, beforeEach } from 'vitest'
import { useNewsData } from '../../composables/useNewsData'

// Mock global fetch
global.fetch = vi.fn()

describe('useNewsData composable', () => {
    beforeEach(() => {
        vi.resetAllMocks()
    })

    it('initializes with default values', () => {
        const { newsItems, isLoadingMoreNews, allNewsLoaded } = useNewsData()

        expect(newsItems.value).toEqual([])
        expect(isLoadingMoreNews.value).toBe(false)
        expect(allNewsLoaded.value).toBe(false)
    })

    it('loads news successfully', async () => {
        const mockResponse = [
            { id: 1, title: 'Test News 1' },
            { id: 2, title: 'Test News 2' }
        ]

        global.fetch.mockResolvedValueOnce({
            ok: true,
            json: async () => mockResponse
        })

        const { newsItems, isLoadingMoreNews, loadMoreNews } = useNewsData()

        await loadMoreNews()

        expect(newsItems.value.length).toBe(2)
        expect(newsItems.value[0].title).toBe('Test News 1')
        expect(isLoadingMoreNews.value).toBe(false)
    })

    it('handles api error gracefully', async () => {
        global.fetch.mockRejectedValueOnce(new Error('Network error'))

        const { newsItems, isLoadingMoreNews, loadMoreNews } = useNewsData()

        await loadMoreNews()

        expect(newsItems.value.length).toBe(0) // Should remain empty
        expect(isLoadingMoreNews.value).toBe(false)
    })
})
