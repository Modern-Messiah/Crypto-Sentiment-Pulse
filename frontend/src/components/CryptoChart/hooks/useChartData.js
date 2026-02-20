import { computed } from 'vue'
import { hexToRgba, sampleData } from './chartUtils.js'

export const useChartData = (props, nowAnchor) => {
    return computed(() => {
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
                        return sampleData(baseData, props.period, nowAnchor.value);
                    }).value,
                    spanGaps: true,
                    fill: true,
                    tension: props.period === '1m' ? 0.1 : 0.3
                }
            ]
        }
    });
}
