'use client';

import { useState } from 'react';
import { TrendingUp, Calculator, Info } from 'lucide-react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar
} from 'recharts';

interface GreeksResult {
  price: number;
  delta: number;
  gamma: number;
  vega: number;
  theta: number;
  rho: number;
}

export default function OptionsPage() {
  const [optionType, setOptionType] = useState<'call' | 'put'>('call');
  const [spotPrice, setSpotPrice] = useState(100);
  const [strikePrice, setStrikePrice] = useState(100);
  const [timeToMaturity, setTimeToMaturity] = useState(1.0);
  const [riskFreeRate, setRiskFreeRate] = useState(0.05);
  const [volatility, setVolatility] = useState(0.20);
  const [dividendYield, setDividendYield] = useState(0.0);

  const [result, setResult] = useState<GreeksResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const calculateOption = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/options/black-scholes', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          S: spotPrice,
          K: strikePrice,
          T: timeToMaturity,
          r: riskFreeRate,
          sigma: volatility,
          q: dividendYield,
          option_type: optionType
        })
      });

      if (!response.ok) {
        throw new Error('Calculation failed');
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Calculation failed');
    } finally {
      setLoading(false);
    }
  };

  // Generate spot price sensitivity data for chart
  const generateSpotSensitivity = () => {
    if (!result) return [];

    const data = [];
    const range = spotPrice * 0.3;
    for (let s = spotPrice - range; s <= spotPrice + range; s += range / 10) {
      // Simplified approximation for visualization
      const moneyness = s / strikePrice;
      const estimatedPrice = result.price + result.delta * (s - spotPrice);
      data.push({
        spot: s.toFixed(2),
        price: Math.max(0, estimatedPrice)
      });
    }
    return data;
  };

  const greeksRadarData = result ? [
    { greek: 'Delta', value: Math.abs(result.delta) * 100, fullMark: 100 },
    { greek: 'Gamma', value: result.gamma * 1000, fullMark: 10 },
    { greek: 'Vega', value: result.vega * 10, fullMark: 5 },
    { greek: 'Theta', value: Math.abs(result.theta / 252) * 100, fullMark: 1 },
    { greek: 'Rho', value: Math.abs(result.rho) * 10, fullMark: 5 }
  ] : [];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
      {/* Header */}
      <header className="border-b border-slate-800 bg-slate-900/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                <Calculator className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white">Black-Scholes Options Calculator</h1>
                <p className="text-sm text-slate-400">European option pricing with Greeks</p>
              </div>
            </div>
            <a
              href="/"
              className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg transition-all"
            >
              ← Dashboard
            </a>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Input Panel */}
          <div className="lg:col-span-1">
            <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-slate-700 space-y-6">
              <h2 className="text-xl font-bold text-white mb-4">Option Parameters</h2>

              {/* Option Type Toggle */}
              <div>
                <label className="block text-sm text-slate-400 mb-2">Option Type</label>
                <div className="grid grid-cols-2 gap-2">
                  <button
                    onClick={() => setOptionType('call')}
                    className={`px-4 py-2 rounded-lg transition-all ${
                      optionType === 'call'
                        ? 'bg-green-500 text-white'
                        : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                    }`}
                  >
                    Call
                  </button>
                  <button
                    onClick={() => setOptionType('put')}
                    className={`px-4 py-2 rounded-lg transition-all ${
                      optionType === 'put'
                        ? 'bg-red-500 text-white'
                        : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                    }`}
                  >
                    Put
                  </button>
                </div>
              </div>

              {/* Spot Price */}
              <div>
                <label className="block text-sm text-slate-400 mb-2">
                  Spot Price (S) <span className="text-white">${spotPrice}</span>
                </label>
                <input
                  type="range"
                  min="50"
                  max="200"
                  step="1"
                  value={spotPrice}
                  onChange={(e) => setSpotPrice(Number(e.target.value))}
                  className="w-full"
                />
              </div>

              {/* Strike Price */}
              <div>
                <label className="block text-sm text-slate-400 mb-2">
                  Strike Price (K) <span className="text-white">${strikePrice}</span>
                </label>
                <input
                  type="range"
                  min="50"
                  max="200"
                  step="1"
                  value={strikePrice}
                  onChange={(e) => setStrikePrice(Number(e.target.value))}
                  className="w-full"
                />
              </div>

              {/* Time to Maturity */}
              <div>
                <label className="block text-sm text-slate-400 mb-2">
                  Time to Maturity (T) <span className="text-white">{timeToMaturity.toFixed(2)} years</span>
                </label>
                <input
                  type="range"
                  min="0.1"
                  max="5"
                  step="0.1"
                  value={timeToMaturity}
                  onChange={(e) => setTimeToMaturity(Number(e.target.value))}
                  className="w-full"
                />
              </div>

              {/* Risk-Free Rate */}
              <div>
                <label className="block text-sm text-slate-400 mb-2">
                  Risk-Free Rate (r) <span className="text-white">{(riskFreeRate * 100).toFixed(1)}%</span>
                </label>
                <input
                  type="range"
                  min="0"
                  max="0.10"
                  step="0.001"
                  value={riskFreeRate}
                  onChange={(e) => setRiskFreeRate(Number(e.target.value))}
                  className="w-full"
                />
              </div>

              {/* Volatility */}
              <div>
                <label className="block text-sm text-slate-400 mb-2">
                  Volatility (σ) <span className="text-white">{(volatility * 100).toFixed(1)}%</span>
                </label>
                <input
                  type="range"
                  min="0.05"
                  max="1.0"
                  step="0.01"
                  value={volatility}
                  onChange={(e) => setVolatility(Number(e.target.value))}
                  className="w-full"
                />
              </div>

              {/* Dividend Yield */}
              <div>
                <label className="block text-sm text-slate-400 mb-2">
                  Dividend Yield (q) <span className="text-white">{(dividendYield * 100).toFixed(1)}%</span>
                </label>
                <input
                  type="range"
                  min="0"
                  max="0.10"
                  step="0.001"
                  value={dividendYield}
                  onChange={(e) => setDividendYield(Number(e.target.value))}
                  className="w-full"
                />
              </div>

              <button
                onClick={calculateOption}
                disabled={loading}
                className="w-full px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg hover:from-blue-600 hover:to-purple-700 disabled:opacity-50 transition-all font-semibold"
              >
                {loading ? 'Calculating...' : 'Calculate Price & Greeks'}
              </button>

              {error && (
                <div className="bg-red-500/10 border border-red-500 rounded-lg p-4 text-red-400 text-sm">
                  {error}
                </div>
              )}
            </div>
          </div>

          {/* Results Panel */}
          <div className="lg:col-span-2 space-y-6">
            {result ? (
              <>
                {/* Price Display */}
                <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-8 border border-slate-700">
                  <div className="text-center">
                    <p className="text-slate-400 text-sm mb-2">Option Price</p>
                    <p className="text-6xl font-bold text-white mb-2">${result.price.toFixed(4)}</p>
                    <p className="text-slate-400">
                      {spotPrice > strikePrice ? 'In-the-Money' : spotPrice < strikePrice ? 'Out-of-the-Money' : 'At-the-Money'}
                    </p>
                  </div>
                </div>

                {/* Greeks Grid */}
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                  <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-slate-700">
                    <div className="flex items-center gap-2 mb-2">
                      <TrendingUp className="w-4 h-4 text-blue-400" />
                      <p className="text-slate-400 text-sm">Delta (Δ)</p>
                    </div>
                    <p className="text-3xl font-bold text-white">{result.delta.toFixed(4)}</p>
                    <p className="text-xs text-slate-500 mt-1">Price sensitivity</p>
                  </div>

                  <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-slate-700">
                    <div className="flex items-center gap-2 mb-2">
                      <Info className="w-4 h-4 text-green-400" />
                      <p className="text-slate-400 text-sm">Gamma (Γ)</p>
                    </div>
                    <p className="text-3xl font-bold text-white">{result.gamma.toFixed(4)}</p>
                    <p className="text-xs text-slate-500 mt-1">Delta sensitivity</p>
                  </div>

                  <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-slate-700">
                    <div className="flex items-center gap-2 mb-2">
                      <Info className="w-4 h-4 text-purple-400" />
                      <p className="text-slate-400 text-sm">Vega (ν)</p>
                    </div>
                    <p className="text-3xl font-bold text-white">{result.vega.toFixed(4)}</p>
                    <p className="text-xs text-slate-500 mt-1">Vol sensitivity</p>
                  </div>

                  <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-slate-700">
                    <div className="flex items-center gap-2 mb-2">
                      <Info className="w-4 h-4 text-orange-400" />
                      <p className="text-slate-400 text-sm">Theta (Θ)</p>
                    </div>
                    <p className="text-3xl font-bold text-white">{result.theta.toFixed(4)}</p>
                    <p className="text-xs text-slate-500 mt-1">Time decay (annual)</p>
                  </div>

                  <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-slate-700">
                    <div className="flex items-center gap-2 mb-2">
                      <Info className="w-4 h-4 text-red-400" />
                      <p className="text-slate-400 text-sm">Rho (ρ)</p>
                    </div>
                    <p className="text-3xl font-bold text-white">{result.rho.toFixed(4)}</p>
                    <p className="text-xs text-slate-500 mt-1">Rate sensitivity</p>
                  </div>

                  <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-slate-700">
                    <div className="flex items-center gap-2 mb-2">
                      <Info className="w-4 h-4 text-yellow-400" />
                      <p className="text-slate-400 text-sm">Theta (Daily)</p>
                    </div>
                    <p className="text-3xl font-bold text-white">{(result.theta / 252).toFixed(4)}</p>
                    <p className="text-xs text-slate-500 mt-1">Daily time decay</p>
                  </div>
                </div>

                {/* Charts */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Spot Price Sensitivity */}
                  <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-slate-700">
                    <h3 className="text-lg font-bold text-white mb-4">Spot Price Sensitivity</h3>
                    <ResponsiveContainer width="100%" height={250}>
                      <LineChart data={generateSpotSensitivity()}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                        <XAxis dataKey="spot" stroke="#94a3b8" />
                        <YAxis stroke="#94a3b8" />
                        <Tooltip
                          contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                        />
                        <Line type="monotone" dataKey="price" stroke="#3b82f6" strokeWidth={2} />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>

                  {/* Greeks Radar */}
                  <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-slate-700">
                    <h3 className="text-lg font-bold text-white mb-4">Greeks Profile</h3>
                    <ResponsiveContainer width="100%" height={250}>
                      <RadarChart data={greeksRadarData}>
                        <PolarGrid stroke="#334155" />
                        <PolarAngleAxis dataKey="greek" stroke="#94a3b8" />
                        <PolarRadiusAxis stroke="#94a3b8" />
                        <Radar name="Greeks" dataKey="value" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.6} />
                        <Tooltip
                          contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                        />
                      </RadarChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              </>
            ) : (
              <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-12 border border-slate-700 text-center">
                <Calculator className="w-16 h-16 mx-auto mb-4 text-slate-600" />
                <p className="text-slate-400">
                  Adjust parameters and click &quot;Calculate&quot; to see option pricing and Greeks
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
