import { beforeEach, describe, expect, test, vi } from 'vitest'
import '@testing-library/jest-dom/vitest'
import { render } from '@testing-library/svelte'
import Navigation from './Navigation.svelte'

describe('/Navigation.svelte', () => {
  beforeEach(async () => {
    vi.mock('$env/static/public', async (importOriginal) => {
      const original = (await importOriginal()) as Record<string, any>
      return Promise.resolve({
        ...original,
        PUBLIC_FEATUREFLAG_REQUESTS_ENABLED: 'true',
      })
    })
  })

  test('should highlight nothing', async () => {
    // Given
    const { container } = render(Navigation)

    // Then
    const highlight = container.querySelector('.highlight')
    expect(highlight).toBeNull()
  })

  test('should highlight home item', async () => {
    // Given
    const { container } = render(Navigation, { currentItem: 'home' })

    // Then
    const highlight = container.querySelector('.highlight')
    expect(highlight).toHaveTextContent('Accueil')
  })

  test('should highlight agenda item', async () => {
    // Given
    const { container } = render(Navigation, { currentItem: 'agenda' })

    // Then
    const highlight = container.querySelector('.highlight')
    expect(highlight).toHaveTextContent('Agenda')
  })

  test('should highlight followup item', async () => {
    // Given
    const { container } = render(Navigation, { currentItem: 'requests' })

    // Then
    const highlight = container.querySelector('.highlight')
    expect(highlight).toHaveTextContent('Suivi')
  })
})
