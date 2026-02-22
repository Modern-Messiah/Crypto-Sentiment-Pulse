import { describe, it, expect } from 'vitest'
import { useNavigation } from '../../composables/useNavigation'

describe('useNavigation composable', () => {
    it('initializes with default values', () => {
        const { activeTab, viewMode, tabs } = useNavigation()

        expect(activeTab.value).toBe('prices')
        expect(viewMode.value).toBe('grid')
        expect(tabs.length).toBeGreaterThan(0)
    })

    it('can set a new tab', () => {
        const { activeTab, transitionName, setTab } = useNavigation()

        // Change to telegram tab
        setTab('telegram', 1) // index 1 is right of index 0

        expect(activeTab.value).toBe('telegram')
        expect(transitionName.value).toBe('slide-left')

        // Change back to prices
        setTab('prices', 0)

        expect(activeTab.value).toBe('prices')
        expect(transitionName.value).toBe('slide-right')
    })

    it('can set view mode', () => {
        const { viewMode, setViewMode } = useNavigation()

        setViewMode('list')
        expect(viewMode.value).toBe('list')

        setViewMode('grid')
        expect(viewMode.value).toBe('grid')
    })
})
