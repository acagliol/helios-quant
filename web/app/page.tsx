'use client';

import { useState, useEffect } from 'react';
import {
  TrendingUp,
  DollarSign,
  Activity,
  PieChart,
  BarChart3,
  LineChart as LineChartIcon,
  RefreshCw,
  Play
} from 'lucide-react';
import {
  BarChart,
  Bar,
  PieChart as RechartsPie,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Area,
  AreaChart
} from 'recharts';

interface SimulationResult {
  mean: number;
  std_dev: number;
  percentile: number[];
  iterations: number;
}


const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

export default function Dashboard() {
  const [simulationData, setSimulationData] = useState<SimulationResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [apiStatus, setApiStatus] = useState<'checking' | 'online' | 'offline'>('checking');

  // Check API health
  useEffect(() => {
    checkApiHealth();
  }, []);

  const checkApiHealth = async () => {
    try {
      const response = await fetch('/api/health');
      const data = await response.json();
      if (data.status === 'healthy') {
        setApiStatus('online');
      } else {
        setApiStatus('offline');
      }
    } catch {
      setApiStatus('offline');
    }
  };

  const runMonteCarloSimulation = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/simulate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          iterations: 10000,
          mean: 0.12,
          std_dev: 0.08,
          jobs: 4
        })
      });
      const data = await response.json();
      setSimulationData(data);
    } catch (error) {
      console.error('Simulation error:', error);
    } finally {
      setLoading(false);
    }
  };

  // Sample portfolio data for visualization
  const samplePortfolios = [
    { sector: 'Technology', irr: 0.245, nav: 180, volatility: 0.28 },
    { sector: 'Healthcare', irr: 0.185, nav: 115, volatility: 0.22 },
    { sector: 'Energy', irr: 0.165, nav: 195, volatility: 0.32 },
    { sector: 'Consumer', irr: 0.215, nav: 92, volatility: 0.25 },
    { sector: 'Finance', irr: 0.125, nav: 210, volatility: 0.35 },
  ];

  const performanceData = [
    { year: '2020', portfolio: 8.5, benchmark: 7.2 },
    { year: '2021', portfolio: 15.3, benchmark: 12.8 },
    { year: '2022', portfolio: -5.2, benchmark: -8.1 },
    { year: '2023', portfolio: 18.7, benchmark: 15.4 },
    { year: '2024', portfolio: 21.5, benchmark: 18.2 },
  ];

  const distributionData = simulationData?.percentile
    ? [
        { name: 'P5', value: simulationData.percentile[0] * 100 },
        { name: 'P25', value: simulationData.percentile[1] * 100 },
        { name: 'P50', value: simulationData.percentile[2] * 100 },
        { name: 'P75', value: simulationData.percentile[3] * 100 },
        { name: 'P95', value: simulationData.percentile[4] * 100 },
      ]
    : [];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
      {/* Header */}
      <header className="border-b border-slate-800 bg-slate-900/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                <TrendingUp className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white">Helios Quant Framework</h1>
                <p className="text-sm text-slate-400">Multi-Language Quantitative Analytics Platform</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <a
                href="/portfolio"
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg transition-all flex items-center gap-2"
              >
                <PieChart className="w-4 h-4" />
                Manage Portfolio
              </a>
              <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-800">
                <div className={`w-2 h-2 rounded-full ${
                  apiStatus === 'online' ? 'bg-green-500 animate-pulse' :
                  apiStatus === 'offline' ? 'bg-red-500' :
                  'bg-yellow-500 animate-pulse'
                }`} />
                <span className="text-xs text-slate-300">
                  {apiStatus === 'online' ? 'API Online' :
                   apiStatus === 'offline' ? 'API Offline' :
                   'Checking...'}
                </span>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-6 py-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-slate-700 hover:border-blue-500 transition-all">
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 bg-blue-500/20 rounded-lg flex items-center justify-center">
                <DollarSign className="w-6 h-6 text-blue-400" />
              </div>
            </div>
            <div className="space-y-1">
              <p className="text-slate-400 text-sm">Total AUM</p>
              <p className="text-3xl font-bold text-white">$575M</p>
              <p className="text-green-400 text-sm flex items-center gap-1">
                <TrendingUp className="w-4 h-4" />
                +12.5% YTD
              </p>
            </div>
          </div>

          <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-slate-700 hover:border-green-500 transition-all">
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 bg-green-500/20 rounded-lg flex items-center justify-center">
                <Activity className="w-6 h-6 text-green-400" />
              </div>
            </div>
            <div className="space-y-1">
              <p className="text-slate-400 text-sm">Average IRR</p>
              <p className="text-3xl font-bold text-white">18.7%</p>
              <p className="text-green-400 text-sm">Across 5 funds</p>
            </div>
          </div>

          <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-slate-700 hover:border-purple-500 transition-all">
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 bg-purple-500/20 rounded-lg flex items-center justify-center">
                <BarChart3 className="w-6 h-6 text-purple-400" />
              </div>
            </div>
            <div className="space-y-1">
              <p className="text-slate-400 text-sm">Sharpe Ratio</p>
              <p className="text-3xl font-bold text-white">1.42</p>
              <p className="text-slate-400 text-sm">Risk-adjusted</p>
            </div>
          </div>

          <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-slate-700 hover:border-orange-500 transition-all">
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 bg-orange-500/20 rounded-lg flex items-center justify-center">
                <LineChartIcon className="w-6 h-6 text-orange-400" />
              </div>
            </div>
            <div className="space-y-1">
              <p className="text-slate-400 text-sm">Volatility</p>
              <p className="text-3xl font-bold text-white">27.4%</p>
              <p className="text-slate-400 text-sm">Annualized</p>
            </div>
          </div>
        </div>

        {/* Monte Carlo Simulation Section */}
        <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-slate-700 mb-8">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-xl font-bold text-white flex items-center gap-2">
                <Activity className="w-5 h-5 text-blue-400" />
                Monte Carlo Simulation
              </h2>
              <p className="text-sm text-slate-400 mt-1">Parallel portfolio return simulation (10,000 iterations)</p>
            </div>
            <button
              onClick={runMonteCarloSimulation}
              disabled={loading || apiStatus !== 'online'}
              className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg hover:from-blue-600 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              {loading ? (
                <RefreshCw className="w-5 h-5 animate-spin" />
              ) : (
                <Play className="w-5 h-5" />
              )}
              {loading ? 'Running...' : 'Run Simulation'}
            </button>
          </div>

          {simulationData && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-slate-900/50 rounded-lg p-4 border border-slate-700">
                    <p className="text-slate-400 text-sm mb-1">Mean Return</p>
                    <p className="text-2xl font-bold text-white">{(simulationData.mean * 100).toFixed(2)}%</p>
                  </div>
                  <div className="bg-slate-900/50 rounded-lg p-4 border border-slate-700">
                    <p className="text-slate-400 text-sm mb-1">Std Deviation</p>
                    <p className="text-2xl font-bold text-white">{(simulationData.std_dev * 100).toFixed(2)}%</p>
                  </div>
                </div>
                <div className="bg-slate-900/50 rounded-lg p-4 border border-slate-700">
                  <p className="text-slate-400 text-sm mb-3">Return Distribution</p>
                  <div className="space-y-2">
                    {['5th', '25th', '50th', '75th', '95th'].map((label, idx) => (
                      <div key={label} className="flex items-center justify-between">
                        <span className="text-sm text-slate-300">{label} Percentile</span>
                        <span className="text-sm font-semibold text-white">
                          {(simulationData.percentile[idx] * 100).toFixed(2)}%
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              <div className="bg-slate-900/50 rounded-lg p-4 border border-slate-700">
                <p className="text-slate-400 text-sm mb-3">Percentile Distribution</p>
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={distributionData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                    <XAxis dataKey="name" stroke="#94a3b8" />
                    <YAxis stroke="#94a3b8" />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                      labelStyle={{ color: '#e2e8f0' }}
                    />
                    <Bar dataKey="value" fill="#3b82f6" radius={[8, 8, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}

          {!simulationData && !loading && (
            <div className="text-center py-12 text-slate-400">
              <Activity className="w-12 h-12 mx-auto mb-3 opacity-50" />
              <p>Click &quot;Run Simulation&quot; to see results</p>
            </div>
          )}
        </div>

        {/* Charts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Sector Performance */}
          <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-slate-700">
            <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
              <PieChart className="w-5 h-5 text-green-400" />
              Sector Performance (IRR)
            </h3>
            <ResponsiveContainer width="100%" height={300}>
              <RechartsPie>
                <Pie
                  data={samplePortfolios}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={(props) => {
                    const data = props as unknown as { sector: string; irr: number };
                    return `${data.sector}: ${(data.irr * 100).toFixed(1)}%`;
                  }}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="irr"
                >
                  {samplePortfolios.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                />
              </RechartsPie>
            </ResponsiveContainer>
          </div>

          {/* Portfolio vs Benchmark */}
          <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-slate-700">
            <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
              <LineChartIcon className="w-5 h-5 text-blue-400" />
              Portfolio vs Benchmark
            </h3>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={performanceData}>
                <defs>
                  <linearGradient id="colorPortfolio" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="colorBenchmark" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="year" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                  labelStyle={{ color: '#e2e8f0' }}
                />
                <Legend />
                <Area
                  type="monotone"
                  dataKey="portfolio"
                  stroke="#3b82f6"
                  fillOpacity={1}
                  fill="url(#colorPortfolio)"
                  strokeWidth={2}
                />
                <Area
                  type="monotone"
                  dataKey="benchmark"
                  stroke="#10b981"
                  fillOpacity={1}
                  fill="url(#colorBenchmark)"
                  strokeWidth={2}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          {/* Risk-Return Profile */}
          <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-slate-700">
            <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-purple-400" />
              Risk-Return Profile
            </h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={samplePortfolios}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="sector" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                  labelStyle={{ color: '#e2e8f0' }}
                />
                <Legend />
                <Bar dataKey="irr" fill="#8b5cf6" name="IRR" radius={[8, 8, 0, 0]} />
                <Bar dataKey="volatility" fill="#ef4444" name="Volatility" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* NAV by Sector */}
          <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-slate-700">
            <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
              <DollarSign className="w-5 h-5 text-green-400" />
              NAV by Sector ($M)
            </h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={samplePortfolios} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis type="number" stroke="#94a3b8" />
                <YAxis dataKey="sector" type="category" stroke="#94a3b8" />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                  labelStyle={{ color: '#e2e8f0' }}
                />
                <Bar dataKey="nav" fill="#10b981" radius={[0, 8, 8, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Tech Stack Info */}
        <div className="mt-8 bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-slate-700">
          <h3 className="text-lg font-bold text-white mb-4">Technology Stack</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-slate-900/50 rounded-lg p-4 border border-slate-700">
              <p className="text-blue-400 font-semibold mb-1">Go</p>
              <p className="text-xs text-slate-400">Backend API & Monte Carlo</p>
            </div>
            <div className="bg-slate-900/50 rounded-lg p-4 border border-slate-700">
              <p className="text-green-400 font-semibold mb-1">R</p>
              <p className="text-xs text-slate-400">Statistical Analysis</p>
            </div>
            <div className="bg-slate-900/50 rounded-lg p-4 border border-slate-700">
              <p className="text-yellow-400 font-semibold mb-1">Python</p>
              <p className="text-xs text-slate-400">ML & QuantLib</p>
            </div>
            <div className="bg-slate-900/50 rounded-lg p-4 border border-slate-700">
              <p className="text-purple-400 font-semibold mb-1">Next.js</p>
              <p className="text-xs text-slate-400">Web Dashboard</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
