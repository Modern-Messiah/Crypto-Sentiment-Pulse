export const formatPrice = (value) => {
    if (value >= 1000) {
        return '$' + value.toLocaleString('en-US', { maximumFractionDigits: 0 })
    } else if (value >= 1) {
        return '$' + value.toFixed(2)
    } else {
        return '$' + value.toFixed(4)
    }
}

export const hexToRgba = (hex, alpha) => {
    const r = parseInt(hex.slice(1, 3), 16)
    const g = parseInt(hex.slice(3, 5), 16)
    const b = parseInt(hex.slice(5, 7), 16)
    return `rgba(${r}, ${g}, ${b}, ${alpha})`
}
