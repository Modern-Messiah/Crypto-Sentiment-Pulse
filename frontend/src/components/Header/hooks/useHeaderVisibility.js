import { ref, onMounted, onUnmounted } from 'vue'

export const useHeaderVisibility = (toolbarSelector = '.toolbar') => {
    const isHidden = ref(false)
    let lastScrollY = window.scrollY
    let ticking = false

    const updateVisibility = (scrollTarget = window) => {
        const isWindow = scrollTarget === window || scrollTarget === document
        const currentScrollY = isWindow ? window.scrollY : scrollTarget.scrollTop

        const selectors = ['.toolbar', '.table-header', '.nav-tabs', '.feed-header']
        let reachedTarget = false

        for (const selector of selectors) {
            const el = document.querySelector(selector)
            if (el) {
                const rect = el.getBoundingClientRect()
                if (rect.top <= 85) {
                    reachedTarget = true
                    break
                }
            }
        }

        const scrollingDown = currentScrollY > (scrollTarget._lastScrollY || 0)

        if ((scrollingDown && (isWindow ? currentScrollY > 100 : currentScrollY > 20)) || reachedTarget) {
            isHidden.value = true
        } else {
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
                updateVisibility(event.target)
            })
            ticking = true
        }
    }

    onMounted(() => {
        window.addEventListener('scroll', onScroll, { passive: true, capture: true })
    })

    onUnmounted(() => {
        window.removeEventListener('scroll', onScroll, { capture: true })
    })

    return {
        isHidden
    }
}
