import { computed, ref, watch } from 'vue'
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
    Filler
} from 'chart.js'
import { Line } from 'vue-chartjs'

ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
    Filler
)

export const useCryptoChart = (props) => {
    // Format price for display
    const formatPrice = (value) => {
        if (value >= 1000) {
            return '$' + value.toLocaleString('en-US', { maximumFractionDigits: 0 })
        } else if (value >= 1) {
            return '$' + value.toFixed(2)
        } else {
            return '$' + value.toFixed(4)
        }
    }

    // Helper to convert hex to rgba
    const hexToRgba = (hex, alpha) => {
        const r = parseInt(hex.slice(1, 3), 16)
        const g = parseInt(hex.slice(3, 5), 16)
        const b = parseInt(hex.slice(5, 7), 16)
        return `rgba(${r}, ${g}, ${b}, ${alpha})`
    }

    // Calculate price stats
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

    const nowAnchor = ref(Date.now())
    let tickerInterval = null

    // Update 'now' every second to keep the chart scrolling smoothly
    const startTicker = () => {
        stopTicker()
        tickerInterval = setInterval(() => {
            const latestTs = props.history.length > 0 ? Math.max(...props.history.map(h => h.time)) : 0
            const clientNow = Date.now()
            nowAnchor.value = Math.max(clientNow, latestTs)
        }, 1000)
    }

    const stopTicker = () => {
        if (tickerInterval) clearInterval(tickerInterval)
    }

    watch(() => props.history, (newHistory) => {
        if (newHistory.length > 0 && !tickerInterval) {
            startTicker()
        }
    }, { immediate: true })

    const chartData = computed(() => {
        return {
            datasets: [
                {
                    label: 'Price',
                    backgroundColor: (context) => {
                        const ctx = context.chart.ctx
                        const gradient = ctx.createLinearGradient(0, 0, 0, 150)
                        gradient.addColorStop(0, hexToRgba(props.color, 0.4))
                        gradient.addColorStop(1, hexToRgba(props.color, 0.02))
                        return gradient
                    },
                    borderColor: props.color,
                    borderWidth: 2,
                    pointRadius: 0,
                    pointHoverRadius: 5,
                    pointHoverBackgroundColor: props.color,
                    pointHoverBorderColor: '#fff',
                    pointHoverBorderWidth: 2,
                    data: props.history.map(h => ({ x: h.time, y: h.price })),
                    fill: true,
                    tension: 0.3
                }
            ]
        }
    })

    const chartOptions = computed(() => {
        const period = props.period || '15m'
        let periodMs = 15 * 60 * 1000
        if (period === '1h') periodMs = 60 * 60 * 1000
        else if (period === '4h') periodMs = 4 * 60 * 60 * 1000
        else if (period === '24h') periodMs = 24 * 60 * 60 * 1000

        const max = nowAnchor.value
        const min = max - periodMs

        return {
            responsive: true,
            maintainAspectRatio: false,
            animation: {
                duration: 300
            },
            plugins: {
                legend: { display: false },
                tooltip: {
                    enabled: true,
                    backgroundColor: 'rgba(15, 15, 26, 0.95)',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    borderColor: 'rgba(255,255,255,0.1)',
                    borderWidth: 1,
                    padding: 12,
                    displayColors: false,
                    callbacks: {
                        title: (items) => {
                            if (items.length) {
                                const date = new Date(items[0].raw.x)
                                const h = date.getHours().toString().padStart(2, '0')
                                const m = date.getMinutes().toString().padStart(2, '0')
                                const s = date.getSeconds().toString().padStart(2, '0')

                                if (period === '15m') return `${h}:${m}:${s}`
                                if (period === '24h') {
                                    const day = date.getDate().toString().padStart(2, '0')
                                    const mon = (date.getMonth() + 1).toString().padStart(2, '0')
                                    return `${day}/${mon} ${h}:${m}`
                                }
                                return `${h}:${m}`
                            }
                            return ''
                        },
                        label: (context) => {
                            return formatPrice(context.raw.y)
                        },
                        afterLabel: (context) => {
                            const firstPrice = props.history[0]?.price
                            if (!firstPrice) return ''
                            const diff = context.raw.y - firstPrice
                            const percent = ((diff / firstPrice) * 100).toFixed(2)
                            const sign = diff >= 0 ? '+' : ''
                            return `${sign}${percent}% from start`
                        }
                    }
                }
            },
            scales: {
                x: {
                    type: 'linear',
                    display: true,
                    min: min,
                    max: max,
                    grid: {
                        display: false,
                        drawBorder: false
                    },
                    ticks: {
                        color: 'rgba(255, 255, 255, 0.4)',
                        font: { size: 9 },
                        maxTicksLimit: 5,
                        maxRotation: 0,
                        callback: (value) => {
                            const date = new Date(value)
                            const h = date.getHours().toString().padStart(2, '0')
                            const m = date.getMinutes().toString().padStart(2, '0')
                            if (period === '15m') {
                                const s = date.getSeconds().toString().padStart(2, '0')
                                return `${h}:${m}:${s}`
                            }
                            if (period === '24h') {
                                const day = date.getDate().toString().padStart(2, '0')
                                const mon = (date.getMonth() + 1).toString().padStart(2, '0')
                                return `${day}/${mon} ${h}:${m}`
                            }
                            return `${h}:${m}`
                        }
                    }
                },
                y: {
                    display: true,
                    position: 'right',
                    grid: {
                        color: 'rgba(255, 255, 255, 0.05)',
                        drawBorder: false
                    },
                    ticks: {
                        color: 'rgba(255, 255, 255, 0.4)',
                        font: { size: 9 },
                        maxTicksLimit: 4,
                        callback: (value) => formatPrice(value)
                    }
                }
            },
            interaction: {
                mode: 'index',
                intersect: false,
                axis: 'x'
            }
        }
    })

    const onUnmount = () => {
        stopTicker()
    }

    return {
        Line,
        chartData,
        chartOptions,
        priceStats,
        formatPrice,
        onUnmount
    }
}
