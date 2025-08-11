'use client'
import { useState } from 'react'

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000'

export default function Home() {
  const [kenteken, setKenteken] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<any>(null)

  async function onSearch(e: React.FormEvent) {
    e.preventDefault()
    if (!kenteken) return
    setLoading(true)
    setResult(null)
    try {
      const r = await fetch(`${API_BASE}/search?kenteken=${encodeURIComponent(kenteken)}`)
      const data = await r.json()
      setResult(data)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-6">
      <div className="w-full max-w-xl bg-white shadow-lg rounded-2xl p-6">
        <h1 className="text-2xl font-semibold mb-2">Kenteken Zoeker</h1>
        <p className="text-gray-600 mb-6">Zoek openbaar op kenteken. Alleen niet-gevoelige velden worden getoond.</p>
        <form onSubmit={onSearch} className="flex gap-2 mb-6">
          <input
            type="text"
            value={kenteken}
            onChange={(e) => setKenteken(e.target.value)}
            placeholder="Voer kenteken in (bijv. G-123-AB)"
            className="flex-1 border rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-black/10"
          />
          <button
            type="submit"
            className="px-5 py-3 rounded-xl bg-black text-white disabled:opacity-50"
            disabled={loading}
          >
            {loading ? 'Zoeken…' : 'Zoek'}
          </button>
        </form>

        {result && (
          <div className="mt-4">
            {!result.found ? (
              <div className="text-sm text-gray-600">Geen resultaat gevonden.</div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <Field label="Kenteken" value={result.data.kenteken} />
                <Field label="Bandenmaat" value={result.data.bandenmaat} />
                <Field label="Meldcode" value={result.data.meldcode} />
                <Field label="Leasemaatschappij" value={result.data.leasemaatschappij} />
                <Field label="WIBA-status" value={result.data.wiba_status} />
                <Field label="Laatst bijgewerkt" value={new Date(result.data.last_seen_at).toLocaleString()} />
              </div>
            )}
          </div>
        )}

        <div className="mt-8 p-4 bg-gray-100 rounded-xl text-sm text-gray-700">
          <p className="font-medium mb-2">Upload (alleen intern)</p>
          <p>Gebruik de <code>POST /upload</code> endpoint van de API met een Excelbestand (.xlsx/.xls). Voorbeeld met <code>curl</code>:</p>
          <pre className="mt-2 overflow-auto text-xs bg-white p-3 rounded-lg border">curl -X POST -H "X-Upload-Token: YOUR_TOKEN" -F "file=@data.xlsx" -F "source_name=Import" {API_BASE}/upload</pre>
        </div>
      </div>
    </div>
  )
}

function Field({label, value}:{label:string, value:any}){
  return (
    <div className="border rounded-xl p-3">
      <div className="text-xs uppercase tracking-wide text-gray-500">{label}</div>
      <div className="mt-1 text-sm">{value ?? '—'}</div>
    </div>
  )
}