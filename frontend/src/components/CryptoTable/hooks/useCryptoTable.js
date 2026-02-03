import { ref, computed } from 'vue'

export const useCryptoTable = (props) => {
    const searchQuery = ref('')
    const sortKey = ref('change_24h')
    const sortOrder = ref('desc')

    const pricesArray = computed(() => {
        return Object.values(props.prices)
    })

    const filteredPrices = computed(() => {
        const query = searchQuery.value.toLowerCase().trim()
        if (!query) return pricesArray.value

        return pricesArray.value.filter(coin =>
            coin.symbol.toLowerCase().includes(query)
        )
    })

    const sortedPrices = computed(() => {
        return [...filteredPrices.value].sort((a, b) => {
            let modifier = sortOrder.value === 'asc' ? 1 : -1

            if (sortKey.value === 'symbol') {
                return a.symbol.localeCompare(b.symbol) * modifier
            }

            return (a[sortKey.value] - b[sortKey.value]) * modifier
        })
    })

    function sortBy(key) {
        if (sortKey.value === key) {
            sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
        } else {
            sortKey.value = key
            sortOrder.value = 'desc'
        }
    }

    return {
        searchQuery,
        sortKey,
        sortOrder,
        sortedPrices,
        sortBy
    }
}
