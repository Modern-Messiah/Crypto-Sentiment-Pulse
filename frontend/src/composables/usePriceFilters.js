import { computed, ref } from 'vue'

export function usePriceFilters(prices) {
    const filterMode = ref('all')
    const expandedSymbols = ref(new Set())
    const frozenSymbols = ref([])

    const filters = [
        { id: 'all', label: 'All Assets' },
        { id: 'gainers', label: 'Top Gainers' },
        { id: 'losers', label: 'Top Losers' }
    ]

    const allPricesArray = computed(() => Object.values(prices.value))

    const globalStats = computed(() => {
        const first = allPricesArray.value[0]
        return first?.global_stats || {}
    })

    const hasData = computed(() => Object.keys(prices.value).length > 0)

    const displayPrices = computed(() => {
        let data = [...allPricesArray.value]

        if (frozenSymbols.value.length > 0) {
            const symbolMap = new Map(data.map(c => [c.symbol, c]))
            return frozenSymbols.value
                .map(s => symbolMap.get(s))
                .filter(c => !!c)
        }

        if (filterMode.value === 'gainers') {
            return data.filter(c => c.change_24h > 0).sort((a, b) => b.change_24h - a.change_24h)
        }

        if (filterMode.value === 'losers') {
            return data.filter(c => c.change_24h < 0).sort((a, b) => a.change_24h - b.change_24h)
        }

        return data.sort((a, b) => b.change_24h - a.change_24h)
    })

    const displayPricesArray = computed(() => {
        const obj = {}
        displayPrices.value.forEach(c => {
            obj[c.symbol] = c
        })
        return obj
    })

    const onToggleExpand = (symbol, isOpen) => {
        if (isOpen) {
            if (expandedSymbols.value.size === 0) {
                frozenSymbols.value = displayPrices.value.map(c => c.symbol)
            }
            expandedSymbols.value.add(symbol)
        } else {
            expandedSymbols.value.delete(symbol)
            if (expandedSymbols.value.size === 0) {
                frozenSymbols.value = []
            }
        }
    }

    return {
        filterMode,
        filters,
        hasData,
        globalStats,
        displayPrices,
        displayPricesArray,
        onToggleExpand
    }
}
