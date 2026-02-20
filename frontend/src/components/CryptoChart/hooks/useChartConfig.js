import { useChartData } from './useChartData.js'
import { useChartOptions } from './useChartOptions.js'

export const useChartConfig = (props, nowAnchor) => {
    const chartData = useChartData(props, nowAnchor)
    const chartOptions = useChartOptions(props, nowAnchor)

    return { chartData, chartOptions }
}
