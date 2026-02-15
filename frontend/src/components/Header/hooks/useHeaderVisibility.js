import { ref, onMounted, onUnmounted } from 'vue'

export const useHeaderVisibility = (toolbarSelector = '.toolbar') => {
    const isHidden = ref(false)
    let lastScrollY = window.scrollY
    let ticking = false

    const updateVisibility = (scrollTarget = window) => {
        const isWindow = scrollTarget === window || scrollTarget === document
        const currentScrollY = isWindow ? window.scrollY : scrollTarget.scrollTop

        // Target selectors that should trigger header hide when reached
        const selectors = ['.toolbar', '.table-header', '.nav-tabs', '.feed-header']
        let reachedTarget = false

        for (const selector of selectors) {
            const el = document.querySelector(selector)
            if (el) {
                const rect = el.getBoundingClientRect()
                // If element top is near the top of the viewport (considering header height ~80px)
                if (rect.top <= 85) {
                    reachedTarget = true
                    break
                }
            }
        }

        const scrollingDown = currentScrollY > (scrollTarget._lastScrollY || 0)

        // Hide if:
        // - Scrolling down AND we are not at the very top
        // - OR we reached/passed any of our targets
        if ((scrollingDown && (isWindow ? currentScrollY > 100 : currentScrollY > 20)) || reachedTarget) {
            isHidden.value = true
        } else {
            // Show if scrolling up
            if (!scrollingDown) {
                isHidden.value = false
            }
        }

        scrollTarget._lastScrollY = currentScrollY
        if (isWindow) lastScrollY = currentScrollY
        ticking = false
    }

    const onScroll = (event) => {
        if (!ticking) {
            window.requestAnimationFrame(() => {
                // If it's an internal scroll, we might need a different logic
                // But for header hide, we usually just care if ANY scroll happens down
                updateVisibility(event.target)
            })
            ticking = true
        }
    }

    onMounted(() => {
        // Use capture: true to catch scrolls from internal containers (bubbles don't work for scroll)
        window.addEventListener('scroll', onScroll, { passive: true, capture: true })
    })

    onUnmounted(() => {
        window.removeEventListener('scroll', onScroll, { capture: true })
    })

    return {
        isHidden
    }
}
