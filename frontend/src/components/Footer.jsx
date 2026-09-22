import { Leaf, Github } from 'lucide-react'
import { API_BASE_URL } from '../api/client.js'

export default function Footer() {
  return (
    <footer className="border-t border-slate-200 bg-white">
      <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-3 px-4 py-6 text-sm text-slate-500 sm:flex-row sm:px-6">
        <div className="flex items-center gap-2">
          <Leaf className="h-4 w-4 text-leaf-600" />
          <span>
            <strong className="text-slate-700">LeafGuard AI</strong> — Plant Disease Detection &
            Classification
          </span>
        </div>
        <div className="flex items-center gap-4">
          <a
            href={`${API_BASE_URL}/docs`}
            target="_blank"
            rel="noreferrer"
            className="hover:text-leaf-700"
          >
            API Docs
          </a>
          <a
            href="https://github.com/spMohanty/PlantVillage-Dataset"
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-1.5 hover:text-leaf-700"
          >
            <Github className="h-4 w-4" />
            Dataset
          </a>
        </div>
      </div>
    </footer>
  )
}
