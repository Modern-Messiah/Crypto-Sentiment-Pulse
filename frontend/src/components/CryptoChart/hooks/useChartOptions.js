import { computed } from 'vue'
import { formatPrice, getPeriodMs, formatDate } from './chartUtils.js'

export const useChartOptions = (props, nowAnchor) => {
    return computed(() => {
        const period = props.period || '15m'
        const periodMs = getPeriodMs(period)
        const max = nowAnchor.value
        const min = max - periodMs

        return {
            responsive: true,
            maintainAspectRatio: false,
            animation: { duration: 300 },
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
                                return formatDate(items[0].raw.x, period)
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
                    grid: { display: false, drawBorder: false },
                    ticks: {
                        color: 'rgba(255, 255, 255, 0.4)',
                        font: { size: 9 },
                        maxTicksLimit: 5,
                        maxRotation: 0,
                        callback: (value) => formatDate(value, period)
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
    });
}
