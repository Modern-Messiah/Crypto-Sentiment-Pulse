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

        // Find the active button within the container
        const activeButton = containerRef.value.querySelector('.active')

        if (activeButton) {
            const { offsetLeft, offsetWidth } = activeButton
            indicatorStyle.value = {
                left: `${offsetLeft}px`,
                width: `${offsetWidth}px`,
                opacity: 1,
                transition: isInitialized.value ? 'all 0.35s cubic-bezier(0.4, 0, 0.2, 1)' : 'none'
            }
            // Allow transition only after the first successful positioning
            if (!isInitialized.value) {
                setTimeout(() => {
                    isInitialized.value = true
                }, 50)
            }
        } else {
            indicatorStyle.value.opacity = 0
        }
    }

    // Watch for changes in active value
    watch(activeValue, () => {
        updateIndicator()
    })

    // Watch for the container becoming available (e.g. after v-if changes)
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
        // Initialize ResizeObserver
        resizeObserver = new ResizeObserver(() => {
            updateIndicator()
        })

        // If the element is already there, start observing
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
