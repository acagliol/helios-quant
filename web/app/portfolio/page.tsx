'use client';

import { useState } from 'react';
import Link from 'next/link';
import {
  Plus,
  Trash2,
  Edit2,
  Download,
  Upload,
  Save,
  X,
  Search,
  Filter,
  ArrowUpDown,
  TrendingUp,
  FileSpreadsheet
} from 'lucide-react';
import Papa from 'papaparse';

interface Fund {
  id: string;
  fund_name: string;
  vintage: number;
  sector: string;
  committed_capital: number;
  invested_capital: number;
  current_nav: number;
  irr: number;
  moic: number;
  tvpi: number;
  dpi: number;
  benchmark_return: number;
  volatility: number;
  status: string;
}

const SECTORS = ['Technology', 'Healthcare', 'Energy', 'Consumer', 'Finance', 'Industrial', 'Real Estate'];
const STATUSES = ['Active', 'Realized', 'Written-Off'];

export default function PortfolioManagement() {
  const [funds, setFunds] = useState<Fund[]>([
    {
      id: '1',
      fund_name: 'Tech Growth Fund I',
      vintage: 2018,
      sector: 'Technology',
      committed_capital: 100000000,
      invested_capital: 95000000,
      current_nav: 180000000,
      irr: 0.2450,
      moic: 1.89,
      tvpi: 1.95,
      dpi: 0.50,
      benchmark_return: 0.1200,
      volatility: 0.2800,
      status: 'Active'
    },
    {
      id: '2',
      fund_name: 'Healthcare Ventures II',
      vintage: 2019,
      sector: 'Healthcare',
      committed_capital: 75000000,
      invested_capital: 72000000,
      current_nav: 115000000,
      irr: 0.1850,
      moic: 1.60,
      tvpi: 1.72,
      dpi: 0.35,
      benchmark_return: 0.0950,
      volatility: 0.2200,
      status: 'Active'
    },
    {
      id: '3',
      fund_name: 'Energy Transition Fund',
      vintage: 2020,
      sector: 'Energy',
      committed_capital: 150000000,
      invested_capital: 130000000,
      current_nav: 195000000,
      irr: 0.1650,
      moic: 1.50,
      tvpi: 1.63,
      dpi: 0.28,
      benchmark_return: 0.0850,
      volatility: 0.3200,
      status: 'Active'
    },
  ]);

  const [editingId, setEditingId] = useState<string | null>(null);
  const [editForm, setEditForm] = useState<Fund | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterSector, setFilterSector] = useState('All');
  const [sortField, setSortField] = useState<keyof Fund>('fund_name');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');

  const handleEdit = (fund: Fund) => {
    setEditingId(fund.id);
    setEditForm({ ...fund });
  };

  const handleSave = () => {
    if (editForm) {
      setFunds(funds.map(f => f.id === editForm.id ? editForm : f));
      setEditingId(null);
      setEditForm(null);
    }
  };

  const handleCancel = () => {
    setEditingId(null);
    setEditForm(null);
  };

  const handleDelete = (id: string) => {
    if (confirm('Are you sure you want to delete this fund?')) {
      setFunds(funds.filter(f => f.id !== id));
    }
  };

  const handleAdd = () => {
    const newFund: Fund = {
      id: Date.now().toString(),
      fund_name: 'New Fund',
      vintage: new Date().getFullYear(),
      sector: 'Technology',
      committed_capital: 0,
      invested_capital: 0,
      current_nav: 0,
      irr: 0,
      moic: 0,
      tvpi: 0,
      dpi: 0,
      benchmark_return: 0,
      volatility: 0,
      status: 'Active'
    };
    setFunds([...funds, newFund]);
    setEditingId(newFund.id);
    setEditForm(newFund);
  };

  const handleExportCSV = () => {
    const csv = Papa.unparse(funds);
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `portfolio_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
  };

  const handleImportCSV = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      Papa.parse<Record<string, string>>(file, {
        header: true,
        complete: (results) => {
          const importedFunds = results.data.map((row, index) => ({
            id: (Date.now() + index).toString(),
            fund_name: row.fund_name || '',
            vintage: parseInt(row.vintage) || new Date().getFullYear(),
            sector: row.sector || 'Technology',
            committed_capital: parseFloat(row.committed_capital) || 0,
            invested_capital: parseFloat(row.invested_capital) || 0,
            current_nav: parseFloat(row.current_nav) || 0,
            irr: parseFloat(row.irr) || 0,
            moic: parseFloat(row.moic) || 0,
            tvpi: parseFloat(row.tvpi) || 0,
            dpi: parseFloat(row.dpi) || 0,
            benchmark_return: parseFloat(row.benchmark_return) || 0,
            volatility: parseFloat(row.volatility) || 0,
            status: row.status || 'Active'
          }));
          setFunds([...funds, ...importedFunds.filter(f => f.fund_name)]);
        }
      });
    }
  };

  const handleSort = (field: keyof Fund) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  const filteredAndSortedFunds = funds
    .filter(f =>
      (filterSector === 'All' || f.sector === filterSector) &&
      (f.fund_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
       f.sector.toLowerCase().includes(searchTerm.toLowerCase()))
    )
    .sort((a, b) => {
      const aVal = a[sortField];
      const bVal = b[sortField];
      const modifier = sortDirection === 'asc' ? 1 : -1;
      return aVal > bVal ? modifier : -modifier;
    });

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  const formatPercent = (value: number) => {
    return `${(value * 100).toFixed(2)}%`;
  };

  const totalAUM = funds.reduce((sum, f) => sum + f.current_nav, 0);
  const avgIRR = funds.reduce((sum, f) => sum + f.irr, 0) / funds.length;
  const totalCommitted = funds.reduce((sum, f) => sum + f.committed_capital, 0);

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
                <h1 className="text-2xl font-bold text-white">Portfolio Management</h1>
                <p className="text-sm text-slate-400">Manage your investment funds</p>
              </div>
            </div>
            <Link href="/" className="text-sm text-slate-400 hover:text-white transition-colors">
              ← Back to Dashboard
            </Link>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-6 py-8">
        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-slate-700">
            <p className="text-slate-400 text-sm mb-2">Total Funds</p>
            <p className="text-3xl font-bold text-white">{funds.length}</p>
          </div>
          <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-slate-700">
            <p className="text-slate-400 text-sm mb-2">Total AUM</p>
            <p className="text-3xl font-bold text-white">{formatCurrency(totalAUM / 1000000)}M</p>
          </div>
          <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-slate-700">
            <p className="text-slate-400 text-sm mb-2">Avg IRR</p>
            <p className="text-3xl font-bold text-white">{formatPercent(avgIRR)}</p>
          </div>
          <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-slate-700">
            <p className="text-slate-400 text-sm mb-2">Total Committed</p>
            <p className="text-3xl font-bold text-white">{formatCurrency(totalCommitted / 1000000)}M</p>
          </div>
        </div>

        {/* Toolbar */}
        <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-slate-700 mb-8">
          <div className="flex flex-col lg:flex-row gap-4 justify-between">
            <div className="flex flex-col sm:flex-row gap-4 flex-1">
              {/* Search */}
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                <input
                  type="text"
                  placeholder="Search funds..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              {/* Sector Filter */}
              <div className="relative">
                <Filter className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                <select
                  value={filterSector}
                  onChange={(e) => setFilterSector(e.target.value)}
                  className="pl-10 pr-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="All">All Sectors</option>
                  {SECTORS.map(sector => (
                    <option key={sector} value={sector}>{sector}</option>
                  ))}
                </select>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-2">
              <button
                onClick={handleAdd}
                className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg hover:from-blue-600 hover:to-purple-700 transition-all"
              >
                <Plus className="w-5 h-5" />
                Add Fund
              </button>
              <label className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-all cursor-pointer">
                <Upload className="w-5 h-5" />
                Import CSV
                <input
                  type="file"
                  accept=".csv"
                  onChange={handleImportCSV}
                  className="hidden"
                />
              </label>
              <button
                onClick={handleExportCSV}
                className="flex items-center gap-2 px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-all"
              >
                <Download className="w-5 h-5" />
                Export
              </button>
              <a
                href="/portfolio_template.csv"
                download
                className="flex items-center gap-2 px-4 py-2 bg-slate-700 text-white rounded-lg hover:bg-slate-600 transition-all"
              >
                <FileSpreadsheet className="w-5 h-5" />
                Template
              </a>
            </div>
          </div>
        </div>

        {/* Table */}
        <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl border border-slate-700 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-slate-900/50">
                <tr>
                  {[
                    { key: 'fund_name', label: 'Fund Name' },
                    { key: 'vintage', label: 'Vintage' },
                    { key: 'sector', label: 'Sector' },
                    { key: 'committed_capital', label: 'Committed ($M)' },
                    { key: 'current_nav', label: 'NAV ($M)' },
                    { key: 'irr', label: 'IRR' },
                    { key: 'moic', label: 'MOIC' },
                    { key: 'tvpi', label: 'TVPI' },
                    { key: 'status', label: 'Status' },
                  ].map(({ key, label }) => (
                    <th
                      key={key}
                      onClick={() => handleSort(key as keyof Fund)}
                      className="px-6 py-4 text-left text-sm font-semibold text-slate-300 cursor-pointer hover:text-white transition-colors"
                    >
                      <div className="flex items-center gap-2">
                        {label}
                        <ArrowUpDown className="w-4 h-4" />
                      </div>
                    </th>
                  ))}
                  <th className="px-6 py-4 text-left text-sm font-semibold text-slate-300">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-700">
                {filteredAndSortedFunds.map((fund) => (
                  <tr key={fund.id} className="hover:bg-slate-900/30 transition-colors">
                    {editingId === fund.id && editForm ? (
                      <>
                        <td className="px-6 py-4">
                          <input
                            type="text"
                            value={editForm.fund_name}
                            onChange={(e) => setEditForm({ ...editForm, fund_name: e.target.value })}
                            className="w-full px-2 py-1 bg-slate-900 border border-slate-700 rounded text-white text-sm"
                          />
                        </td>
                        <td className="px-6 py-4">
                          <input
                            type="number"
                            value={editForm.vintage}
                            onChange={(e) => setEditForm({ ...editForm, vintage: parseInt(e.target.value) })}
                            className="w-20 px-2 py-1 bg-slate-900 border border-slate-700 rounded text-white text-sm"
                          />
                        </td>
                        <td className="px-6 py-4">
                          <select
                            value={editForm.sector}
                            onChange={(e) => setEditForm({ ...editForm, sector: e.target.value })}
                            className="px-2 py-1 bg-slate-900 border border-slate-700 rounded text-white text-sm"
                          >
                            {SECTORS.map(sector => (
                              <option key={sector} value={sector}>{sector}</option>
                            ))}
                          </select>
                        </td>
                        <td className="px-6 py-4">
                          <input
                            type="number"
                            value={editForm.committed_capital / 1000000}
                            onChange={(e) => setEditForm({ ...editForm, committed_capital: parseFloat(e.target.value) * 1000000 })}
                            className="w-24 px-2 py-1 bg-slate-900 border border-slate-700 rounded text-white text-sm"
                          />
                        </td>
                        <td className="px-6 py-4">
                          <input
                            type="number"
                            value={editForm.current_nav / 1000000}
                            onChange={(e) => setEditForm({ ...editForm, current_nav: parseFloat(e.target.value) * 1000000 })}
                            className="w-24 px-2 py-1 bg-slate-900 border border-slate-700 rounded text-white text-sm"
                          />
                        </td>
                        <td className="px-6 py-4">
                          <input
                            type="number"
                            step="0.01"
                            value={editForm.irr * 100}
                            onChange={(e) => setEditForm({ ...editForm, irr: parseFloat(e.target.value) / 100 })}
                            className="w-20 px-2 py-1 bg-slate-900 border border-slate-700 rounded text-white text-sm"
                          />
                        </td>
                        <td className="px-6 py-4">
                          <input
                            type="number"
                            step="0.01"
                            value={editForm.moic}
                            onChange={(e) => setEditForm({ ...editForm, moic: parseFloat(e.target.value) })}
                            className="w-20 px-2 py-1 bg-slate-900 border border-slate-700 rounded text-white text-sm"
                          />
                        </td>
                        <td className="px-6 py-4">
                          <input
                            type="number"
                            step="0.01"
                            value={editForm.tvpi}
                            onChange={(e) => setEditForm({ ...editForm, tvpi: parseFloat(e.target.value) })}
                            className="w-20 px-2 py-1 bg-slate-900 border border-slate-700 rounded text-white text-sm"
                          />
                        </td>
                        <td className="px-6 py-4">
                          <select
                            value={editForm.status}
                            onChange={(e) => setEditForm({ ...editForm, status: e.target.value })}
                            className="px-2 py-1 bg-slate-900 border border-slate-700 rounded text-white text-sm"
                          >
                            {STATUSES.map(status => (
                              <option key={status} value={status}>{status}</option>
                            ))}
                          </select>
                        </td>
                        <td className="px-6 py-4">
                          <div className="flex gap-2">
                            <button
                              onClick={handleSave}
                              className="p-2 bg-green-600 text-white rounded hover:bg-green-700 transition-colors"
                            >
                              <Save className="w-4 h-4" />
                            </button>
                            <button
                              onClick={handleCancel}
                              className="p-2 bg-slate-600 text-white rounded hover:bg-slate-700 transition-colors"
                            >
                              <X className="w-4 h-4" />
                            </button>
                          </div>
                        </td>
                      </>
                    ) : (
                      <>
                        <td className="px-6 py-4 text-sm font-medium text-white">{fund.fund_name}</td>
                        <td className="px-6 py-4 text-sm text-slate-300">{fund.vintage}</td>
                        <td className="px-6 py-4">
                          <span className="px-2 py-1 text-xs font-semibold rounded-full bg-blue-500/20 text-blue-400">
                            {fund.sector}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-sm text-slate-300">{(fund.committed_capital / 1000000).toFixed(1)}</td>
                        <td className="px-6 py-4 text-sm text-slate-300">{(fund.current_nav / 1000000).toFixed(1)}</td>
                        <td className="px-6 py-4 text-sm font-semibold text-green-400">{formatPercent(fund.irr)}</td>
                        <td className="px-6 py-4 text-sm text-slate-300">{fund.moic.toFixed(2)}x</td>
                        <td className="px-6 py-4 text-sm text-slate-300">{fund.tvpi.toFixed(2)}x</td>
                        <td className="px-6 py-4">
                          <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                            fund.status === 'Active' ? 'bg-green-500/20 text-green-400' :
                            fund.status === 'Realized' ? 'bg-blue-500/20 text-blue-400' :
                            'bg-red-500/20 text-red-400'
                          }`}>
                            {fund.status}
                          </span>
                        </td>
                        <td className="px-6 py-4">
                          <div className="flex gap-2">
                            <button
                              onClick={() => handleEdit(fund)}
                              className="p-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
                            >
                              <Edit2 className="w-4 h-4" />
                            </button>
                            <button
                              onClick={() => handleDelete(fund.id)}
                              className="p-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </div>
                        </td>
                      </>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {filteredAndSortedFunds.length === 0 && (
            <div className="text-center py-12 text-slate-400">
              <FileSpreadsheet className="w-12 h-12 mx-auto mb-3 opacity-50" />
              <p>No funds found. Add a fund or adjust your filters.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
