import { describe, expect, it, vi } from 'vitest'
import { fireEvent, render, screen } from '@testing-library/react'
import UploadZone from '../components/UploadZone.jsx'

function renderZone(props = {}) {
  const onFileSelected = vi.fn()
  render(<UploadZone file={null} onFileSelected={onFileSelected} {...props} />)
  return onFileSelected
}

describe('UploadZone', () => {
  it('accepts a valid image file', () => {
    const onFileSelected = renderZone()
    const input = document.querySelector('input[type="file"]')
    const file = new File(['bytes'], 'leaf.jpg', { type: 'image/jpeg' })

    fireEvent.change(input, { target: { files: [file] } })

    expect(onFileSelected).toHaveBeenCalledWith(file)
  })

  it('rejects unsupported file types with a visible error', () => {
    const onFileSelected = renderZone()
    const input = document.querySelector('input[type="file"]')
    const file = new File(['bytes'], 'payload.pdf', { type: 'application/pdf' })

    fireEvent.change(input, { target: { files: [file] } })

    expect(onFileSelected).not.toHaveBeenCalled()
    expect(screen.getByRole('alert')).toHaveTextContent(/Unsupported format/i)
  })

  it('rejects oversized images', () => {
    const onFileSelected = renderZone()
    const input = document.querySelector('input[type="file"]')
    const file = new File(['x'.repeat(64)], 'huge.png', { type: 'image/png' })
    Object.defineProperty(file, 'size', { value: 11 * 1024 * 1024 })

    fireEvent.change(input, { target: { files: [file] } })

    expect(onFileSelected).not.toHaveBeenCalled()
    expect(screen.getByRole('alert')).toHaveTextContent(/too large/i)
  })
})
