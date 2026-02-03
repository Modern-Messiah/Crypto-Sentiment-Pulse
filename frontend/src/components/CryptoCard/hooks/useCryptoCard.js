import { computed, toRefs, ref, watch } from "vue";

export const useCryptoCard = (props) => {
    const { data } = toRefs(props);
    const animationClass = ref("");
    const animationTimeout = ref(null);

    const showChart = ref(false);
    const history = ref([]);
    const loadingHistory = ref(false);
    const currentPeriod = ref("15m");

    const fetchHistory = async () => {
        loadingHistory.value = true;
        try {
            const WS_URL = import.meta.env.PROD ? "" : "http://localhost:8080";
            const res = await fetch(
                `${WS_URL}/api/history/${props.symbol}?period=${currentPeriod.value}`,
            );
            const json = await res.json();
            if (json.history) {
                history.value = json.history;
            }
        } catch (e) {
            console.error("Failed to fetch history", e);
        } finally {
            loadingHistory.value = false;
        }
    };

    const toggleChart = async () => {
        showChart.value = !showChart.value;
        if (showChart.value && history.value.length === 0) {
            await fetchHistory();
        }
    };

    const changePeriod = async (period) => {
        currentPeriod.value = period;
        await fetchHistory();
    };

    // Watch for price changes to update history if chart is visible and on 15m period
    watch(
        () => data.value.price,
        (newVal) => {
            if (showChart.value && newVal && currentPeriod.value === "15m") {
                history.value.push({
                    time: Date.now(),
                    price: newVal,
                });
                if (history.value.length > 100) history.value.shift();
            }
        },
    );

    // Watch for price changes to trigger animation
    watch(
        () => data.value.price,
        (newVal, oldVal) => {
            if (!oldVal) return;

            // Clear previous timeout
            if (animationTimeout.value) clearTimeout(animationTimeout.value);

            // Set new animation class
            if (newVal > oldVal) {
                animationClass.value = "price-up-trigger";
            } else if (newVal < oldVal) {
                animationClass.value = "price-down-trigger";
            }

            // Remove class after animation finishes
            animationTimeout.value = setTimeout(() => {
                animationClass.value = "";
            }, 1000);
        },
    );

    const formattedPrice = computed(() => {
        return formatPrice(data.value.price);
    });

    const formattedChange = computed(() => {
        const val = data.value.change_24h;
        return `${val > 0 ? "+" : ""}${val.toFixed(2)}%`;
    });

    const changeClass = computed(() => {
        const val = data.value.change_24h;
        if (val > 0) return "text-success bg-success-dim";
        if (val < 0) return "text-danger bg-danger-dim";
        return "text-muted";
    });

    const chartColor = computed(() => {
        return data.value.change_24h >= 0 ? "#00d084" : "#ff4757";
    });

    function formatPrice(val) {
        if (!val) return "0.00";
        return new Intl.NumberFormat("en-US", {
            style: "currency",
            currency: "USD",
            minimumFractionDigits: val < 1 ? 4 : 2,
            maximumFractionDigits: val < 1 ? 4 : 2,
        }).format(val);
    }

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
