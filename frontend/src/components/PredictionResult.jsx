import {
  Activity,
  CheckCircle2,
  Clock,
  Leaf,
  ShieldAlert,
  Sprout,
  Stethoscope,
  XCircle,
} from 'lucide-react'
import ConfidenceBar from './ConfidenceBar.jsx'
import { SEVERITY_STYLES, formatConfidence } from '../utils/format.js'

function InfoList({ title, icon: Icon, items, tone }) {
  if (!items?.length) return null
  return (
    <div>
      <h4 className="flex items-center gap-2 text-sm font-semibold text-slate-800">
        <Icon className={`h-4 w-4 ${tone}`} /> {title}
      </h4>
      <ul className="mt-2 space-y-1.5">
        {items.map((item, index) => (
          <li key={index} className="flex gap-2 text-sm leading-relaxed text-slate-600">
            <span className={`mt-[7px] h-1.5 w-1.5 shrink-0 rounded-full ${tone.replace('text-', 'bg-')}`} />
            {item}
          </li>
        ))}
      </ul>
    </div>
  )
}

export default function PredictionResult({ result, imageUrl, onAnalyzeAnother }) {
  const { prediction, recommendation } = result
  const severityStyle = SEVERITY_STYLES[recommendation.severity] || SEVERITY_STYLES.unknown

  return (
    <div className="space-y-6 animate-fade-in-up" data-testid="prediction-result">
      {/* ---- verdict card ---- */}
      <div className="card overflow-hidden">
        <div className="grid gap-6 p-6 sm:grid-cols-[220px_1fr] sm:p-8">
          <img
            src={imageUrl}
            alt="Analyzed leaf"
            className="h-52 w-full rounded-xl border border-slate-200 bg-slate-50 object-cover sm:h-full"
          />
          <div className="flex flex-col justify-center gap-4">
            <div className="flex flex-wrap items-center gap-2">
              <span className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-semibold ring-1 ${severityStyle}`}>
                {prediction.is_healthy ? (
                  <CheckCircle2 className="h-3.5 w-3.5" />
                ) : (
                  <ShieldAlert className="h-3.5 w-3.5" />
                )}
                {prediction.is_healthy ? 'Healthy' : `${recommendation.severity} severity`}
              </span>
              <span className="inline-flex items-center gap-1.5 rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600">
                <Clock className="h-3.5 w-3.5" />
                {prediction.processing_time?.toFixed?.(2) ?? prediction.processing_time}s
              </span>
              <span className="inline-flex items-center gap-1.5 rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600">
                <Activity className="h-3.5 w-3.5" />
                {prediction.model_name}
              </span>
            </div>

            <div>
              <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">Plant</p>
              <p className="mt-0.5 text-lg font-semibold text-slate-700">{prediction.plant}</p>
            </div>

            <div>
              <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                Detected condition
              </p>
              <h3
                className={`mt-0.5 text-2xl font-bold sm:text-3xl ${
                  prediction.is_healthy ? 'text-leaf-700' : 'text-slate-900'
                }`}
              >
                {prediction.disease}
              </h3>
            </div>

            <div>
              <p className="mb-1.5 text-xs font-semibold uppercase tracking-wider text-slate-400">
                Model confidence
              </p>
              <ConfidenceBar value={prediction.confidence} />
            </div>
          </div>
        </div>

        {prediction.top_predictions?.length > 1 && (
          <div className="border-t border-slate-100 bg-slate-50/70 px-6 py-4 sm:px-8">
            <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">
              Top predictions
            </p>
            <div className="mt-2 flex flex-wrap gap-x-8 gap-y-2">
              {prediction.top_predictions.map((tp) => (
                <div key={tp.label} className="flex items-center gap-2 text-sm">
                  <span className={tp.label === prediction.disease ? 'font-semibold text-leaf-700' : 'text-slate-500'}>
                    {tp.label}
                  </span>
                  <span className="tabular-nums text-slate-400">{formatConfidence(tp.confidence)}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* ---- agronomic info ---- */}
      <div className="card p-6 sm:p-8">
        <div className="flex items-start gap-3">
          <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-leaf-100">
            <Sprout className="h-5 w-5 text-leaf-700" />
          </span>
          <div>
            <h4 className="font-semibold text-slate-900">What is this?</h4>
            <p className="mt-1 text-sm leading-relaxed text-slate-600">
              {recommendation.description}
            </p>
          </div>
        </div>

        <div className="mt-6 grid gap-6 md:grid-cols-3">
          <InfoList title="Symptoms" icon={Stethoscope} items={recommendation.symptoms} tone="text-amber-600" />
          <InfoList title="Prevention" icon={Leaf} items={recommendation.prevention} tone="text-leaf-600" />
          <InfoList title="Treatment" icon={XCircle} items={recommendation.treatment} tone="text-red-500" />
        </div>
      </div>

      <div className="flex justify-center">
        <button type="button" onClick={onAnalyzeAnother} className="btn-primary">
          Analyze Another Image
        </button>
      </div>
    </div>
  )
}
