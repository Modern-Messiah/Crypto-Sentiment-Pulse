import { ref, watch, onMounted, onUnmounted, nextTick } from 'vue'

export function useSlidingIndicator(containerRef, activeValue) {
    const isInitialized = ref(false)
    const indicatorStyle = ref({
        left: '0px',
        width: '0px',
        opacity: 0,
        transition: 'none'
    })

    let resizeObserver = null

    const updateIndicator = async () => {
        await nextTick()
        if (!containerRef.value) return

        const activeButton = containerRef.value.querySelector('.active')

        if (activeButton) {
            const { offsetLeft, offsetWidth } = activeButton
            indicatorStyle.value = {
                left: `${offsetLeft}px`,
                width: `${offsetWidth}px`,
                opacity: 1,
                transition: isInitialized.value ? 'all 0.35s cubic-bezier(0.4, 0, 0.2, 1)' : 'none'
            }
            if (!isInitialized.value) {
                setTimeout(() => {
                    isInitialized.value = true
                }, 50)
            }
        } else {
            indicatorStyle.value.opacity = 0
        }
    }

    watch(activeValue, () => {
        updateIndicator()
    })

    watch(containerRef, (newEl, oldEl) => {
        if (oldEl && resizeObserver) {
            resizeObserver.unobserve(oldEl)
        }
        if (newEl) {
            updateIndicator()
            if (resizeObserver) {
                resizeObserver.observe(newEl)
            }
        }
    }, { immediate: true })

    onMounted(() => {
        resizeObserver = new ResizeObserver(() => {
            updateIndicator()
        })

        if (containerRef.value) {
            updateIndicator()
            resizeObserver.observe(containerRef.value)
        }
    })

    onUnmounted(() => {
        if (resizeObserver) {
            resizeObserver.disconnect()
        }
    })

    return {
        indicatorStyle,
        updateIndicator
    }
}
