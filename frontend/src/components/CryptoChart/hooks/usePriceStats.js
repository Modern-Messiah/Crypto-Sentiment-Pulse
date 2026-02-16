import { computed } from 'vue'

export const usePriceStats = (props) => {
    const priceStats = computed(() => {
        if (!props.history.length) return { min: 0, max: 0, change: 0, changePercent: 0 }

        const prices = props.history.map(h => h.price)
        const min = Math.min(...prices)
        const max = Math.max(...prices)
        const first = prices[0]
        const last = prices[prices.length - 1]
        const change = last - first
        const changePercent = first ? ((change / first) * 100) : 0

        return { min, max, change, changePercent, first, last }
    })

    return { priceStats }
}
