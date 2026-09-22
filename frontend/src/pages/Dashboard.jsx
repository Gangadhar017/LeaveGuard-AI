import {
  BarChart3,
  CheckCircle2,
  Gauge,
  Leaf,
  ShieldAlert,
  Sprout,
} from 'lucide-react'
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { leafguardApi } from '../api/client.js'
import useFetch from '../hooks/useFetch.js'
import Alert from '../components/Alert.jsx'
import EmptyState from '../components/EmptyState.jsx'
import Spinner from '../components/Spinner.jsx'
import StatCard from '../components/StatCard.jsx'
import { formatConfidence } from '../utils/format.js'

const PIE_COLORS = ['#16a34a', '#e11d48']

export default function Dashboard() {
  const { data: stats, loading, error } = useFetch(() => leafguardApi.stats())

  if (loading) {
    return (
      <div className="mx-auto flex max-w-6xl items-center justify-center gap-3 px-4 py-24 text-slate-500">
        <Spinner /> <span className="text-sm">Loading dashboard…</span>
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-6xl px-4 py-10 sm:px-6 sm:py-14">
      <h1 className="text-3xl font-bold tracking-tight text-slate-900">Dashboard</h1>
      <p className="mt-2 text-slate-500">Live statistics across every leaf analyzed by this instance.</p>

      <div className="mt-8 space-y-6">
        <Alert message={error} />

        {!error && stats && stats.total_predictions === 0 && (
          <EmptyState
            icon={Sprout}
            title="No data yet"
            message="Statistics appear here as soon as the first leaf has been analyzed through the API."
          >
            <a href="/predict" className="btn-primary">Analyze a Leaf</a>
          </EmptyState>
        )}

        {!error && stats && stats.total_predictions > 0 && (
          <>
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              <StatCard icon={Leaf} label="Total Predictions" value={stats.total_predictions} />
              <StatCard
                icon={CheckCircle2}
                label="Healthy Leaves"
                value={stats.healthy_count}
                tone="text-leaf-600"
              />
              <StatCard
                icon={ShieldAlert}
                label="Diseased Leaves"
                value={stats.diseased_count}
                tone="text-red-500"
              />
              <StatCard
                icon={Gauge}
                label="Avg. Confidence"
                value={formatConfidence(stats.average_confidence)}
                tone="text-sky-600"
              />
            </div>

            {stats.most_detected_disease && (
              <div className="card flex items-center gap-4 border-l-4 !border-l-leaf-600 p-5">
                <span className="flex h-11 w-11 items-center justify-center rounded-xl bg-leaf-100">
                  <BarChart3 className="h-5 w-5 text-leaf-700" />
                </span>
                <div>
                  <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                    Most detected disease
                  </p>
                  <p className="text-lg font-bold text-slate-900">
                    {stats.most_detected_disease.disease}
                    <span className="ml-2 text-sm font-medium text-slate-400">
                      ({stats.most_detected_disease.count} detections)
                    </span>
                  </p>
                </div>
              </div>
            )}

            <div className="grid gap-6 lg:grid-cols-2">
              <div className="card p-5">
                <h3 className="font-semibold text-slate-900">Healthy vs diseased</h3>
                <div className="mt-4 h-64" data-testid="health-pie">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={[
                          { name: 'Healthy', value: stats.healthy_count },
                          { name: 'Diseased', value: stats.diseased_count },
                        ]}
                        dataKey="value"
                        innerRadius={55}
                        outerRadius={85}
                        paddingAngle={3}
                      >
                        {PIE_COLORS.map((color) => (
                          <Cell key={color} fill={color} />
                        ))}
                      </Pie>
                      <Tooltip />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              </div>

              <div className="card p-5">
                <h3 className="font-semibold text-slate-900">Top detected diseases</h3>
                <div className="mt-4 h-64" data-testid="disease-bar">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={stats.top_diseases} layout="vertical" margin={{ left: 8, right: 16 }}>
                      <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                      <XAxis type="number" allowDecimals={false} fontSize={12} />
                      <YAxis
                        type="category"
                        dataKey="name"
                        width={150}
                        fontSize={11}
                        tickFormatter={(v) => (v.length > 22 ? `${v.slice(0, 21)}…` : v)}
                      />
                      <Tooltip />
                      <Bar dataKey="count" fill="#16a34a" radius={[0, 6, 6, 0]} barSize={18} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              <div className="card p-5 lg:col-span-2">
                <h3 className="font-semibold text-slate-900">Predictions by plant</h3>
                <div className="mt-4 h-56">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={stats.by_plant} margin={{ left: -16, right: 16 }}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} />
                      <XAxis dataKey="name" fontSize={12} />
                      <YAxis allowDecimals={false} fontSize={12} />
                      <Tooltip />
                      <Bar dataKey="count" fill="#0d9488" radius={[6, 6, 0, 0]} barSize={48} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  )
}
