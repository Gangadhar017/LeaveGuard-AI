import { describe, expect, it } from 'vitest'
import { getApiError } from '../api/client.js'

describe('getApiError', () => {
  it('extracts the backend error message', () => {
    const error = {
      response: {
        status: 422,
        data: { success: false, error: { code: 'INVALID_IMAGE', message: 'Please upload a valid leaf image.' } },
      },
    }
    expect(getApiError(error)).toBe('Please upload a valid leaf image.')
  })

  it('maps network failures to a helpful message', () => {
    expect(getApiError({ request: {} })).toMatch(/Cannot reach the LeafGuard API/)
  })

  it('maps timeouts to a helpful message', () => {
    expect(getApiError({ code: 'ECONNABORTED' })).toMatch(/timed out/i)
  })

  it('falls back to a generic message for unexpected errors', () => {
    expect(getApiError({ response: { status: 500, data: {} } })).toMatch(/Server error \(500\)/)
  })
})
