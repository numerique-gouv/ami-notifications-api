import { describe, expect, test } from 'vitest'
import '@testing-library/jest-dom/vitest'
import { prettyDate } from './prettyDate'

describe('prettyDate', () => {
  test('should properly format seconds', async () => {
    // Given
    const now = new Date()
    const seconds = 7
    const before = new Date(now.getTime() - seconds * 1000)
    // When
    const pretty = prettyDate(before)
    const pretty2 = prettyDate(before.toJSON())

    // Then
    expect(pretty).equal('< 1h')
    expect(pretty2).equal('< 1h')
  })
  test('should properly format minutes', async () => {
    // Given
    const now = new Date()
    const minutes = 7
    const before = new Date(now.getTime() - minutes * 60 * 1000)
    // When
    const pretty = prettyDate(before)
    const pretty2 = prettyDate(before.toJSON())

    // Then
    expect(pretty).equal('< 1h')
    expect(pretty2).equal('< 1h')
  })
  test('should properly format hours', async () => {
    // Given
    const now = new Date()
    const hours = 7
    const before = new Date(now.getTime() - hours * 60 * 60 * 1000)
    // When
    const pretty = prettyDate(before)
    const pretty2 = prettyDate(before.toJSON())

    // Then
    expect(pretty).equal('7h')
    expect(pretty2).equal('7h')
  })
  test('should properly format days', async () => {
    // Given
    const now = new Date()
    const days = 7
    const before = new Date(now.getTime() - days * 24 * 60 * 60 * 1000)
    // When
    const pretty = prettyDate(before)
    const pretty2 = prettyDate(before.toJSON())

    // Then
    expect(pretty).equal('7j')
    expect(pretty2).equal('7j')
  })
  test('should properly format months', async () => {
    // Given
    const now = new Date()
    const months = 7
    const before = new Date(now.getTime() - months * 31 * 24 * 60 * 60 * 1000)
    // When
    const pretty = prettyDate(before)
    const pretty2 = prettyDate(before.toJSON())

    // Then
    expect(pretty).equal('7m')
    expect(pretty2).equal('7m')
  })
  test('should properly format years', async () => {
    // Given
    const now = new Date()
    const years = 7
    const before = new Date(now.getTime() - years * 365 * 24 * 60 * 60 * 1000)
    // When
    const pretty = prettyDate(before)
    const pretty2 = prettyDate(before.toJSON())

    // Then
    expect(pretty).equal('7a')
    expect(pretty2).equal('7a')
  })
})
