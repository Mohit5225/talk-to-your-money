'use client'

import { useMemo, useState } from 'react'
import Link from 'next/link'
import Image from 'next/image'

interface PredictionResult {
  symbol: string;
  high: number;
  low: number;
  close: number;
  date?: string;
}

interface Stock {
  symbol: string;
  name: string;
  logo: string;
  color: string;
}

// Stock Prediction Page
export default function StockPredictions() {
  const [loading, setLoading] = useState(false)
  const [prediction, setPrediction] = useState<PredictionResult | null>(null)
  const [error, setError] = useState('')
  const [targetDate, setTargetDate] = useState('')
  
  const stocks: Stock[] = [
    {
      symbol: 'AAPL',
      name: 'Apple Inc.',
      logo: 'https://logo.clearbit.com/apple.com',
      color: 'bg-gradient-to-r from-[#110f24] via-[#191238] to-[#25175a]'
    },
    {
      symbol: 'MSFT',
      name: 'Microsoft Corporation',
      logo: 'https://logo.clearbit.com/microsoft.com',
      color: 'bg-gradient-to-r from-[#121028] via-[#1c1a43] to-[#2b1f5a]'
    },
    {
      symbol: 'NVDA',
      name: 'NVIDIA Corporation',
      logo: 'https://logo.clearbit.com/nvidia.com',
      color: 'bg-gradient-to-r from-[#0f1628] via-[#1a2748] to-[#243664]'
    },
    {
      symbol: 'GOOGL',
      name: 'Alphabet Inc.',
      logo: 'https://logo.clearbit.com/google.com',
      color: 'bg-gradient-to-r from-[#11152a] via-[#202358] to-[#2d3174]'
    },
    {
      symbol: 'AMD',
      name: 'Advanced Micro Devices Inc.',
      logo: 'https://logo.clearbit.com/amd.com',
      color: 'bg-gradient-to-r from-[#12162d] via-[#222456] to-[#303072]'
    },
    {
      symbol: 'META',
      name: 'Meta Platforms Inc.',
      logo: 'https://logo.clearbit.com/meta.com',
      color: 'bg-gradient-to-r from-[#10162b] via-[#262b5a] to-[#333874]'
    }
  ];

  const normalizedDate = useMemo(() => targetDate.trim(), [targetDate])

  const handlePredictionRequest = async (symbol: string, requestedDate?: string) => {
    setLoading(true)
    setPrediction(null)
    setError('')
    
    try {
      const dateToUse = (requestedDate ?? normalizedDate)
      const url = new URL(`http://localhost:8000/predict/${symbol}`)
      if (dateToUse) {
        url.searchParams.set('date', dateToUse)
      }

      // Make API call to your backend
      const response = await fetch(url.toString(), {
        method: 'GET',  // Changed to GET for compatibility
        headers: {
          'Content-Type': 'application/json'
        }
      })
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Failed to fetch prediction' }));
        throw new Error(errorData.detail || 'Failed to fetch prediction');
      }
      
      const data = await response.json()
      setPrediction(data)
    } catch (err) {
      console.error('Error fetching prediction:', err)
      setError(err instanceof Error ? err.message : 'Failed to get prediction. Please try again.')
    } finally {
      setLoading(false)
    }
  }
  
  return (
    <div className="p-8 text-[var(--foreground)]">
      <div className="mb-6">
        <Link href="/dashboard" className="text-[var(--accent)] hover:text-[#ff5c8f] transition-colors flex items-center">
          ← Back to Dashboard
        </Link>                                                                                                                                                                         
      </div>
      
      <h1 className="text-3xl font-bold mb-6 text-[#f1eeff] drop-shadow-[0_0_18px_rgba(123,91,255,0.28)]">Stock Predictions</h1>
      
  <div className="mb-8 bg-gradient-to-br from-[#0b0a1d] to-[#141238] border border-[#221f46] rounded-xl p-6 shadow-[0_0_30px_rgba(64,55,255,0.22)] backdrop-blur">
        <h2 className="text-xl font-semibold mb-3 text-[var(--accent-secondary)]">Choose a prediction date</h2>
        <p className="text-sm text-[#c8cdfd] mb-4">Pick a target date for your forecast. Leave it empty to use today.</p>
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
          <label htmlFor="target-date" className="text-sm font-medium text-[#e6e9ff]/80">Prediction date</label>
          <input
            id="target-date"
            type="date"
            value={targetDate}
            onChange={(event) => setTargetDate(event.target.value)}
            className="bg-[#121531]/70 border border-[var(--accent)]/35 rounded-md px-3 py-2 text-[var(--foreground)] placeholder-[#c8cdfd]/60 focus:outline-none focus:ring-2 focus:ring-[var(--accent)] focus:border-transparent transition-colors"
          />
        </div>
        <p className="text-xs text-[#c8cdfd] mt-3">Now pick a stock card below to fetch the prediction for that day.</p>
      </div>

      <div className="mb-8">
        <h2 className="text-xl font-semibold mb-4 text-[var(--accent-secondary)]">Select a Stock</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {stocks.map((stock) => (
            <div 
              key={stock.symbol}
              className={`${stock.color} p-6 rounded-xl shadow-[0_0_26px_rgba(64,55,255,0.24)] cursor-pointer transform transition-transform hover:scale-105 hover:shadow-[0_0_38px_rgba(64,55,255,0.32)] border border-[var(--accent-secondary)]/25`}
              onClick={() => handlePredictionRequest(stock.symbol)}
            >
              <div className="flex items-center mb-4">
                {stock.logo && (
                  <Image
                    src={stock.logo}
                    alt={stock.name}
                    width={32}
                    height={32}
                    className="mr-3 h-8 w-8 rounded-full object-cover border border-white/20"
                    onError={(event) => {
                      event.currentTarget.classList.add('hidden')
                    }}
                  />
                )}
                <h3 className="text-lg font-semibold text-[#f6f5ff] drop-shadow">{stock.name}</h3>
              </div>
              <div className="text-sm text-[#d8dcff]">
                Symbol: <span className="font-semibold text-[#f6f5ff]">{stock.symbol}</span>
              </div>
              <div className="mt-4">
                <button 
                  className="px-4 py-2 bg-[var(--accent)] text-[#1d0618] rounded font-semibold hover:bg-[#ff568c] transition-colors shadow-[0_0_20px_rgba(255,63,125,0.28)]"
                  onClick={(e) => {
                    e.stopPropagation()
                    handlePredictionRequest(stock.symbol)
                  }}
                >
                  Get Prediction
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
      
      {loading && (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[var(--accent)] mx-auto mb-4"></div>
          <p className="text-[#c8cdfd]">Loading prediction...</p>
        </div>
      )}
      
      {error && (
        <div className="bg-[#1a142e]/85 border border-[var(--accent)]/35 text-[var(--accent)] p-4 rounded-lg mb-6 shadow-[0_0_24px_rgba(64,55,255,0.22)]">
          {error}
        </div>
      )}
      
      {prediction && (
  <div className="bg-gradient-to-br from-[#0b0a1f] to-[#17143c] border border-[#222046] rounded-xl shadow-[0_0_32px_rgba(64,55,255,0.26)] p-6 backdrop-blur">
          <h2 className="text-2xl font-bold mb-4 text-[#f1eeff] drop-shadow-[0_0_18px_rgba(123,91,255,0.28)]">Prediction Results</h2>
          <div className="mb-5 text-sm text-[#c8cdfd]">
            <span className="text-[var(--accent-secondary)]">Reference date:</span>{' '}
            <span className="font-semibold text-[#f6f5ff]">
              {prediction.date
                ? new Date(`${prediction.date}T00:00:00Z`).toLocaleDateString()
                : new Date().toLocaleDateString()}
            </span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-gradient-to-br from-[#151436] via-[#202457] to-[#2b2f6c] border border-[var(--accent-secondary)]/30 p-4 rounded-lg shadow-[0_0_24px_rgba(64,55,255,0.24)]">
              <h3 className="text-lg font-medium text-[var(--accent-secondary)] mb-2">High</h3>
              <p className="text-2xl font-bold text-[#f6f5ff]">${prediction.high.toFixed(2)}</p>
            </div>
            <div className="bg-gradient-to-br from-[#151436] via-[#24265a] to-[#313572] border border-[var(--accent-secondary)]/30 p-4 rounded-lg shadow-[0_0_24px_rgba(64,55,255,0.24)]">
              <h3 className="text-lg font-medium text-[var(--accent-secondary)] mb-2">Close</h3>
              <p className="text-2xl font-bold text-[#f6f5ff]">${prediction.close.toFixed(2)}</p>
            </div>
            <div className="bg-gradient-to-br from-[#151436] via-[#292c60] to-[#383a78] border border-[var(--accent-secondary)]/30 p-4 rounded-lg shadow-[0_0_24px_rgba(64,55,255,0.24)]">
              <h3 className="text-lg font-medium text-[var(--accent-secondary)] mb-2">Low</h3>
              <p className="text-2xl font-bold text-[#f6f5ff]">${prediction.low.toFixed(2)}</p>
            </div>
          </div>
          <div className="mt-6 text-sm text-[#c8cdfd]">
            <p>Prediction for {stocks.find(s => s.symbol === prediction.symbol)?.name || prediction.symbol}</p>
          </div>
        </div>
      )}
    </div>
  )
}