import { describe, it, expect } from 'vitest'
import {
  formatDate,
  formatConfidence,
  truncate,
  SEVERITY_STYLES,
} from '../utils/format'

describe('format utils', () => {
  describe('formatDate', () => {
    it('returns a dash for falsy or empty values', () => {
      expect(formatDate(null)).toBe('—')
      expect(formatDate(undefined)).toBe('—')
      expect(formatDate('')).toBe('—')
    })

    it('returns a dash for invalid date strings', () => {
      expect(formatDate('not-a-valid-date')).toBe('—')
    })

    it('formats valid ISO dates correctly', () => {
      const formatted = formatDate('2026-09-22T20:00:00Z')
      expect(formatted).not.toBe('—')
      expect(typeof formatted).toBe('string')
      expect(formatted.length).toBeGreaterThan(0)
    })
  })

  describe('formatConfidence', () => {
    it('returns a dash when value is null or undefined', () => {
      expect(formatConfidence(null)).toBe('—')
      expect(formatConfidence(undefined)).toBe('—')
    })

    it('formats numeric values with two decimal places and percentage sign', () => {
      expect(formatConfidence(95.456)).toBe('95.46%')
      expect(formatConfidence(100)).toBe('100.00%')
      expect(formatConfidence(0)).toBe('0.00%')
    })
  })

  describe('truncate', () => {
    it('returns empty string for nullish or empty input', () => {
      expect(truncate(null)).toBe('')
      expect(truncate(undefined)).toBe('')
      expect(truncate('')).toBe('')
    })

    it('preserves text shorter than or equal to the limit', () => {
      expect(truncate('Short text', 20)).toBe('Short text')
    })

    it('truncates text exceeding the limit and appends an ellipsis', () => {
      const longText = 'This is a long sentence that should definitely be truncated.'
      const truncated = truncate(longText, 15)
      expect(truncated.endsWith('…')).toBe(true)
      expect(truncated.length).toBe(15)
    })
  })

  describe('SEVERITY_STYLES', () => {
    it('defines styles for standard severity tiers', () => {
      expect(SEVERITY_STYLES).toHaveProperty('healthy')
      expect(SEVERITY_STYLES).toHaveProperty('low')
      expect(SEVERITY_STYLES).toHaveProperty('medium')
      expect(SEVERITY_STYLES).toHaveProperty('high')
      expect(SEVERITY_STYLES).toHaveProperty('critical')
      expect(SEVERITY_STYLES).toHaveProperty('unknown')
    })
  })
})
