import { ref, watch } from 'vue'

export const useCryptoTableRow = (coin) => {
    const animationClass = ref('')
    const animationTimeout = ref(null)

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

    return {
        animationClass
    }
}
