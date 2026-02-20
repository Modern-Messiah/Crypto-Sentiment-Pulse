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

export const getPeriodMs = (period) => {
    const periods = {
        "1m": 60000,
        "5m": 300000,
        "15m": 900000,
        "1h": 3600000,
        "4h": 14400000,
        "24h": 86400000
    };
    return periods[period] || 900000;
};

export const sampleData = (baseData, period, nowAnchor) => {
    const targetPoints = {
        "1m": 60,
        "5m": 30,
        "15m": 30,
        "1h": 30,
        "4h": 30,
        "24h": 48
    };
    const MAX_POINTS = targetPoints[period] || 30;
    let processedData = baseData;

    if (baseData.length > MAX_POINTS) {
        const step = Math.ceil(baseData.length / MAX_POINTS);
        processedData = baseData.filter((_, i) => i % step === 0);
    }

    if (processedData.length > 0) {
        const periodMs = getPeriodMs(period);
        const windowStart = nowAnchor - periodMs;
        if (processedData[0].x > windowStart) {
            processedData = [{ x: windowStart, y: processedData[0].y }, ...processedData];
        }

        const lastPoint = baseData[baseData.length - 1];
        if (lastPoint.x < nowAnchor) {
            processedData = [...processedData, { x: nowAnchor, y: lastPoint.y }];
        }
    }
    return processedData;
};

export const formatDate = (value, period) => {
    const date = new Date(value)
    const h = date.getHours().toString().padStart(2, '0')
    const m = date.getMinutes().toString().padStart(2, '0')
    const s = date.getSeconds().toString().padStart(2, '0')

    if (period === '15m' || period === '1m' || period === '5m') {
        return `${h}:${m}:${s}`
    }
    if (period === '24h') {
        const day = date.getDate().toString().padStart(2, '0')
        const mon = (date.getMonth() + 1).toString().padStart(2, '0')
        return `${day}/${mon} ${h}:${m}`
    }
    return `${h}:${m}`
};
