import { ref, onMounted, onUnmounted, watch } from 'vue'
import { checkReachedTarget, calculateHeaderState } from './utils/visibilityLogic'

export const useHeaderVisibility = (toolbarSelector = '.toolbar', activeTab = null) => {
    const isHidden = ref(false)
    let ticking = false

    const STICKY_SELECTORS = ['.toolbar', '.table-header', '.nav-tabs', '.feed-header']
    const FEED_TABS = ['telegram', 'news']

    const updateVisibility = (scrollTarget = window) => {
        const isWindow = scrollTarget === window || scrollTarget === document
        const currentY = isWindow ? window.scrollY : scrollTarget.scrollTop
        const lastY = scrollTarget._lastScrollY || 0

        const reachedTarget = checkReachedTarget(STICKY_SELECTORS)

        const newState = calculateHeaderState({
            currentY,
            lastY,
            reachedTarget,
            isWindow
        })

        if (newState !== null) {
            isHidden.value = newState
        }

        scrollTarget._lastScrollY = currentY
        ticking = false
    }

    const onScroll = (event) => {
        const target = event.target
        const isWindow = target === window || target === document || target === document.documentElement
        const isFixedLayout = !!document.querySelector('.app-container.fixed-layout')

        if (ticking) return

        window.requestAnimationFrame(() => {
            if (isFixedLayout) {
                const scrollContainer = isWindow ? null : (target.closest('.messages-list') || target.closest('.news-list'))
                if (isWindow || scrollContainer) {
                    updateVisibility(isWindow ? window : scrollContainer)
                }
            } else if (isWindow) {
                updateVisibility(window)
            }
            ticking = false
        })
        ticking = true
    }

    const syncScrollAndState = (newTab, oldTab) => {
        const isSwitchingBetweenFeeds = FEED_TABS.includes(newTab) && FEED_TABS.includes(oldTab)

        window.requestAnimationFrame(() => {
            const scrollContainer = newTab === 'telegram'
                ? document.querySelector('.messages-list')
                : document.querySelector('.news-list')

            if (scrollContainer) {
                scrollContainer._lastScrollY = scrollContainer.scrollTop

                if (!isSwitchingBetweenFeeds) {
                    updateVisibility(scrollContainer)
                }
            }
        })

        if (!isSwitchingBetweenFeeds && newTab === 'prices') {
            isHidden.value = false
        }
    }

    if (activeTab) {
        watch(activeTab, syncScrollAndState, { immediate: true })
    }

    onMounted(() => {
        window.addEventListener('scroll', onScroll, { passive: true, capture: true })
        updateVisibility(window)
    })

    onUnmounted(() => {
        window.removeEventListener('scroll', onScroll, { capture: true })
    })

    return { isHidden }
}
