import { describe, expect, test, vi } from 'vitest'
import '@testing-library/jest-dom/vitest'
import { render, screen } from '@testing-library/svelte'
import * as navigationMethods from '$app/navigation'
import Navigation from './Navigation.svelte'

describe('/Navigation.svelte', () => {
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

  test('should navigate to homepage when click on homepage button', async () => {
    // Given
    const spy = vi
      .spyOn(navigationMethods, 'goto')
      .mockImplementation(() => Promise.resolve())
    render(Navigation, { currentItem: 'home' })

    // When
    const link = screen.getByTestId('homepage-link')
    link.click()

    // Then
    expect(spy).toHaveBeenCalledWith('/')
  })

  test('should highlight agenda item', async () => {
    // Given
    const { container } = render(Navigation, { currentItem: 'agenda' })

    // Then
    const highlight = container.querySelector('.highlight')
    expect(highlight).toHaveTextContent('Agenda')
  })

  test('should navigate to agenda when click on agenda button', async () => {
    // Given
    const spy = vi
      .spyOn(navigationMethods, 'goto')
      .mockImplementation(() => Promise.resolve())
    render(Navigation, { currentItem: 'home' })

    // When
    const link = screen.getByTestId('agenda-link')
    link.click()

    // Then
    expect(spy).toHaveBeenCalledWith('/#/agenda')
  })
})
