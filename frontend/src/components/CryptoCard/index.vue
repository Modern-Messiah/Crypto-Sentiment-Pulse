<template>
    <div class="glass-card crypto-card" :class="animationClass">
        <div class="card-header">
            <div class="symbol-info">
                <h3>{{ symbol.replace("USDT", "") }}</h3>
                <span class="pair">/USDT</span>
            </div>
            <div class="change-badge" :class="changeClass">
                {{ formattedChange }}
            </div>
        </div>

        <div class="price-container">
            <div class="price">{{ formattedPrice }}</div>
            <button
                class="chart-btn"
                @click.stop="toggleChart"
                :class="{ active: showChart }"
                title="Toggle Chart"
            >
                <span v-if="!showChart">Chart</span>
                <span v-else>Close</span>
            </button>
        </div>

        <!-- Chart Section -->
        <div v-if="showChart" class="chart-wrapper animate-fade-in">
            <div class="chart-controls">
                <button
                    v-for="p in ['15m', '1h', '4h', '24h']"
                    :key="p"
                    class="range-btn"
                    :class="{ active: currentPeriod === p }"
                    @click="changePeriod(p)"
                >
                    {{ p }}
                </button>
            </div>

            <div v-if="loadingHistory" class="chart-loader">
                <div class="spinner"></div>
            </div>
            <CryptoChart
                v-else-if="history.length > 0"
                :history="history"
                :color="chartColor"
            />
            <div v-else class="chart-loader">
                No history data for {{ currentPeriod }}
            </div>
        </div>

        <div class="card-footer">
            <div class="stat">
                <span class="label">High</span>
                <span class="value">{{ formatPrice(data.high_24h) }}</span>
            </div>
            <div class="stat">
                <span class="label">Low</span>
                <span class="value">{{ formatPrice(data.low_24h) }}</span>
            </div>
        </div>
    </div>
</template>

<script setup>
import { defineProps, toRefs } from "vue";
import CryptoChart from "../CryptoChart/index.vue";
import { useCryptoCard } from "./CryptoCard.js";
import "./CryptoCard.css";

const props = defineProps({
    symbol: {
        type: String,
        required: true,
    },
    data: {
        type: Object,
        required: true,
        default: () => ({
            price: 0,
            change_24h: 0,
            high_24h: 0,
            low_24h: 0,
        }),
    },
});

const {
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
} = useCryptoCard(props);
</script>
