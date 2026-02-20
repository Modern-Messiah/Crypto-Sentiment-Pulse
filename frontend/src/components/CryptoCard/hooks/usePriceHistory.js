import { ref, watch } from "vue";

export const usePriceHistory = (symbol, price, timestampRef, emit) => {
    const showChart = ref(false);
    const history = ref([]);
    const loadingHistory = ref(false);
    const currentPeriod = ref("15m");
    const lastUpdateTs = ref(0);

    const fetchHistory = async () => {
        loadingHistory.value = true;
        try {
            const WS_URL = import.meta.env.PROD ? "" : "http://localhost:8080";
            const res = await fetch(
                `${WS_URL}/api/v1/history/${symbol.value}?period=${currentPeriod.value}`,
            );
            const json = await res.json();
            if (json.history) {
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

        if (typeof emit === 'function') {
            emit('toggle-expand', symbol.value, showChart.value);
        }

        if (showChart.value && history.value.length === 0) {
            await fetchHistory();
        }
    };

    const changePeriod = async (period) => {
        currentPeriod.value = period;
        await fetchHistory();
    };

    watch(
        () => price.value,
        (newVal) => {
            if (showChart.value && newVal) {
                const timestamp = timestampRef.value || Date.now();

                const THROTTLES = {
                    "1m": 1000,
                    "5m": 15000,
                    "15m": 30000,
                    "1h": 120000,
                    "4h": 600000,
                    "24h": 1800000,
                };

                const throttleMs = THROTTLES[currentPeriod.value] || 10000;

                if (timestamp - lastUpdateTs.value < throttleMs) return;
                lastUpdateTs.value = timestamp;

                history.value.push({
                    time: timestamp,
                    price: newVal,
                });

                const uniqueHistory = [];
                const seenTimes = new Set();
                const sorted = [...history.value].sort((a, b) => a.time - b.time);

                for (const item of sorted) {
                    if (!seenTimes.has(item.time)) {
                        uniqueHistory.push(item);
                        seenTimes.add(item.time);
                    }
                }

                history.value = uniqueHistory.slice(-1000);
            }
        },
    );

    return {
        showChart,
        history,
        loadingHistory,
        currentPeriod,
        toggleChart,
        changePeriod
    };
};
