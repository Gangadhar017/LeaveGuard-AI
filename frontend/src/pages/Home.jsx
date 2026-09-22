import { Link } from 'react-router-dom'
import {
  ArrowRight,
  BarChart3,
  BookOpenCheck,
  Camera,
  FileSearch,
  ScanSearch,
  Sprout,
  Upload,
} from 'lucide-react'

const FEATURES = [
  {
    icon: ScanSearch,
    title: 'AI Disease Detection',
    text: 'A computer-vision pipeline analyzes leaf color, texture and lesion patterns to identify diseases across tomato and potato crops.',
  },
  {
    icon: Camera,
    title: 'Instant Results',
    text: 'Upload a photo and get a prediction with a confidence score in under a second — no lab equipment required.',
  },
  {
    icon: BookOpenCheck,
    title: 'Actionable Guidance',
    text: 'Every result comes with symptoms, prevention tips and treatment recommendations curated from agronomic sources.',
  },
  {
    icon: BarChart3,
    title: 'History & Insights',
    text: 'All scans are stored so you can review past predictions and track detection statistics on the dashboard.',
  },
]

const STEPS = [
  {
    icon: Upload,
    title: '1. Upload a leaf photo',
    text: 'Drag & drop or browse for a clear photo of the affected leaf.',
  },
  {
    icon: ScanSearch,
    title: '2. AI analyzes the image',
    text: 'The image is preprocessed with OpenCV and classified by a trained scikit-learn model.',
  },
  {
    icon: FileSearch,
    title: '3. Get the diagnosis',
    text: 'See the predicted disease, confidence level and what to do about it.',
  },
]

export default function Home() {
  return (
    <div className="animate-fade-in">
      {/* ---- hero ---- */}
      <section className="relative overflow-hidden bg-slate-950">
        <div
          className="pointer-events-none absolute inset-0 opacity-40"
          style={{
            background:
              'radial-gradient(600px 300px at 80% 20%, rgba(22,163,74,0.35), transparent), radial-gradient(500px 260px at 10% 90%, rgba(20,184,166,0.25), transparent)',
          }}
        />
        <div className="relative mx-auto max-w-6xl px-4 py-24 text-center sm:px-6 sm:py-32">
          <span className="inline-flex items-center gap-2 rounded-full border border-leaf-500/30 bg-leaf-500/10 px-4 py-1.5 text-xs font-semibold text-leaf-300">
            <Sprout className="h-3.5 w-3.5" />
            Computer vision for plant health
          </span>
          <h1 className="mx-auto mt-6 max-w-3xl text-4xl font-extrabold tracking-tight text-white sm:text-6xl">
            Protect your crops with
            <span className="bg-gradient-to-r from-leaf-400 to-emerald-300 bg-clip-text text-transparent"> AI-powered leaf diagnosis</span>
          </h1>
          <p className="mx-auto mt-6 max-w-2xl text-lg leading-relaxed text-slate-300">
            Upload a photo of a plant leaf and LeafGuard AI detects the disease, shows its
            confidence and tells you how to fight back — instantly.
          </p>
          <div className="mt-10 flex flex-wrap items-center justify-center gap-4">
            <Link to="/predict" className="btn-primary !px-7 !py-3 !text-base">
              Scan a Leaf <ArrowRight className="h-4 w-4" />
            </Link>
            <Link
              to="/about"
              className="inline-flex items-center justify-center gap-2 rounded-xl border border-slate-700 bg-slate-900/60 px-7 py-3 text-base font-semibold text-slate-200 transition hover:bg-slate-800"
            >
              How it works
            </Link>
          </div>
        </div>
      </section>

      {/* ---- features ---- */}
      <section className="mx-auto max-w-6xl px-4 py-20 sm:px-6">
        <div className="text-center">
          <h2 className="text-3xl font-bold tracking-tight text-slate-900">
            Everything a farmer needs, nothing they don't
          </h2>
          <p className="mx-auto mt-3 max-w-2xl text-slate-500">
            Built as an end-to-end ML product: image pipeline, trained model, REST API and a
            modern web dashboard.
          </p>
        </div>
        <div className="mt-12 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {FEATURES.map((feature) => (
            <div key={feature.title} className="card group p-6 transition hover:-translate-y-1 hover:shadow-md">
              <span className="flex h-11 w-11 items-center justify-center rounded-xl bg-leaf-100 transition group-hover:bg-leaf-600">
                <feature.icon className="h-5 w-5 text-leaf-700 transition group-hover:text-white" />
              </span>
              <h3 className="mt-4 font-semibold text-slate-900">{feature.title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-slate-500">{feature.text}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ---- how it works ---- */}
      <section className="border-y border-slate-200 bg-white">
        <div className="mx-auto max-w-6xl px-4 py-20 sm:px-6">
          <div className="text-center">
            <h2 className="text-3xl font-bold tracking-tight text-slate-900">Three simple steps</h2>
          </div>
          <div className="mt-12 grid gap-8 md:grid-cols-3">
            {STEPS.map((step) => (
              <div key={step.title} className="relative rounded-2xl border border-slate-200 bg-slate-50/60 p-6">
                <span className="flex h-11 w-11 items-center justify-center rounded-xl bg-leaf-600 text-white shadow-sm">
                  <step.icon className="h-5 w-5" />
                </span>
                <h3 className="mt-4 font-semibold text-slate-900">{step.title}</h3>
                <p className="mt-2 text-sm leading-relaxed text-slate-500">{step.text}</p>
              </div>
            ))}
          </div>
          <div className="mt-12 text-center">
            <Link to="/predict" className="btn-primary !px-7 !py-3 !text-base">
              Try it now <ArrowRight className="h-4 w-4" />
            </Link>
          </div>
        </div>
      </section>
    </div>
  )
}
