import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  History as HistoryIcon,
  Leaf,
  Search,
  Trash2,
  Eye,
  X,
  ScanSearch,
} from 'lucide-react'
import { leafguardApi } from '../api/client.js'
import useFetch from '../hooks/useFetch.js'
import useDebounce from '../hooks/useDebounce.js'
import Alert from '../components/Alert.jsx'
import EmptyState from '../components/EmptyState.jsx'
import Pagination from '../components/Pagination.jsx'
import Spinner from '../components/Spinner.jsx'
import ConfidenceBar from '../components/ConfidenceBar.jsx'
import { formatDate } from '../utils/format.js'

function DetailModal({ record, onClose }) {
  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/60 p-4 animate-fade-in"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
    >
      <div className="card w-full max-w-lg p-6" onClick={(e) => e.stopPropagation()}>
        <div className="flex items-start justify-between gap-4">
          <div>
            <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">{record.plant}</p>
            <h3 className={`text-xl font-bold ${record.is_healthy ? 'text-leaf-700' : 'text-slate-900'}`}>
              {record.disease}
            </h3>
          </div>
          <button onClick={onClose} aria-label="Close details" className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100">
            <X className="h-5 w-5" />
          </button>
        </div>
        {record.thumbnail && (
          <img src={record.thumbnail} alt="Analyzed leaf" className="mx-auto mt-4 max-h-56 rounded-xl border border-slate-100" />
        )}
        <dl className="mt-5 space-y-2.5 text-sm">
          <div className="flex justify-between gap-4">
            <dt className="text-slate-500">Confidence</dt>
            <dd className="font-semibold text-slate-800">{record.confidence.toFixed(2)}%</dd>
          </div>
          <div className="flex justify-between gap-4">
            <dt className="text-slate-500">File</dt>
            <dd className="max-w-[60%] truncate font-medium text-slate-700">{record.image_name}</dd>
          </div>
          <div className="flex justify-between gap-4">
            <dt className="text-slate-500">Processing time</dt>
            <dd className="font-medium text-slate-700">{record.processing_time?.toFixed?.(3)}s</dd>
          </div>
          <div className="flex justify-between gap-4">
            <dt className="text-slate-500">Model</dt>
            <dd className="font-medium text-slate-700">{record.model_name}</dd>
          </div>
          <div className="flex justify-between gap-4">
            <dt className="text-slate-500">Date</dt>
            <dd className="font-medium text-slate-700">{formatDate(record.created_at)}</dd>
          </div>
        </dl>
      </div>
    </div>
  )
}

export default function History() {
  const [search, setSearch] = useState('')
  const [plant, setPlant] = useState('')
  const [status, setStatus] = useState('')
  const [sort, setSort] = useState('newest')
  const [page, setPage] = useState(1)
  const [detail, setDetail] = useState(null)
  const [deletingId, setDeletingId] = useState(null)

  const debouncedSearch = useDebounce(search)
  const params = useMemo(
    () => ({ page, page_size: 8, search: debouncedSearch || undefined, plant: plant || undefined, status: status || undefined, sort }),
    [page, debouncedSearch, plant, status, sort],
  )
  const { data, loading, error, reload } = useFetch(
    () => leafguardApi.listPredictions(params),
    [params],
  )

  const removeRecord = async (id) => {
    if (!window.confirm('Delete this prediction record?')) return
    setDeletingId(id)
    try {
      await leafguardApi.deletePrediction(id)
      await reload(true)
    } finally {
      setDeletingId(null)
    }
  }

  const hasFilters = search || plant || status

  return (
    <div className="mx-auto max-w-6xl px-4 py-10 sm:px-6 sm:py-14">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-slate-900">Prediction History</h1>
          <p className="mt-2 text-slate-500">Every scan is stored with its full result.</p>
        </div>
        <Link to="/predict" className="btn-primary">
          <ScanSearch className="h-4 w-4" /> New Scan
        </Link>
      </div>

      {/* ---- filters ---- */}
      <div className="card mt-8 grid gap-3 p-4 sm:grid-cols-2 lg:grid-cols-4">
        <div className="relative">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
          <input
            className="input !pl-9"
            placeholder="Search plant or disease…"
            value={search}
            onChange={(e) => {
              setSearch(e.target.value)
              setPage(1)
            }}
            aria-label="Search predictions"
          />
        </div>
        <select
          className="input"
          value={plant}
          onChange={(e) => {
            setPlant(e.target.value)
            setPage(1)
          }}
          aria-label="Filter by plant"
        >
          <option value="">All plants</option>
          <option value="Tomato">Tomato</option>
          <option value="Potato">Potato</option>
        </select>
        <select
          className="input"
          value={status}
          onChange={(e) => {
            setStatus(e.target.value)
            setPage(1)
          }}
          aria-label="Filter by status"
        >
          <option value="">Healthy &amp; diseased</option>
          <option value="healthy">Healthy only</option>
          <option value="diseased">Diseased only</option>
        </select>
        <select
          className="input"
          value={sort}
          onChange={(e) => setSort(e.target.value)}
          aria-label="Sort order"
        >
          <option value="newest">Newest first</option>
          <option value="oldest">Oldest first</option>
          <option value="confidence">Highest confidence</option>
        </select>
      </div>

      <div className="mt-6 space-y-4">
        <Alert message={error} onDismiss={() => reload(true)} />

        {loading && (
          <div className="card flex items-center justify-center gap-3 p-12 text-slate-500">
            <Spinner /> <span className="text-sm">Loading history…</span>
          </div>
        )}

        {!loading && !error && data?.items?.length === 0 && (
          <EmptyState
            icon={hasFilters ? HistoryIcon : Leaf}
            title={hasFilters ? 'No matching predictions' : 'No predictions yet'}
            message={
              hasFilters
                ? 'Try adjusting your search or filters.'
                : 'Analyze your first leaf image and it will appear here.'
            }
          >
            <Link to="/predict" className="btn-primary">Analyze a Leaf</Link>
          </EmptyState>
        )}

        {!loading && data?.items?.length > 0 && (
          <>
            {/* table (desktop) */}
            <div className="card hidden overflow-hidden md:block">
              <table className="w-full text-sm" data-testid="history-table">
                <thead>
                  <tr className="border-b border-slate-100 bg-slate-50/80 text-left text-xs uppercase tracking-wider text-slate-400">
                    <th className="px-5 py-3.5 font-semibold">Plant</th>
                    <th className="px-5 py-3.5 font-semibold">Disease</th>
                    <th className="px-5 py-3.5 font-semibold">Confidence</th>
                    <th className="px-5 py-3.5 font-semibold">Date</th>
                    <th className="px-5 py-3.5 text-right font-semibold">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {data.items.map((record) => (
                    <tr key={record.id} className="border-b border-slate-50 transition hover:bg-leaf-50/40">
                      <td className="px-5 py-3.5">
                        <div className="flex items-center gap-3">
                          {record.thumbnail ? (
                            <img src={record.thumbnail} alt="" className="h-10 w-10 rounded-lg object-cover" />
                          ) : (
                            <span className="flex h-10 w-10 items-center justify-center rounded-lg bg-slate-100">
                              <Leaf className="h-4 w-4 text-slate-400" />
                            </span>
                          )}
                          <span className="font-medium text-slate-700">{record.plant}</span>
                        </div>
                      </td>
                      <td className="px-5 py-3.5">
                        <span className={`font-semibold ${record.is_healthy ? 'text-leaf-700' : 'text-slate-800'}`}>
                          {record.disease}
                        </span>
                      </td>
                      <td className="px-5 py-3.5">
                        <ConfidenceBar value={record.confidence} className="max-w-[180px]" />
                      </td>
                      <td className="px-5 py-3.5 whitespace-nowrap text-slate-500">{formatDate(record.created_at)}</td>
                      <td className="px-5 py-3.5">
                        <div className="flex justify-end gap-1.5">
                          <button
                            onClick={() => setDetail(record)}
                            className="rounded-lg p-2 text-slate-500 transition hover:bg-slate-100 hover:text-leaf-700"
                            aria-label={`View details of ${record.disease}`}
                          >
                            <Eye className="h-4 w-4" />
                          </button>
                          <button
                            onClick={() => removeRecord(record.id)}
                            disabled={deletingId === record.id}
                            className="rounded-lg p-2 text-slate-500 transition hover:bg-red-50 hover:text-red-600 disabled:opacity-50"
                            aria-label={`Delete ${record.disease} record`}
                          >
                            <Trash2 className="h-4 w-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* cards (mobile) */}
            <div className="space-y-3 md:hidden">
              {data.items.map((record) => (
                <div key={record.id} className="card flex items-center gap-3 p-4">
                  {record.thumbnail ? (
                    <img src={record.thumbnail} alt="" className="h-12 w-12 rounded-lg object-cover" />
                  ) : (
                    <span className="flex h-12 w-12 items-center justify-center rounded-lg bg-slate-100">
                      <Leaf className="h-5 w-5 text-slate-400" />
                    </span>
                  )}
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-sm font-semibold text-slate-800">{record.disease}</p>
                    <p className="text-xs text-slate-400">
                      {record.plant} · {formatDate(record.created_at)}
                    </p>
                  </div>
                  <button onClick={() => setDetail(record)} aria-label="View details" className="rounded-lg p-2 text-slate-500 hover:bg-slate-100">
                    <Eye className="h-4 w-4" />
                  </button>
                  <button onClick={() => removeRecord(record.id)} aria-label="Delete record" className="rounded-lg p-2 text-slate-500 hover:bg-red-50 hover:text-red-600">
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              ))}
            </div>

            <Pagination
              page={data.pagination.page}
              totalPages={data.pagination.total_pages}
              onChange={setPage}
            />
          </>
        )}
      </div>

      {detail && <DetailModal record={detail} onClose={() => setDetail(null)} />}
    </div>
  )
}
