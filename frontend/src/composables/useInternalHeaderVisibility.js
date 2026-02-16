import { ref, onMounted, onUnmounted } from 'vue'

export const useInternalHeaderVisibility = (threshold = 10) => {
    const isHeaderHidden = ref(false)
    let lastScrollTop = 0
    const THRESHOLD_DESKTOP = 1024

    const handleInternalScroll = (event) => {

        const scrollTop = event.target.scrollTop

        // Always show at the very top
        if (scrollTop <= threshold) {
            isHeaderHidden.value = false
            lastScrollTop = scrollTop
            return
        }

        // MOBILE LOGIC:
        // Hide on ANY downward scroll.
        // Reveal ONLY when returning to the absolute top (scrollTop <= threshold)
        if (scrollTop > lastScrollTop) {
            // Scrolling down
            if (scrollTop > 50) {
                isHeaderHidden.value = true
            }
        } else {
            // Scrolling up (Stay hidden on mobile as per user request, until top)
        }

        lastScrollTop = scrollTop
    }

    onMounted(() => {
        // Standard mounted logic
    })

    return {
        isHeaderHidden,
        handleInternalScroll
    }
}
