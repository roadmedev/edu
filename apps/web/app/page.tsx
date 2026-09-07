'use client'

import { useEffect, useState } from 'react'

export default function Home() {
  const [message, setMessage] = useState<string>('Yuklanmoqda...')
  const [loading, setLoading] = useState<boolean>(true)

  useEffect(() => {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8787'

    fetch(`${apiUrl}/api/hello`)
      .then((res) => res.json())
      .then((data) => {
        setMessage(data.message || data.error)
        setLoading(false)
      })
      .catch((err) => {
        setMessage('Backend bilan ulanishda xatolik!')
        setLoading(false)
      })
  }, [])

  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-slate-900 text-white p-6">
      <div className="bg-slate-800 border border-slate-700 p-8 rounded-xl shadow-2xl text-center max-w-md w-full">
        <h1 className="text-xl font-medium text-slate-400 mb-2">Neon.tech DB Result:</h1>
        <div className="text-3xl font-bold text-emerald-400 min-h-[40px] flex items-center justify-center">
          {loading ? (
            <span className="animate-pulse text-slate-500">Kutilmoqda...</span>
          ) : (
            message
          )}
        </div>
      </div>
    </main>
  )
}