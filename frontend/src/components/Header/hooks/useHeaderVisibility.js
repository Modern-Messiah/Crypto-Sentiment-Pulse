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
        // 1. If we are close to the top, always SHOW (increased threshold for responsiveness)
        if (currentScrollY <= 60) {
            isHidden.value = false
        }
        // 2. Show immediately on scroll up if near the top (removes "perceived delay")
        else if (!scrollingDown && currentScrollY < 150) {
            isHidden.value = false
        }
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
        watch(activeTab, (newTab, oldTab) => {
            // When switching between telegram and news, preserve header state as-is
            const feedTabs = ['telegram', 'news']
            const isSwitchingBetweenFeeds = feedTabs.includes(newTab) && feedTabs.includes(oldTab)

            if (isSwitchingBetweenFeeds) {
                // Just sync _lastScrollY on the new container so next scroll doesn't glitch
                window.requestAnimationFrame(() => {
                    const scrollContainer = newTab === 'telegram'
                        ? document.querySelector('.messages-list')
                        : document.querySelector('.news-list')
                    if (scrollContainer) {
                        scrollContainer._lastScrollY = scrollContainer.scrollTop
                    }
                })
                return // keep isHidden as-is
            }

            // Switching to Prices — always show header
            if (newTab === 'prices') {
                isHidden.value = false
                return
            }

            // Switching from Prices to a feed tab — run visibility check
            window.requestAnimationFrame(() => {
                const scrollContainer = newTab === 'telegram'
                    ? document.querySelector('.messages-list')
                    : document.querySelector('.news-list')

                if (scrollContainer) {
                    scrollContainer._lastScrollY = scrollContainer.scrollTop
                    updateVisibility(scrollContainer)
                }
            })
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
