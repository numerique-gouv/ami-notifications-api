import { describe, expect, test } from 'vitest'
import '@testing-library/jest-dom/vitest'
import { render } from '@testing-library/svelte'
import NotificationIcon from '$lib/NotificationIcon.svelte'

describe('/NotificationIcon.svelte', () => {
  test('icon is absent, should display default icon', async () => {
    // When
    const { container } = render(NotificationIcon, {
      defaultIcon: 'default-icon',
    })

    // Then
    const icon = container.querySelector('.notification__icon')
    expect(icon).toHaveClass('default-icon')
  })
  test('icon is undefined, should display default icon', async () => {
    // When
    const { container } = render(NotificationIcon, {
      icon: undefined,
      defaultIcon: 'default-icon',
    })

    // Then
    const icon = container.querySelector('.notification__icon')
    expect(icon).toHaveClass('default-icon')
  })
  test('icon is empty, should display default icon', async () => {
    // When
    const { container } = render(NotificationIcon, {
      icon: '',
      defaultIcon: 'default-icon',
    })

    // Then
    const icon = container.querySelector('.notification__icon')
    expect(icon).toHaveClass('default-icon')
  })
  test('icon is unknown, should display default icon', async () => {
    // When
    const { container } = render(NotificationIcon, {
      icon: 'unknown',
      defaultIcon: 'default-icon',
    })

    // Then
    const icon = container.querySelector('.notification__icon')
    expect(icon).toHaveClass('default-icon')
  })
  test('icon is known, should display icon', async () => {
    // When
    const { container } = render(NotificationIcon, {
      icon: 'fr-icon-mail-star-line',
      defaultIcon: 'default-icon',
    })

    // Then
    const icon = container.querySelector('.notification__icon')
    expect(icon).toHaveClass('fr-icon-mail-star-line')
    expect(icon).not.toHaveClass('default-icon')
  })
})
