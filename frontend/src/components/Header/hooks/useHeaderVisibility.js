import { ref, onMounted, onUnmounted } from 'vue'

export const useHeaderVisibility = (toolbarSelector = '.toolbar') => {
    const isHidden = ref(false)
    let lastScrollY = window.scrollY
    let ticking = false

    const updateVisibility = () => {
        const currentScrollY = window.scrollY
        const toolbar = document.querySelector(toolbarSelector)

        // 1. Check for scroll direction
        const scrollingDown = currentScrollY > lastScrollY

        // 2. Check for toolbar collision/reach
        let reachedToolbar = false
        if (toolbar) {
            const rect = toolbar.getBoundingClientRect()
            // If toolbar top is near the top of the viewport (considering header height)
            // Header height is roughly 80px
            reachedToolbar = rect.top <= 80
        }

        // Hide if:
        // - Scrolling down AND we are not at the very top
        // - OR we reached/passed the toolbar
        if ((scrollingDown && currentScrollY > 100) || reachedToolbar) {
            isHidden.value = true
        } else {
            // Show if:
            // - Scrolling up
            // - AND we haven't reached the toolbar (or we are moving away from it upwards)
            // Actually, if we are scrolling up, we usually want to show it immediately
            // unless we are still "inside" the toolbar area.
            if (!scrollingDown) {
                isHidden.value = false
            }
        }

        lastScrollY = currentScrollY
        ticking = false
    }

    const onScroll = () => {
        if (!ticking) {
            window.requestAnimationFrame(() => {
                updateVisibility()
            })
            ticking = true
        }
    }

    onMounted(() => {
        window.addEventListener('scroll', onScroll, { passive: true })
    })

    onUnmounted(() => {
        window.removeEventListener('scroll', onScroll)
    })

    return {
        isHidden
    }
}
