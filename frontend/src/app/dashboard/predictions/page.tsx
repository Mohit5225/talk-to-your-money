'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'

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
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [prediction, setPrediction] = useState<PredictionResult | null>(null)
  const [error, setError] = useState('')
  
  const stocks: Stock[] = [
    {
      symbol: 'AAPL',
      name: 'Apple Inc.',
      logo: 'https://logo.clearbit.com/apple.com',
      color: 'bg-gradient-to-r from-gray-50 to-gray-100'
    }
  ]

  const handlePredictionRequest = async (symbol: string) => {
    setLoading(true)
    setPrediction(null)
    setError('')
    
    try {
      // Make API call to your backend
      const response = await fetch(`http://localhost:8000/predict/${symbol}`, {
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
    <div className="p-8">
      <div className="mb-6">
        <Link href="/dashboard" className="text-blue-600 hover:underline flex items-center">
          ← Back to Dashboard
        </Link>
      </div>
      
      <h1 className="text-3xl font-bold mb-6">Stock Predictions</h1>
      
      <div className="mb-8">
        <h2 className="text-xl font-semibold mb-4">Select a Stock</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {stocks.map((stock) => (
            <div 
              key={stock.symbol}
              className={`${stock.color} p-6 rounded-lg shadow-md cursor-pointer transform transition-transform hover:scale-105`}
              onClick={() => handlePredictionRequest(stock.symbol)}
            >
              <div className="flex items-center mb-4">
                {stock.logo && (
                  <img 
                    src={stock.logo} 
                    alt={stock.name} 
                    className="w-8 h-8 mr-3 rounded-full"
                    onError={(e) => {
                      e.currentTarget.style.display = 'none'
                    }}
                  />
                )}
                <h3 className="text-lg font-semibold">{stock.name}</h3>
              </div>
              <div className="text-sm text-gray-600">
                Symbol: <span className="font-medium">{stock.symbol}</span>
              </div>
              <div className="mt-4">
                <button 
                  className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
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
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p>Loading prediction...</p>
        </div>
      )}
      
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-800 p-4 rounded-lg mb-6">
          {error}
        </div>
      )}
      
      {prediction && (
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-2xl font-bold mb-4">Prediction Results</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-green-50 p-4 rounded-lg">
              <h3 className="text-lg font-medium text-green-800 mb-2">High</h3>
              <p className="text-2xl font-bold text-green-700">${prediction.high.toFixed(2)}</p>
            </div>
            <div className="bg-blue-50 p-4 rounded-lg">
              <h3 className="text-lg font-medium text-blue-800 mb-2">Close</h3>
              <p className="text-2xl font-bold text-blue-700">${prediction.close.toFixed(2)}</p>
            </div>
            <div className="bg-red-50 p-4 rounded-lg">
              <h3 className="text-lg font-medium text-red-800 mb-2">Low</h3>
              <p className="text-2xl font-bold text-red-700">${prediction.low.toFixed(2)}</p>
            </div>
          </div>
          <div className="mt-6 text-sm text-gray-600">
            <p>Prediction for {stocks.find(s => s.symbol === prediction.symbol)?.name || prediction.symbol}</p>
            <p className="mt-1">Date: {new Date().toLocaleDateString()}</p>
          </div>
        </div>
      )}
    </div>
  )
}