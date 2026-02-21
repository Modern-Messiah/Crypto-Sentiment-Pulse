export const formatTime = (dateStr) => {
    if (!dateStr) return ''
    const date = new Date(dateStr)
    return date.toLocaleTimeString('ru-RU', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    })
}

export const formatViews = (views) => {
    if (!views) return '0'
    if (views >= 1000000) return (views / 1000000).toFixed(1) + 'M'
    if (views >= 1000) return (views / 1000).toFixed(1) + 'K'
    return views.toString()
}

export const formatTelegramText = (text) => {
    if (!text) return ''

    let formatted = text
    formatted = formatted.replace(/\[([^\]]+)\]\(tg:\/\/search_hashtag[^\s)]*\)/g, '$1')
    formatted = formatted.replace(/\*{3,}/g, '')
    formatted = formatted.replace(/-{3,}/g, '')
    formatted = formatted
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')

    formatted = formatted.replace(/\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g, (match, linkText, url) => {
        return `<a href="${url}" target="_blank" rel="noopener noreferrer">${linkText}</a>`
    })

    const urlRegex = /(?<![\]\(]|href=")(https?:\/\/[^\s<]+)(?![^<]*?<\/a>)/g
    formatted = formatted.replace(urlRegex, (url) => {
        return `<a href="${url}" target="_blank" rel="noopener noreferrer">${url}</a>`
    })

    formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    formatted = formatted.replace(/#\s+/g, '#')
    formatted = formatted.replace(/(^|\s)(#[\w\u0400-\u04FF]+)/g, '$1<span class="hashtag">$2</span>')
    formatted = formatted.replace(/\n{3,}/g, '\n\n')
    formatted = formatted.replace(/\n/g, '<br>')

    return formatted
}
