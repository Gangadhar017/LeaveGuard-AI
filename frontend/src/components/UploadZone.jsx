import { useCallback, useRef, useState } from 'react'
import { ImagePlus, UploadCloud, X } from 'lucide-react'

const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/webp']
const MAX_SIZE_MB = 10

export default function UploadZone({ file, onFileSelected, disabled }) {
  const inputRef = useRef(null)
  const [dragging, setDragging] = useState(false)
  const [localError, setLocalError] = useState(null)

  const accept = useCallback(
    (candidate) => {
      setLocalError(null)
      if (!candidate) return
      if (!ALLOWED_TYPES.includes(candidate.type)) {
        setLocalError('Unsupported format. Please use a JPG, PNG or WEBP image.')
        return
      }
      if (candidate.size > MAX_SIZE_MB * 1024 * 1024) {
        setLocalError(`Image is too large. Maximum size is ${MAX_SIZE_MB} MB.`)
        return
      }
      onFileSelected(candidate)
    },
    [onFileSelected],
  )

  const onDrop = (event) => {
    event.preventDefault()
    setDragging(false)
    if (!disabled) accept(event.dataTransfer.files?.[0])
  }

  const previewUrl = file ? URL.createObjectURL(file) : null

  return (
    <div>
      <input
        ref={inputRef}
        type="file"
        accept="image/jpeg,image/png,image/webp"
        className="hidden"
        onChange={(e) => {
          accept(e.target.files?.[0])
          e.target.value = ''
        }}
      />

      {!file ? (
        <button
          type="button"
          disabled={disabled}
          onClick={() => inputRef.current?.click()}
          onDragOver={(e) => {
            e.preventDefault()
            setDragging(true)
          }}
          onDragLeave={() => setDragging(false)}
          onDrop={onDrop}
          className={`flex w-full flex-col items-center justify-center gap-4 rounded-2xl border-2 border-dashed px-6 py-14 text-center transition ${
            dragging
              ? 'border-leaf-500 bg-leaf-50'
              : 'border-slate-300 bg-slate-50/60 hover:border-leaf-400 hover:bg-leaf-50/50'
          } ${disabled ? 'cursor-not-allowed opacity-60' : 'cursor-pointer'}`}
          data-testid="upload-zone"
        >
          <span className="flex h-16 w-16 items-center justify-center rounded-2xl bg-leaf-100">
            <UploadCloud className="h-8 w-8 text-leaf-600" />
          </span>
          <span>
            <span className="block text-base font-semibold text-slate-800">
              Drag &amp; drop a leaf image here
            </span>
            <span className="mt-1 block text-sm text-slate-500">
              or click to browse — JPG, PNG or WEBP, up to {MAX_SIZE_MB} MB
            </span>
          </span>
          <span className="btn-primary mt-1">Select an Image</span>
        </button>
      ) : (
        <div className="card overflow-hidden animate-fade-in" data-testid="preview-card">
          <div className="relative mx-auto max-w-md">
            <img
              src={previewUrl}
              alt={`Preview of ${file.name}`}
              className="max-h-80 w-full object-contain bg-slate-50"
            />
            <button
              type="button"
              onClick={() => {
                onFileSelected(null)
                setLocalError(null)
              }}
              disabled={disabled}
              aria-label="Remove selected image"
              className="absolute right-3 top-3 rounded-full bg-white/95 p-2 shadow-md transition hover:bg-white disabled:opacity-50"
            >
              <X className="h-4 w-4 text-slate-600" />
            </button>
          </div>
          <div className="flex items-center gap-3 border-t border-slate-100 px-5 py-3.5">
            <ImagePlus className="h-4 w-4 shrink-0 text-leaf-600" />
            <p className="truncate text-sm font-medium text-slate-700">{file.name}</p>
            <p className="ml-auto shrink-0 text-xs text-slate-400">
              {(file.size / 1024).toFixed(0)} KB
            </p>
          </div>
        </div>
      )}

      {localError && (
        <p role="alert" className="mt-3 rounded-xl bg-red-50 px-4 py-3 text-sm text-red-700">
          {localError}
        </p>
      )}
    </div>
  )
}
