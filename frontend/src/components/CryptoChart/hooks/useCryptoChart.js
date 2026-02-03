import { computed } from 'vue'
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

    const chartData = computed(() => {
        return {
            labels: props.history.map(h => {
                const date = new Date(h.time)
                return date.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })
            }),
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
                    data: props.history.map(h => h.price),
                    fill: true,
                    tension: 0.3
                }
            ]
        }
    })

    const chartOptions = computed(() => ({
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
                            return items[0].label
                        }
                        return ''
                    },
                    label: (context) => {
                        return formatPrice(context.raw)
                    },
                    afterLabel: (context) => {
                        const firstPrice = props.history[0]?.price
                        if (!firstPrice) return ''
                        const diff = context.raw - firstPrice
                        const percent = ((diff / firstPrice) * 100).toFixed(2)
                        const sign = diff >= 0 ? '+' : ''
                        return `${sign}${percent}% from start`
                    }
                }
            }
        },
        scales: {
            x: {
                display: true,
                grid: {
                    display: false,
                    drawBorder: false
                },
                ticks: {
                    color: 'rgba(255, 255, 255, 0.4)',
                    font: { size: 9 },
                    maxTicksLimit: 5,
                    maxRotation: 0
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
            intersect: false
        }
    }))

    return {
        Line,
        chartData,
        chartOptions,
        priceStats,
        formatPrice
    }
}
