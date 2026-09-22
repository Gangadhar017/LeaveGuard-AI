import { useRef, useState } from 'react'
import { ScanSearch } from 'lucide-react'
import UploadZone from '../components/UploadZone.jsx'
import PredictionResult from '../components/PredictionResult.jsx'
import Alert from '../components/Alert.jsx'
import Spinner from '../components/Spinner.jsx'
import { getApiError, leafguardApi } from '../api/client.js'

export default function Predict() {
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [error, setError] = useState(null)
  const [result, setResult] = useState(null)
  const resultRef = useRef(null)

  const analyze = async () => {
    if (!file) return
    setLoading(true)
    setError(null)
    setResult(null)
    setProgress(0)
    try {
      const response = await leafguardApi.predict(file, (event) => {
        if (event.total) setProgress(Math.round((event.loaded / event.total) * 100))
      })
      setResult(response.data)
      setTimeout(() => resultRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' }), 60)
    } catch (err) {
      setError(getApiError(err))
    } finally {
      setLoading(false)
    }
  }

  const reset = () => {
    setFile(null)
    setResult(null)
    setError(null)
  }

  return (
    <div className="mx-auto max-w-4xl px-4 py-10 sm:px-6 sm:py-14">
      <div className="text-center">
        <h1 className="text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">Leaf Analysis</h1>
        <p className="mt-2 text-slate-500">
          Upload a clear photo of a tomato or potato leaf to detect diseases.
        </p>
      </div>

      <div className="mt-8 space-y-6">
        <div className="card p-5 sm:p-7">
          <UploadZone file={file} onFileSelected={setFile} disabled={loading} />

          {file && !result && (
            <div className="mt-5 flex flex-col items-center gap-3">
              <button
                type="button"
                onClick={analyze}
                disabled={loading}
                className="btn-primary !px-8 !py-3 !text-base"
                data-testid="analyze-button"
              >
                {loading ? <Spinner className="h-5 w-5 !text-white" /> : <ScanSearch className="h-5 w-5" />}
                {loading ? `Analyzing… ${progress}%` : 'Analyze Leaf'}
              </button>
              {loading && (
                <div className="h-1.5 w-56 overflow-hidden rounded-full bg-slate-200">
                  <div
                    className="h-full rounded-full bg-leaf-600 transition-[width] duration-300"
                    style={{ width: `${Math.max(progress, 8)}%` }}
                  />
                </div>
              )}
            </div>
          )}
        </div>

        <Alert title="Prediction failed" message={error} onDismiss={() => setError(null)} />

        {loading && (
          <div className="card flex items-center gap-4 p-6" data-testid="loading-state">
            <Spinner />
            <div>
              <p className="text-sm font-semibold text-slate-800">Running the analysis…</p>
              <p className="text-sm text-slate-500">
                Preprocessing the image and running the classifier — usually under a second.
              </p>
            </div>
          </div>
        )}

        <div ref={resultRef}>
          {result && (
            <PredictionResult
              result={result}
              imageUrl={URL.createObjectURL(file)}
              onAnalyzeAnother={reset}
            />
          )}
        </div>
      </div>
    </div>
  )
}
