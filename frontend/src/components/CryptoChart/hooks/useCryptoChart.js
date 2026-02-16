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
import { formatPrice } from './chartUtils.js'
import { usePriceStats } from './usePriceStats.js'
import { useChartTicker } from './useChartTicker.js'
import { useChartConfig } from './useChartConfig.js'

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
    const { priceStats } = usePriceStats(props)
    const { nowAnchor, onUnmount } = useChartTicker(props)
    const { chartData, chartOptions } = useChartConfig(props, nowAnchor)

    return {
        Line,
        chartData,
        chartOptions,
        priceStats,
        formatPrice,
        onUnmount
    }
}
