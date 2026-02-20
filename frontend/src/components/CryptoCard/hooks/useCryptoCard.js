import { computed, toRefs } from "vue";
import { usePriceAnimation } from "./usePriceAnimation";
import { usePriceHistory } from "./usePriceHistory";
import { formatPrice, getChangeClass, getChartColor, formatChange } from "../utils/formatters";

export const useCryptoCard = (props, emit) => {
    const { data, symbol } = toRefs(props);

    const price = computed(() => data.value.price);
    const { animationClass } = usePriceAnimation(price);

    const timestamp = computed(() => data.value.timestamp);
    const {
        showChart,
        history,
        loadingHistory,
        currentPeriod,
        toggleChart,
        changePeriod
    } = usePriceHistory(symbol, price, timestamp, emit);

    const formattedPrice = computed(() => formatPrice(data.value.price));
    const formattedChange = computed(() => formatChange(data.value.change_24h));
    const changeClass = computed(() => getChangeClass(data.value.change_24h));
    const chartColor = computed(() => getChartColor(data.value.change_24h));

    return {
        animationClass,
        showChart,
        history,
        loadingHistory,
        currentPeriod,
        toggleChart,
        changePeriod,
        formattedPrice,
        formattedChange,
        changeClass,
        chartColor,
        formatPrice
    };
};
