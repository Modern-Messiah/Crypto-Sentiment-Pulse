import { ref, watch } from 'vue'

export const useChartTicker = (props) => {
    const nowAnchor = ref(Date.now())
    let tickerInterval = null

    const startTicker = () => {
        stopTicker()
        tickerInterval = setInterval(() => {
            const latestTs = props.history.length > 0 ? Math.max(...props.history.map(h => h.time)) : 0
            const clientNow = Date.now()
            nowAnchor.value = Math.max(clientNow, latestTs)
        }, props.period === '1m' ? 1000 : 5000)
    }

    const stopTicker = () => {
        if (tickerInterval) clearInterval(tickerInterval)
    }

    const onUnmount = () => {
        stopTicker()
    }

    watch(() => props.history, (newHistory) => {
        if (newHistory.length > 0 && !tickerInterval) {
            startTicker()
        }
    }, { immediate: true })

    watch(() => props.period, () => {
        startTicker()
    })

    return {
        nowAnchor,
        startTicker,
        stopTicker,
        onUnmount
    }
}
