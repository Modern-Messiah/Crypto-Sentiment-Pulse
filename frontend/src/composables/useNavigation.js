import { ref } from 'vue'

export function useNavigation() {
    const viewMode = ref('grid')
    const viewTransitionName = ref('slide-left')
    const activeTab = ref('prices')
    const transitionName = ref('slide-left')

    const tabs = [
        { id: 'prices', label: 'Prices' },
        { id: 'telegram', label: 'Telegram' },
        { id: 'news', label: 'CryptoPanic' }
    ]

    const setViewMode = (mode) => {
        if (mode === viewMode.value) return

        if (mode === 'table') {
            viewTransitionName.value = 'slide-left'
        } else {
            viewTransitionName.value = 'slide-right'
        }
        viewMode.value = mode
    }

    const setTab = (tabId) => {
        const currentIndex = tabs.findIndex(t => t.id === activeTab.value)
        const nextIndex = tabs.findIndex(t => t.id === tabId)

        if (nextIndex > currentIndex) {
            transitionName.value = 'slide-left'
        } else {
            transitionName.value = 'slide-right'
        }

        activeTab.value = tabId
    }

    return {
        viewMode,
        viewTransitionName,
        activeTab,
        transitionName,
        tabs,
        setViewMode,
        setTab
    }
}
