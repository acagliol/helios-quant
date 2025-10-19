'use client';

import { useState } from 'react';
import { TrendingUp, Activity, Info } from 'lucide-react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';

interface HestonResult {
  call_price: number;
  put_price: number;
  implied_vol: number;
}

export default function HestonPage() {
  const [spotPrice, setSpotPrice] = useState(100);
  const [strikePrice, setStrikePrice] = useState(100);
  const [timeToMaturity, setTimeToMaturity] = useState(1.0);
  const [riskFreeRate, setRiskFreeRate] = useState(0.05);
  const [currentVariance, setCurrentVariance] = useState(0.04);
  const [kappa, setKappa] = useState(2.0);
  const [theta, setTheta] = useState(0.04);
  const [sigma, setSigma] = useState(0.3);
  const [rho, setRho] = useState(-0.7);

  const [result, setResult] = useState<HestonResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const calculateHeston = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/options/heston', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          S0: spotPrice,
          K: strikePrice,
          T: timeToMaturity,
          r: riskFreeRate,
          v0: currentVariance,
          kappa: kappa,
          theta: theta,
          sigma: sigma,
          rho: rho
        })
      });

      if (!response.ok) throw new Error('Calculation failed');
      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Calculation failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
      {/* Header */}
      <header className="border-b border-slate-800 bg-slate-900/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-600 rounded-lg flex items-center justify-center">
                <Activity className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white">Heston Stochastic Volatility</h1>
                <p className="text-sm text-slate-400">Advanced option pricing with volatility smile</p>
              </div>
            </div>
            <a href="/" className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg transition-all">
              ← Dashboard
            </a>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Input Panel */}
          <div className="lg:col-span-1 space-y-6">
            <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-slate-700">
              <h2 className="text-xl font-bold text-white mb-4">Market Parameters</h2>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm text-slate-400 mb-2">
                    Spot Price (S₀) <span className="text-white">${spotPrice}</span>
                  </label>
                  <input type="range" min="50" max="200" step="1" value={spotPrice}
                    onChange={(e) => setSpotPrice(Number(e.target.value))} className="w-full" />
                </div>

                <div>
                  <label className="block text-sm text-slate-400 mb-2">
                    Strike Price (K) <span className="text-white">${strikePrice}</span>
                  </label>
                  <input type="range" min="50" max="200" step="1" value={strikePrice}
                    onChange={(e) => setStrikePrice(Number(e.target.value))} className="w-full" />
                </div>

                <div>
                  <label className="block text-sm text-slate-400 mb-2">
                    Time to Maturity (T) <span className="text-white">{timeToMaturity.toFixed(2)} years</span>
                  </label>
                  <input type="range" min="0.1" max="5" step="0.1" value={timeToMaturity}
                    onChange={(e) => setTimeToMaturity(Number(e.target.value))} className="w-full" />
                </div>

                <div>
                  <label className="block text-sm text-slate-400 mb-2">
                    Risk-Free Rate (r) <span className="text-white">{(riskFreeRate * 100).toFixed(1)}%</span>
                  </label>
                  <input type="range" min="0" max="0.10" step="0.001" value={riskFreeRate}
                    onChange={(e) => setRiskFreeRate(Number(e.target.value))} className="w-full" />
                </div>
              </div>
            </div>

            <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-slate-700">
              <h2 className="text-xl font-bold text-white mb-4">Heston Parameters</h2>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm text-slate-400 mb-2">
                    Current Variance (v₀) <span className="text-white">{currentVariance.toFixed(4)}</span>
                  </label>
                  <input type="range" min="0.01" max="0.20" step="0.01" value={currentVariance}
                    onChange={(e) => setCurrentVariance(Number(e.target.value))} className="w-full" />
                  <p className="text-xs text-slate-500 mt-1">√v₀ = {Math.sqrt(currentVariance).toFixed(2)} (vol)</p>
                </div>

                <div>
                  <label className="block text-sm text-slate-400 mb-2">
                    Mean Reversion Speed (κ) <span className="text-white">{kappa.toFixed(2)}</span>
                  </label>
                  <input type="range" min="0.1" max="5.0" step="0.1" value={kappa}
                    onChange={(e) => setKappa(Number(e.target.value))} className="w-full" />
                </div>

                <div>
                  <label className="block text-sm text-slate-400 mb-2">
                    Long-term Variance (θ) <span className="text-white">{theta.toFixed(4)}</span>
                  </label>
                  <input type="range" min="0.01" max="0.20" step="0.01" value={theta}
                    onChange={(e) => setTheta(Number(e.target.value))} className="w-full" />
                  <p className="text-xs text-slate-500 mt-1">√θ = {Math.sqrt(theta).toFixed(2)} (long-term vol)</p>
                </div>

                <div>
                  <label className="block text-sm text-slate-400 mb-2">
                    Vol of Vol (σ) <span className="text-white">{sigma.toFixed(2)}</span>
                  </label>
                  <input type="range" min="0.1" max="1.0" step="0.05" value={sigma}
                    onChange={(e) => setSigma(Number(e.target.value))} className="w-full" />
                </div>

                <div>
                  <label className="block text-sm text-slate-400 mb-2">
                    Correlation (ρ) <span className="text-white">{rho.toFixed(2)}</span>
                  </label>
                  <input type="range" min="-1" max="1" step="0.05" value={rho}
                    onChange={(e) => setRho(Number(e.target.value))} className="w-full" />
                  <p className="text-xs text-slate-500 mt-1">
                    {rho < 0 ? 'Negative: Leverage effect' : 'Positive: Inverse leverage'}
                  </p>
                </div>

                <div className="bg-slate-900/50 rounded-lg p-3 border border-slate-700">
                  <p className="text-xs text-slate-400 mb-1">Feller Condition</p>
                  <p className="text-sm text-white">
                    2κθ = {(2 * kappa * theta).toFixed(4)} {(2 * kappa * theta) >= sigma**2 ? '≥' : '<'} σ² = {(sigma**2).toFixed(4)}
                  </p>
                  {(2 * kappa * theta) < sigma**2 && (
                    <p className="text-xs text-orange-400 mt-1">⚠️ Variance can reach zero</p>
                  )}
                </div>
              </div>
            </div>

            <button
              onClick={calculateHeston}
              disabled={loading}
              className="w-full px-6 py-3 bg-gradient-to-r from-purple-500 to-pink-600 text-white rounded-lg hover:from-purple-600 hover:to-pink-700 disabled:opacity-50 transition-all font-semibold"
            >
              {loading ? 'Calculating...' : 'Calculate Heston Prices'}
            </button>

            {error && (
              <div className="bg-red-500/10 border border-red-500 rounded-lg p-4 text-red-400 text-sm">
                {error}
              </div>
            )}
          </div>

          {/* Results Panel */}
          <div className="lg:col-span-2 space-y-6">
            {result ? (
              <>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-8 border border-slate-700">
                    <div className="text-center">
                      <p className="text-slate-400 text-sm mb-2">Call Price</p>
                      <p className="text-5xl font-bold text-green-400 mb-2">${result.call_price.toFixed(4)}</p>
                    </div>
                  </div>

                  <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-8 border border-slate-700">
                    <div className="text-center">
                      <p className="text-slate-400 text-sm mb-2">Put Price</p>
                      <p className="text-5xl font-bold text-red-400 mb-2">${result.put_price.toFixed(4)}</p>
                    </div>
                  </div>

                  <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-8 border border-slate-700">
                    <div className="text-center">
                      <p className="text-slate-400 text-sm mb-2">Implied Vol</p>
                      <p className="text-5xl font-bold text-purple-400 mb-2">{(result.implied_vol * 100).toFixed(2)}%</p>
                    </div>
                  </div>
                </div>

                <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-slate-700">
                  <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                    <Info className="w-5 h-5 text-purple-400" />
                    Model Characteristics
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                    <div className="bg-slate-900/50 rounded-lg p-4">
                      <p className="text-slate-400 mb-1">Volatility Smile</p>
                      <p className="text-white">Captures market-observed skew</p>
                    </div>
                    <div className="bg-slate-900/50 rounded-lg p-4">
                      <p className="text-slate-400 mb-1">Mean Reversion</p>
                      <p className="text-white">κ = {kappa.toFixed(2)} (speed to long-term variance)</p>
                    </div>
                    <div className="bg-slate-900/50 rounded-lg p-4">
                      <p className="text-slate-400 mb-1">Leverage Effect</p>
                      <p className="text-white">ρ = {rho.toFixed(2)} ({rho < 0 ? 'Negative correlation' : 'Positive correlation'})</p>
                    </div>
                    <div className="bg-slate-900/50 rounded-lg p-4">
                      <p className="text-slate-400 mb-1">Vol Uncertainty</p>
                      <p className="text-white">σ = {sigma.toFixed(2)} (volatility of volatility)</p>
                    </div>
                  </div>
                </div>

                <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-slate-700">
                  <h3 className="text-lg font-bold text-white mb-4">Mathematical Formula</h3>
                  <div className="bg-slate-900/50 rounded-lg p-4 font-mono text-sm text-slate-300 space-y-2">
                    <p>dS = rS dt + √v S dW₁</p>
                    <p>dv = κ(θ - v) dt + σ√v dW₂</p>
                    <p className="text-slate-500 mt-2">where Corr(dW₁, dW₂) = ρ</p>
                  </div>
                </div>
              </>
            ) : (
              <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-12 border border-slate-700 text-center">
                <Activity className="w-16 h-16 mx-auto mb-4 text-slate-600" />
                <p className="text-slate-400">
                  Adjust Heston parameters and click &quot;Calculate&quot; to see stochastic volatility pricing
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
