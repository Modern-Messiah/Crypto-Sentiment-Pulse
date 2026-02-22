import { describe, it, expect } from 'vitest'
import { ref } from 'vue'
import { usePriceFilters } from '../../composables/usePriceFilters'

describe('usePriceFilters composable', () => {
    it('initializes with default values and handles empty data', () => {
        const prices = ref({})
        const { filterMode, hasData, displayPrices, globalStats } = usePriceFilters(prices)

        expect(filterMode.value).toBe('all')
        expect(hasData.value).toBe(false)
        expect(displayPrices.value).toEqual([])
        expect(globalStats.value).toEqual({})
    })

    it('processes and sorts price data correctly', () => {
        const prices = ref({
            'BTCUSDT': { symbol: 'BTCUSDT', price: 50000, change_24h: 5 },
            'ETHUSDT': { symbol: 'ETHUSDT', price: 3000, change_24h: 2 },
            'SOLUSDT': { symbol: 'SOLUSDT', price: 100, change_24h: -10 }
        })

        const { hasData, displayPrices, filterMode } = usePriceFilters(prices)

        expect(hasData.value).toBe(true)

        // Default 'all' sorts by change_24h descending
        expect(displayPrices.value.length).toBe(3)
        expect(displayPrices.value[0].symbol).toBe('BTCUSDT')
        expect(displayPrices.value[2].symbol).toBe('SOLUSDT')

        // Test top gainers
        filterMode.value = 'gainers'
        expect(displayPrices.value.length).toBe(2)
        expect(displayPrices.value[0].symbol).toBe('BTCUSDT')

        // Test top losers
        filterMode.value = 'losers'
        expect(displayPrices.value.length).toBe(1)
        expect(displayPrices.value[0].symbol).toBe('SOLUSDT')
    })
})
