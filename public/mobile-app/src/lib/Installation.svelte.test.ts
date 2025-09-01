import { describe, test, expect } from 'vitest'
import '@testing-library/jest-dom/vitest'
import { render, screen } from '@testing-library/svelte'
import Installation from './Installation.svelte'

describe('/Installation.svelte', () => {
  test('should render h1', () => {
    // When
    render(Installation)

    // Then
    const title = screen.getByRole('heading', { level: 1 })
    expect(title).toHaveTextContent("Installation de l'application AMI")
  })
})
