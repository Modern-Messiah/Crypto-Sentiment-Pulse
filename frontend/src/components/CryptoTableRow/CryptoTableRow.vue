<template>
  <tr :class="animationClass">
    <SymbolCell :symbol="coin.symbol" />
    <PriceCell :price="coin.price" />
    <ChangeCell :change="coin.change_24h" />
    <RsiCell :rsi="coin.rsi" />
    <TvlCell :tvl="coin.tvl" :change="coin.tvl_change_1d" />
    <VolumeCell :volume="coin.volume_24h" />
  </tr>
</template>

<script setup>
import { toRefs } from 'vue'
import { useCryptoTableRow } from './hooks/useCryptoTableRow.js'
import SymbolCell from './components/SymbolCell.vue'
import PriceCell from './components/PriceCell.vue'
import ChangeCell from './components/ChangeCell.vue'
import RsiCell from './components/RsiCell.vue'
import TvlCell from './components/TvlCell.vue'
import VolumeCell from './components/VolumeCell.vue'
import './styles/CryptoTableRow.css'

const props = defineProps({
  coin: {
    type: Object,
    required: true
  }
})

const { coin } = toRefs(props)
const { animationClass } = useCryptoTableRow(coin)
</script>
