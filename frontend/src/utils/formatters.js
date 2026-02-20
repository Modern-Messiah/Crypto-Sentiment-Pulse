export const formatPrice = (val) => {
    if (!val) return "$0.00";
    return new Intl.NumberFormat("en-US", {
        style: "currency",
        currency: "USD",
        minimumFractionDigits: val < 1 ? 4 : 2,
        maximumFractionDigits: val < 1 ? 4 : 2,
    }).format(val);
};

export const formatChange = (val) => {
    if (val === undefined || val === null) return "0.00%";
    return `${val > 0 ? "+" : ""}${val.toFixed(2)}%`;
};

export const getChangeClass = (val) => {
    if (val > 0) return "text-success";
    if (val < 0) return "text-danger";
    return "text-muted";
};

export const getBadgeChangeClass = (val) => {
    if (val > 0) return "text-success bg-success-dim";
    if (val < 0) return "text-danger bg-danger-dim";
    return "text-muted";
};

export const formatTvl = (value) => {
    if (!value) return '$0';
    if (value >= 1e9) return '$' + (value / 1e9).toFixed(2) + 'B';
    if (value >= 1e6) return '$' + (value / 1e6).toFixed(1) + 'M';
    return '$' + value.toLocaleString();
};

export const formatTVL = formatTvl;

export const formatTvlChange = (val) => {
    if (val === undefined || val === null || val === 0) return '0.0%';
    return `${val > 0 ? '+' : ''}${val.toFixed(1)}%`;
};

export const getTvlChangeClass = (val) => {
    if (val < 0) return 'text-danger';
    return 'text-success';
};

export const formatVolume = (val) => {
    if (!val) return '0';
    if (val >= 1e9) return `$${(val / 1e9).toFixed(2)}B`;
    if (val >= 1e6) return `$${(val / 1e6).toFixed(2)}M`;
    if (val >= 1e3) return `$${(val / 1e3).toFixed(2)}K`;
    return `$${val.toFixed(0)}`;
};

export const formatMoneyFlow = (value) => {
    if (value === undefined || value === null) return '';
    const prefix = value >= 0 ? '+$' : '-$';
    const absValue = Math.abs(value);
    if (absValue >= 1e9) return prefix + (absValue / 1e9).toFixed(1) + 'B';
    if (absValue >= 1e6) return prefix + (absValue / 1e6).toFixed(1) + 'M';
    return prefix + absValue.toLocaleString();
};

export const formatRsi = (rsi) => {
    if (rsi === undefined || rsi === null) return 'N/A';
    return `${rsi}%`;
};

export const getRsiColor = (rsi) => {
    if (rsi >= 70) return '#ff4757';
    if (rsi <= 30) return '#2ed573';
    return '#eccc68';
};

export const getRsiClass = (rsi) => {
    if (rsi === undefined || rsi === null) return 'text-muted';
    if (rsi >= 70) return 'text-danger';
    if (rsi <= 30) return 'text-success';
    return 'text-warning';
};

export const getChartColor = (val) => {
    return val >= 0 ? "#00d084" : "#ff4757";
};
