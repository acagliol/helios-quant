'use client'

import { useState } from 'react'
import Link from 'next/link'
import { TrendingUp, PieChart as PieChartIcon, Target, Shield } from 'lucide-react'

interface OptimizationResult {
  method: string
  weights: number[]
  expected_return: number
  volatility: number
  sharpe_ratio?: number
  cvar?: number
  efficient_frontier?: {
    returns: number[]
    volatilities: number[]
  }
}

const SAMPLE_TICKERS = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'JPM', 'BAC', 'GLD', 'TLT', 'BTC']

export default function PortfolioOptimizePage() {
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState<Record<string, OptimizationResult> | null>(null)
  const [error, setError] = useState<string | null>(null)

  // Portfolio settings
  const [nAssets, setNAssets] = useState(10)
  const [riskFreeRate, setRiskFreeRate] = useState(0.02)
  const [optimizationMethod, setOptimizationMethod] = useState<'all' | 'markowitz' | 'risk_parity' | 'cvar'>('all')

  const runOptimization = async () => {
    setLoading(true)
    setError(null)
    setResults(null)

    try {
      const response = await fetch('/api/portfolio/optimize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          n_assets: nAssets,
          risk_free_rate: riskFreeRate,
          method: optimizationMethod,
        }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Optimization failed')
      }

      setResults(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }

  const formatPercent = (value: number) => `${(value * 100).toFixed(2)}%`

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 p-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <Link
            href="/"
            className="text-blue-300 hover:text-blue-100 transition-colors mb-4 inline-block"
          >
            ← Back to Dashboard
          </Link>
          <h1 className="text-5xl font-bold text-white mb-4">
            Portfolio Optimization
          </h1>
          <p className="text-blue-200 text-lg">
            Modern Portfolio Theory: Markowitz, Risk Parity & CVaR
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Settings Panel */}
          <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-blue-500/30">
            <h2 className="text-2xl font-bold text-white mb-6">Settings</h2>

            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-blue-200 mb-2">
                  Number of Assets: {nAssets}
                </label>
                <input
                  type="range"
                  min="5"
                  max="20"
                  step="1"
                  value={nAssets}
                  onChange={(e) => setNAssets(Number(e.target.value))}
                  className="w-full"
                />
                <p className="text-xs text-blue-300 mt-1">
                  Sample tickers: {SAMPLE_TICKERS.slice(0, nAssets).join(', ')}
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-blue-200 mb-2">
                  Risk-Free Rate: {formatPercent(riskFreeRate)}
                </label>
                <input
                  type="range"
                  min="0"
                  max="0.05"
                  step="0.005"
                  value={riskFreeRate}
                  onChange={(e) => setRiskFreeRate(Number(e.target.value))}
                  className="w-full"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-blue-200 mb-2">
                  Optimization Method
                </label>
                <select
                  value={optimizationMethod}
                  onChange={(e) => setOptimizationMethod(e.target.value as any)}
                  className="w-full px-4 py-2 rounded-lg bg-white/10 text-white border border-blue-500/30 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="all">All Methods (Compare)</option>
                  <option value="markowitz">Markowitz (Max Sharpe)</option>
                  <option value="risk_parity">Risk Parity</option>
                  <option value="cvar">CVaR Optimization</option>
                </select>
              </div>

              <button
                onClick={runOptimization}
                disabled={loading}
                className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-3 px-6 rounded-lg font-semibold hover:from-blue-700 hover:to-purple-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Optimizing...' : 'Run Optimization'}
              </button>
            </div>

            <div className="mt-8 border-t border-blue-500/30 pt-6">
              <h3 className="text-lg font-semibold text-blue-300 mb-3">Methods</h3>
              <div className="space-y-3 text-sm text-blue-200">
                <div>
                  <strong className="text-blue-100">Markowitz:</strong> Maximize Sharpe ratio
                </div>
                <div>
                  <strong className="text-blue-100">Risk Parity:</strong> Equal risk contribution
                </div>
                <div>
                  <strong className="text-blue-100">CVaR:</strong> Minimize tail risk (95%)
                </div>
              </div>
            </div>
          </div>

          {/* Results Panel */}
          <div className="lg:col-span-2 space-y-6">
            {error && (
              <div className="bg-red-500/20 border border-red-500 text-red-200 px-4 py-3 rounded-lg">
                {error}
              </div>
            )}

            {results && (
              <>
                {/* Comparison Cards */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {Object.entries(results).map(([method, data]) => (
                    <div
                      key={method}
                      className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-blue-500/30"
                    >
                      <div className="flex items-center gap-3 mb-4">
                        {method === 'markowitz' && <Target className="w-6 h-6 text-blue-400" />}
                        {method === 'risk_parity' && <Shield className="w-6 h-6 text-green-400" />}
                        {method === 'cvar' && <TrendingUp className="w-6 h-6 text-purple-400" />}
                        <h3 className="text-lg font-semibold text-white capitalize">
                          {method.replace('_', ' ')}
                        </h3>
                      </div>

                      <div className="space-y-3">
                        <div>
                          <div className="text-sm text-blue-200">Expected Return</div>
                          <div className="text-2xl font-bold text-white">
                            {formatPercent(data.expected_return)}
                          </div>
                        </div>

                        <div>
                          <div className="text-sm text-blue-200">Volatility</div>
                          <div className="text-xl font-semibold text-white">
                            {formatPercent(data.volatility)}
                          </div>
                        </div>

                        {data.sharpe_ratio !== undefined && (
                          <div>
                            <div className="text-sm text-blue-200">Sharpe Ratio</div>
                            <div className="text-xl font-semibold text-green-400">
                              {data.sharpe_ratio.toFixed(3)}
                            </div>
                          </div>
                        )}

                        {data.cvar !== undefined && (
                          <div>
                            <div className="text-sm text-blue-200">CVaR (95%)</div>
                            <div className="text-xl font-semibold text-red-400">
                              {formatPercent(data.cvar)}
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>

                {/* Asset Allocation */}
                {Object.entries(results).map(([method, data]) => (
                  <div
                    key={method}
                    className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-blue-500/30"
                  >
                    <h3 className="text-xl font-bold text-white mb-4 capitalize flex items-center gap-2">
                      <PieChartIcon className="w-5 h-5" />
                      {method.replace('_', ' ')} - Asset Allocation
                    </h3>

                    <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
                      {data.weights.map((weight, idx) => {
                        if (weight < 0.001) return null // Hide tiny weights
                        return (
                          <div
                            key={idx}
                            className="bg-white/5 rounded-lg p-3 border border-blue-500/20"
                          >
                            <div className="text-sm font-semibold text-blue-300">
                              {SAMPLE_TICKERS[idx]}
                            </div>
                            <div className="text-lg font-bold text-white">
                              {formatPercent(weight)}
                            </div>
                            <div className="mt-2 bg-blue-900/30 rounded-full h-2 overflow-hidden">
                              <div
                                className="bg-gradient-to-r from-blue-500 to-purple-500 h-full rounded-full"
                                style={{ width: `${weight * 100}%` }}
                              />
                            </div>
                          </div>
                        )
                      })}
                    </div>
                  </div>
                ))}

                {/* Performance Summary */}
                <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-blue-500/30">
                  <h3 className="text-xl font-bold text-white mb-4">Performance Summary</h3>
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b border-blue-500/30">
                          <th className="text-left py-3 px-4 text-blue-200 font-semibold">Method</th>
                          <th className="text-right py-3 px-4 text-blue-200 font-semibold">Return</th>
                          <th className="text-right py-3 px-4 text-blue-200 font-semibold">Volatility</th>
                          <th className="text-right py-3 px-4 text-blue-200 font-semibold">Sharpe</th>
                          <th className="text-right py-3 px-4 text-blue-200 font-semibold">CVaR</th>
                        </tr>
                      </thead>
                      <tbody>
                        {Object.entries(results).map(([method, data]) => (
                          <tr key={method} className="border-b border-blue-500/10">
                            <td className="py-3 px-4 text-white font-medium capitalize">
                              {method.replace('_', ' ')}
                            </td>
                            <td className="text-right py-3 px-4 text-white">
                              {formatPercent(data.expected_return)}
                            </td>
                            <td className="text-right py-3 px-4 text-white">
                              {formatPercent(data.volatility)}
                            </td>
                            <td className="text-right py-3 px-4 text-green-400 font-semibold">
                              {data.sharpe_ratio?.toFixed(3) || '-'}
                            </td>
                            <td className="text-right py-3 px-4 text-red-400">
                              {data.cvar ? formatPercent(data.cvar) : '-'}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </>
            )}

            {!results && !error && !loading && (
              <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-12 border border-blue-500/30 text-center">
                <PieChartIcon className="w-16 h-16 text-blue-400 mx-auto mb-4 opacity-50" />
                <p className="text-blue-200 text-lg">
                  Configure settings and run optimization to see results
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Info Section */}
        <div className="mt-8 bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-blue-500/30">
          <h2 className="text-2xl font-bold text-white mb-4">About Portfolio Optimization</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-blue-200">
            <div>
              <h3 className="font-semibold text-blue-300 mb-2">Markowitz Mean-Variance</h3>
              <p className="text-sm">
                Modern Portfolio Theory classic. Maximizes Sharpe ratio (risk-adjusted return) by optimizing
                the tradeoff between expected return and volatility. Uses quadratic programming.
              </p>
            </div>
            <div>
              <h3 className="font-semibold text-blue-300 mb-2">Risk Parity</h3>
              <p className="text-sm">
                Each asset contributes equally to total portfolio risk (not equal weights!). Better
                diversification than equal weighting. Popular in institutional portfolios.
              </p>
            </div>
            <div>
              <h3 className="font-semibold text-blue-300 mb-2">CVaR Optimization</h3>
              <p className="text-sm">
                Minimizes Conditional Value at Risk - the expected loss in the worst 5% of scenarios.
                Better tail risk management than variance. Coherent risk measure.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
