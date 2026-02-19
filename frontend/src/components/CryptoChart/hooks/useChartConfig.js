import { computed } from 'vue'
import { hexToRgba, formatPrice } from './chartUtils.js'

export const useChartConfig = (props, nowAnchor) => {
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
                    pointRadius: props.period === '1m' ? 2 : 0,
                    pointHoverRadius: 5,
                    pointHoverBackgroundColor: props.color,
                    pointHoverBorderColor: '#fff',
                    pointHoverBorderWidth: 2,
                    data: computed(() => {
                        const baseData = props.history.map(h => ({ x: h.time, y: h.price }));

                        // Sampling logic to keep chart smooth
                        const targetPoints = {
                            "1m": 60,   // every 1s
                            "5m": 30,   // every 10s
                            "15m": 30,  // every 30s
                            "1h": 30,   // every 2m
                            "4h": 30,   // every 8m
                            "24h": 48   // every 30m
                        };
                        const MAX_POINTS = targetPoints[props.period] || 30;
                        let processedData = baseData;

                        if (baseData.length > MAX_POINTS) {
                            const step = Math.ceil(baseData.length / MAX_POINTS);
                            processedData = baseData.filter((_, i) => i % step === 0);
                        }

                        if (processedData.length > 0) {
                            // Fill left edge: ensure line starts from the visible window start
                            const periodMs = { "1m": 60000, "5m": 300000, "15m": 900000, "1h": 3600000, "4h": 14400000, "24h": 86400000 };
                            const windowStart = nowAnchor.value - (periodMs[props.period] || 900000);
                            if (processedData[0].x > windowStart) {
                                processedData = [{ x: windowStart, y: processedData[0].y }, ...processedData];
                            }

                            // Fill right edge: extend line to current time
                            const lastPoint = baseData[baseData.length - 1]; // Use original last point
                            if (lastPoint.x < nowAnchor.value) {
                                processedData = [...processedData, { x: nowAnchor.value, y: lastPoint.y }];
                            }
                        }
                        return processedData;
                    }).value,
                    spanGaps: true,
                    fill: true,
                    tension: props.period === '1m' ? 0.1 : 0.3
                }
            ]
        }
    })

    const chartOptions = computed(() => {
        const period = props.period || '15m'
        let periodMs = 15 * 60 * 1000
        if (period === '1m') periodMs = 60 * 1000
        else if (period === '5m') periodMs = 5 * 60 * 1000
        else if (period === '1h') periodMs = 60 * 60 * 1000
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

                                if (period === '15m' || period === '1m' || period === '5m') return `${h}:${m}:${s}`
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
                            if (period === '15m' || period === '1m' || period === '5m') {
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

    return { chartData, chartOptions }
}
