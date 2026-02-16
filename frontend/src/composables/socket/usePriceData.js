import { ref } from 'vue'

export function usePriceData() {
    const prices = ref({})

    const handlePriceUpdate = (newPricesData) => {
        if (!newPricesData) return

        const newPrices = { ...prices.value }

        const nextPrices = { ...newPricesData }

        for (const [symbol, data] of Object.entries(nextPrices)) {
            const oldPrice = prices.value[symbol]?.price || 0
            const newPrice = data.price

            nextPrices[symbol].priceDirection = newPrice > oldPrice ? 'up' : newPrice < oldPrice ? 'down' : null
            nextPrices[symbol].priceChanged = newPrice !== oldPrice
        }

        prices.value = nextPrices
    }

    return {
        prices,
        handlePriceUpdate
    }
}
