import { ref, onMounted, onUnmounted, watch } from 'vue'

export const useHeaderVisibility = (toolbarSelector = '.toolbar', activeTab = null) => {
    const isHidden = ref(false)
    let ticking = false
    const THRESHOLD_DESKTOP = 1024

    const updateVisibility = (scrollTarget = window) => {
        const isWindow = scrollTarget === window || scrollTarget === document
        const currentScrollY = isWindow ? window.scrollY : scrollTarget.scrollTop

        // Check if any secondary navigation element is at the top
        const selectors = ['.toolbar', '.table-header', '.nav-tabs', '.feed-header']
        let reachedTarget = false

        for (const selector of selectors) {
            const el = document.querySelector(selector)
            if (el) {
                const rect = el.getBoundingClientRect()
                if (rect.top <= 90) {
                    reachedTarget = true
                    break
                }
            }
        }

        const lastY = scrollTarget._lastScrollY || 0
        const scrollingDown = currentScrollY > lastY
        const scrollDelta = Math.abs(currentScrollY - lastY)

        // UNIFIED LOGIC:
        // 1. If we are at the very top (or close to it), always SHOW
        if (currentScrollY <= 15) {
            isHidden.value = false
        }
        // 2. We no longer show on scroll up (user preference)
        // 3. If we are scrolling DOWN and passed a threshold OR secondary nav reached top, HIDE
        else if (scrollingDown) {
            if (reachedTarget || (isWindow ? currentScrollY > 100 : currentScrollY > 60)) {
                isHidden.value = true
            }
        }

        scrollTarget._lastScrollY = currentScrollY
        ticking = false
    }

    const onScroll = (event) => {
        const target = event.target
        const isWindow = target === window || target === document || target === document.documentElement
        const isFixedLayout = !!document.querySelector('.app-container.fixed-layout')

        if (isFixedLayout) {
            const scrollContainer = isWindow ? null : (target.closest('.messages-list') || target.closest('.news-list'))
            if (!isWindow && !scrollContainer) return

            if (!ticking) {
                window.requestAnimationFrame(() => {
                    updateVisibility(isWindow ? window : scrollContainer)
                })
                ticking = true
            }
        } else {
            if (!isWindow) return

            if (!ticking) {
                window.requestAnimationFrame(() => {
                    updateVisibility(window)
                })
                ticking = true
            }
        }
    }

    if (activeTab) {
        watch(activeTab, () => {
            // Trigger check on next tick and again after small delay to be sure
            const performCheck = () => {
                const isFixedLayout = !!document.querySelector('.app-container.fixed-layout')
                if (isFixedLayout) {
                    const scrollContainer = document.querySelector('.messages-list') || document.querySelector('.news-list')
                    updateVisibility(scrollContainer || window)
                } else {
                    updateVisibility(window)
                }
            }
            window.requestAnimationFrame(performCheck)
            setTimeout(performCheck, 50)
        }, { immediate: true })
    }

    onMounted(() => {
        window.addEventListener('scroll', onScroll, { passive: true, capture: true })
        updateVisibility(window)
    })

    onUnmounted(() => {
        window.removeEventListener('scroll', onScroll, { capture: true })
    })

    return {
        isHidden
    }
}
