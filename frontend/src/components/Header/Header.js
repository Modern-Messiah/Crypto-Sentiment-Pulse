export const useHeader = () => {
    const formatTime = (date) => {
        if (!date) return ''
        return date.toLocaleTimeString('ru-RU', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        })
    }

    return {
        formatTime
    }
}
