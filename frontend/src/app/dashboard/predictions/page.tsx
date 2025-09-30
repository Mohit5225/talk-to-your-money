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
      color: 'bg-gradient-to-r from-indigo-800 via-blue-700 to-cyan-600'
    }
  ]

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
    <div className="p-8 text-sky-100">
      <div className="mb-6">
        <Link href="/dashboard" className="text-cyan-300 hover:text-amber-200 transition-colors flex items-center">
          ← Back to Dashboard
        </Link>
      </div>
      
      <h1 className="text-3xl font-bold mb-6 text-amber-200 drop-shadow">Stock Predictions</h1>
      
      <div className="mb-8 bg-indigo-900/60 border border-indigo-700 rounded-xl p-6 shadow-lg backdrop-blur">
        <h2 className="text-xl font-semibold mb-3 text-amber-200">Choose a prediction date</h2>
        <p className="text-sm text-cyan-100 mb-4">Pick a target date for your forecast. Leave it empty to use today.</p>
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
          <label htmlFor="target-date" className="text-sm font-medium text-cyan-200">Prediction date</label>
          <input
            id="target-date"
            type="date"
            value={targetDate}
            onChange={(event) => setTargetDate(event.target.value)}
            className="bg-blue-950/60 border border-cyan-400/50 rounded-md px-3 py-2 text-sky-50 focus:outline-none focus:ring-2 focus:ring-amber-300 focus:border-transparent transition-colors"
          />
        </div>
        <p className="text-xs text-cyan-200 mt-3">Now pick a stock card below to fetch the prediction for that day.</p>
      </div>

      <div className="mb-8">
        <h2 className="text-xl font-semibold mb-4 text-cyan-200">Select a Stock</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {stocks.map((stock) => (
            <div 
              key={stock.symbol}
              className={`${stock.color} p-6 rounded-xl shadow-lg cursor-pointer transform transition-transform hover:scale-105 hover:shadow-2xl border border-cyan-400/40`}
              onClick={() => handlePredictionRequest(stock.symbol)}
            >
              <div className="flex items-center mb-4">
                {stock.logo && (
                  <Image
                    src={stock.logo}
                    alt={stock.name}
                    width={32}
                    height={32}
                    className="mr-3 h-8 w-8 rounded-full object-cover"
                    onError={(event) => {
                      event.currentTarget.classList.add('hidden')
                    }}
                  />
                )}
                <h3 className="text-lg font-semibold text-white drop-shadow">{stock.name}</h3>
              </div>
              <div className="text-sm text-cyan-100">
                Symbol: <span className="font-semibold text-white">{stock.symbol}</span>
              </div>
              <div className="mt-4">
                <button 
                  className="px-4 py-2 bg-amber-400 text-blue-950 rounded font-semibold hover:bg-amber-300 transition-colors"
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
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-amber-300 mx-auto mb-4"></div>
          <p className="text-cyan-100">Loading prediction...</p>
        </div>
      )}
      
      {error && (
        <div className="bg-rose-900/60 border border-rose-500 text-rose-100 p-4 rounded-lg mb-6">
          {error}
        </div>
      )}
      
      {prediction && (
        <div className="bg-indigo-900/80 border border-indigo-700 rounded-xl shadow-xl p-6 backdrop-blur">
          <h2 className="text-2xl font-bold mb-4 text-amber-200">Prediction Results</h2>
          <div className="mb-5 text-sm text-cyan-100">
            <span className="text-cyan-200">Reference date:</span>{' '}
            <span className="font-semibold text-amber-200">
              {prediction.date
                ? new Date(`${prediction.date}T00:00:00Z`).toLocaleDateString()
                : new Date().toLocaleDateString()}
            </span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-emerald-700/40 border border-emerald-400/60 p-4 rounded-lg">
              <h3 className="text-lg font-medium text-emerald-200 mb-2">High</h3>
              <p className="text-2xl font-bold text-emerald-100">${prediction.high.toFixed(2)}</p>
            </div>
            <div className="bg-cyan-700/40 border border-cyan-400/60 p-4 rounded-lg">
              <h3 className="text-lg font-medium text-cyan-100 mb-2">Close</h3>
              <p className="text-2xl font-bold text-cyan-50">${prediction.close.toFixed(2)}</p>
            </div>
            <div className="bg-rose-700/40 border border-rose-400/60 p-4 rounded-lg">
              <h3 className="text-lg font-medium text-rose-100 mb-2">Low</h3>
              <p className="text-2xl font-bold text-rose-50">${prediction.low.toFixed(2)}</p>
            </div>
          </div>
          <div className="mt-6 text-sm text-cyan-100">
            <p>Prediction for {stocks.find(s => s.symbol === prediction.symbol)?.name || prediction.symbol}</p>
          </div>
        </div>
      )}
    </div>
  )
}