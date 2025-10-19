'use client';

import { useState } from 'react';
import { Sparkles } from 'lucide-react';

type ExoticType = 'asian' | 'barrier' | 'lookback' | 'digital';

interface ExoticResult {
  price: number;
  option_type?: string;
  exotic_type?: string;
}

export default function ExoticPage() {
  const [exoticType, setExoticType] = useState<ExoticType>('asian');
  const [S, setS] = useState(100);
  const [K, setK] = useState(100);
  const [T, setT] = useState(1.0);
  const [r, setR] = useState(0.05);
  const [sigma, setSigma] = useState(0.20);
  const [optionType, setOptionType] = useState<'call' | 'put'>('call');

  // Asian specific
  const [averageType, setAverageType] = useState<'arithmetic' | 'geometric'>('arithmetic');

  // Barrier specific
  const [barrier, setBarrier] = useState(120);
  const [barrierType, setBarrierType] = useState<'up-and-out' | 'up-and-in' | 'down-and-out' | 'down-and-in'>('up-and-out');

  // Lookback specific
  const [strikeType, setStrikeType] = useState<'fixed' | 'floating'>('floating');

  // Digital specific
  const [payoutType, setPayoutType] = useState<'cash' | 'asset'>('cash');
  const [payoutAmount, setPayoutAmount] = useState(10);

  const [result, setResult] = useState<ExoticResult | null>(null);
  const [loading, setLoading] = useState(false);

  const calculate = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/options/exotic', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          exotic_type: exoticType,
          S, K, T, r, sigma,
          option_type: optionType,
          ...(exoticType === 'asian' && { average_type: averageType }),
          ...(exoticType === 'barrier' && { barrier, barrier_type: barrierType }),
          ...(exoticType === 'lookback' && { strike_type: strikeType, K: strikeType === 'fixed' ? K : null }),
          ...(exoticType === 'digital' && { payout_type: payoutType, payout_amount: payoutAmount })
        })
      });
      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
      <header className="border-b border-slate-800 bg-slate-900/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-yellow-500 to-orange-600 rounded-lg flex items-center justify-center">
                <Sparkles className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white">Exotic Options</h1>
                <p className="text-sm text-slate-400">Asian, Barrier, Lookback & Digital</p>
              </div>
            </div>
            <a href="/" className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg transition-all">← Dashboard</a>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-6 py-8">
        {/* Type Selector */}
        <div className="grid grid-cols-4 gap-4 mb-8">
          {(['asian', 'barrier', 'lookback', 'digital'] as ExoticType[]).map((type) => (
            <button
              key={type}
              onClick={() => setExoticType(type)}
              className={`px-6 py-4 rounded-xl font-semibold transition-all ${
                exoticType === type
                  ? 'bg-gradient-to-r from-yellow-500 to-orange-600 text-white'
                  : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
              }`}
            >
              {type.charAt(0).toUpperCase() + type.slice(1)}
            </button>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Parameters */}
          <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-slate-700 space-y-4">
            <h2 className="text-xl font-bold text-white mb-4">Parameters</h2>

            <div className="grid grid-cols-2 gap-2">
              <button onClick={() => setOptionType('call')} className={`px-4 py-2 rounded-lg ${optionType === 'call' ? 'bg-green-500' : 'bg-slate-700'}`}>Call</button>
              <button onClick={() => setOptionType('put')} className={`px-4 py-2 rounded-lg ${optionType === 'put' ? 'bg-red-500' : 'bg-slate-700'}`}>Put</button>
            </div>

            <div>
              <label className="block text-sm text-slate-400 mb-2">Spot ${S}</label>
              <input type="range" min="50" max="200" value={S} onChange={(e) => setS(Number(e.target.value))} className="w-full" />
            </div>

            {(exoticType !== 'lookback' || strikeType === 'fixed') && (
              <div>
                <label className="block text-sm text-slate-400 mb-2">Strike ${K}</label>
                <input type="range" min="50" max="200" value={K} onChange={(e) => setK(Number(e.target.value))} className="w-full" />
              </div>
            )}

            <div>
              <label className="block text-sm text-slate-400 mb-2">Time {T.toFixed(2)}y</label>
              <input type="range" min="0.1" max="5" step="0.1" value={T} onChange={(e) => setT(Number(e.target.value))} className="w-full" />
            </div>

            <div>
              <label className="block text-sm text-slate-400 mb-2">Rate {(r*100).toFixed(1)}%</label>
              <input type="range" min="0" max="0.10" step="0.01" value={r} onChange={(e) => setR(Number(e.target.value))} className="w-full" />
            </div>

            <div>
              <label className="block text-sm text-slate-400 mb-2">Vol {(sigma*100).toFixed(0)}%</label>
              <input type="range" min="0.05" max="1" step="0.01" value={sigma} onChange={(e) => setSigma(Number(e.target.value))} className="w-full" />
            </div>

            {/* Type-specific params */}
            {exoticType === 'asian' && (
              <div className="grid grid-cols-2 gap-2">
                <button onClick={() => setAverageType('arithmetic')} className={`px-4 py-2 rounded-lg text-sm ${averageType === 'arithmetic' ? 'bg-blue-500' : 'bg-slate-700'}`}>Arithmetic</button>
                <button onClick={() => setAverageType('geometric')} className={`px-4 py-2 rounded-lg text-sm ${averageType === 'geometric' ? 'bg-blue-500' : 'bg-slate-700'}`}>Geometric</button>
              </div>
            )}

            {exoticType === 'barrier' && (
              <>
                <div>
                  <label className="block text-sm text-slate-400 mb-2">Barrier ${barrier}</label>
                  <input type="range" min="80" max="150" value={barrier} onChange={(e) => setBarrier(Number(e.target.value))} className="w-full" />
                </div>
                <select value={barrierType} onChange={(e) => setBarrierType(e.target.value as any)} className="w-full bg-slate-700 text-white rounded-lg px-4 py-2">
                  <option value="up-and-out">Up-and-Out</option>
                  <option value="up-and-in">Up-and-In</option>
                  <option value="down-and-out">Down-and-Out</option>
                  <option value="down-and-in">Down-and-In</option>
                </select>
              </>
            )}

            {exoticType === 'lookback' && (
              <div className="grid grid-cols-2 gap-2">
                <button onClick={() => setStrikeType('floating')} className={`px-4 py-2 rounded-lg text-sm ${strikeType === 'floating' ? 'bg-purple-500' : 'bg-slate-700'}`}>Floating</button>
                <button onClick={() => setStrikeType('fixed')} className={`px-4 py-2 rounded-lg text-sm ${strikeType === 'fixed' ? 'bg-purple-500' : 'bg-slate-700'}`}>Fixed</button>
              </div>
            )}

            {exoticType === 'digital' && (
              <>
                <div className="grid grid-cols-2 gap-2">
                  <button onClick={() => setPayoutType('cash')} className={`px-4 py-2 rounded-lg text-sm ${payoutType === 'cash' ? 'bg-green-500' : 'bg-slate-700'}`}>Cash</button>
                  <button onClick={() => setPayoutType('asset')} className={`px-4 py-2 rounded-lg text-sm ${payoutType === 'asset' ? 'bg-green-500' : 'bg-slate-700'}`}>Asset</button>
                </div>
                {payoutType === 'cash' && (
                  <div>
                    <label className="block text-sm text-slate-400 mb-2">Payout ${payoutAmount}</label>
                    <input type="range" min="1" max="50" value={payoutAmount} onChange={(e) => setPayoutAmount(Number(e.target.value))} className="w-full" />
                  </div>
                )}
              </>
            )}

            <button onClick={calculate} disabled={loading}
              className="w-full px-6 py-3 bg-gradient-to-r from-yellow-500 to-orange-600 text-white rounded-lg font-semibold disabled:opacity-50">
              {loading ? 'Calculating...' : 'Calculate Price'}
            </button>
          </div>

          {/* Result */}
          <div className="lg:col-span-2">
            {result ? (
              <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-12 border border-slate-700 text-center">
                <p className="text-slate-400 text-sm mb-2">{exoticType.charAt(0).toUpperCase() + exoticType.slice(1)} Option Price</p>
                <p className="text-7xl font-bold text-orange-400 mb-4">${result.price.toFixed(4)}</p>
                <p className="text-slate-300">Path-dependent exotic option using Monte Carlo</p>
              </div>
            ) : (
              <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-12 border border-slate-700 text-center">
                <Sparkles className="w-16 h-16 mx-auto mb-4 text-slate-600" />
                <p className="text-slate-400">Select option type and parameters, then calculate</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
