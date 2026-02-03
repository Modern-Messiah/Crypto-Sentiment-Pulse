import { ref, watch } from 'vue'

export const useCryptoTableRow = (coin) => {
    const animationClass = ref('')
    const animationTimeout = ref(null)

    // Watch for price changes to trigger animation
    watch(() => coin.value.price, (newVal, oldVal) => {
        if (!oldVal) return

        if (animationTimeout.value) clearTimeout(animationTimeout.value)

        if (newVal > oldVal) {
            animationClass.value = 'row-flash-green'
        } else if (newVal < oldVal) {
            animationClass.value = 'row-flash-red'
        }

        animationTimeout.value = setTimeout(() => {
            animationClass.value = ''
        }, 800)
    })

    function getChangeClass(val) {
        if (val > 0) return 'text-success'
        if (val < 0) return 'text-danger'
        return 'text-muted'
    }

    function formatPrice(val) {
        if (!val) return '$0.00'
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: val < 1 ? 4 : 2,
            maximumFractionDigits: val < 1 ? 4 : 2
        }).format(val)
    }

    function formatChange(val) {
        if (val === undefined) return '0.00%'
        return `${val > 0 ? '+' : ''}${val.toFixed(2)}%`
    }

    function formatVolume(val) {
        if (!val) return '0'
        if (val >= 1000000) {
            return `$${(val / 1000000).toFixed(2)}M`
        }
        if (val >= 1000) {
            return `$${(val / 1000).toFixed(2)}K`
        }
        return `$${val.toFixed(0)}`
    }

    return {
        animationClass,
        getChangeClass,
        formatPrice,
        formatChange,
        formatVolume
    }
}
