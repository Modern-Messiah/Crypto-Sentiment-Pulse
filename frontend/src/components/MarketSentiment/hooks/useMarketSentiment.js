import { ref, onMounted, computed, onUnmounted } from 'vue'

export const useMarketSentiment = () => {
    const value = ref(50)
    const classification = ref('Neutral')
    const loading = ref(true)
    const error = ref(null)
    const timeUntilUpdate = ref(null)

    const API_URL = import.meta.env.VITE_API_URL || '/api/v1'

    const fetchData = async () => {
        try {
            loading.value = true
            const res = await fetch(`${API_URL}/sentiment/fear-greed`)
            const data = await res.json()

            if (data.error) {
                throw new Error(data.error)
            }

            value.value = data.value
            classification.value = data.value_classification
            timeUntilUpdate.value = data.time_until_update
        } catch (e) {
            error.value = e.message
            console.error("Sentiment fetch error:", e)
        } finally {
            loading.value = false
        }
    }

    const needleRotation = computed(() => {
        const deg = (value.value / 100) * 180 - 90
        return Math.max(-90, Math.min(90, deg))
    })

    const scoreColor = computed(() => {
        const v = value.value
        if (v < 25) return '#ff4757'
        if (v < 45) return '#ffa502'
        if (v < 55) return '#eccc68'
        if (v < 75) return '#7bed9f'
        return '#2ed573'
    })

    const formattedTimeUntil = computed(() => {
        if (!timeUntilUpdate.value) return ''
        const sec = parseInt(timeUntilUpdate.value)
        if (isNaN(sec)) return ''
        const h = Math.floor(sec / 3600)
        const m = Math.floor((sec % 3600) / 60)
        return `${h}h ${m}m`
    })

    onMounted(() => {
        fetchData()
        const interval = setInterval(fetchData, 5 * 60 * 1000)
        onUnmounted(() => clearInterval(interval))
    })

    return {
        value,
        classification,
        loading,
        error,
        timeUntilUpdate,
        formattedTimeUntil,
        needleRotation,
        scoreColor
    }
}
