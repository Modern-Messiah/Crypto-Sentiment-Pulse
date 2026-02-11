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
                `${WS_URL}/api/v1/history/${props.symbol}?period=${currentPeriod.value}`,
            );
            const json = await res.json();
            if (json.history) {
                // Initial history might come from different sources/resolutions
                // Strict sorting and de-duplication is critical
                const uniqueHistory = [];
                const seenTimes = new Set();
                const sorted = [...json.history].sort((a, b) => a.time - b.time);

                for (const item of sorted) {
                    if (!seenTimes.has(item.time)) {
                        uniqueHistory.push(item);
                        seenTimes.add(item.time);
                    }
                }
                history.value = uniqueHistory;
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

    const lastUpdateTs = ref(0);

    // Watch for price changes to update history if chart is visible
    watch(
        () => data.value.price,
        (newVal) => {
            if (showChart.value && newVal) {
                const timestamp = data.value.timestamp || Date.now();

                // Dynamic throttling based on period to match backend storage/aggregation
                const THROTTLES = {
                    "1m": 1000,     // 1s
                    "5m": 5000,     // 5s
                    "15m": 10000,   // 10s (standard resolution)
                    "1h": 60000,    // 1m
                    "4h": 300000,   // 5m
                    "24h": 900000,  // 15m
                };

                const throttleMs = THROTTLES[currentPeriod.value] || 10000;

                // Only push if enough time has passed based on current resolution
                if (timestamp - lastUpdateTs.value < throttleMs) return;
                lastUpdateTs.value = timestamp;

                history.value.push({
                    time: timestamp,
                    price: newVal,
                });

                // Keep unique and sorted to prevent "backwards" lines
                const uniqueHistory = [];
                const seenTimes = new Set();

                // Sort by time and remove duplicates
                const sorted = [...history.value].sort((a, b) => a.time - b.time);

                for (const item of sorted) {
                    if (!seenTimes.has(item.time)) {
                        uniqueHistory.push(item);
                        seenTimes.add(item.time);
                    }
                }

                // Limit points to keep performance high
                // For 24h at 15m intervals, we only need ~100 points.
                // For 15m at 10s intervals, we need ~90 points.
                // 1000 points is plenty for any view.
                history.value = uniqueHistory.slice(-1000);
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
