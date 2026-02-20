/**
 * Checks if any of the target elements have reached the sticky threshold (near top of viewport)
 */
export const checkReachedTarget = (selectors, threshold = 90) => {
    for (const selector of selectors) {
        const el = document.querySelector(selector)
        if (el) {
            const rect = el.getBoundingClientRect()
            if (rect.top <= threshold) {
                return true
            }
        }
    }
    return false
}

/**
 * Calculates the header visibility state based on current scroll position and direction
 */
export const calculateHeaderState = (params) => {
    const {
        currentY,
        lastY,
        reachedTarget,
        isWindow,
        showThreshold = 60,
        hideThreshold = 100,
        upThreshold = 150
    } = params

    const scrollingDown = currentY > lastY

    // 1. Close to top - always show
    if (currentY <= showThreshold) {
        return false // isHidden = false
    }

    // 2. Scrolling up near top - show (perceived responsiveness)
    if (!scrollingDown && currentY < upThreshold) {
        return false
    }

    // 3. Scrolling down - hide if criteria met
    if (scrollingDown) {
        const desktopThreshold = isWindow ? hideThreshold : showThreshold
        if (reachedTarget || currentY > desktopThreshold) {
            return true // isHidden = true
        }
    }

    // Default: keep current state (caller should manage this)
    return null
}
