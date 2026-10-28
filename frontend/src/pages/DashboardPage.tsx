import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { 
  Trash2, 
  Download, 
  FileText, 
  Calendar,
  Lock,
  ArrowRight,
  ShieldCheck
} from 'lucide-react';
import { api } from '../services/api';
import { AnalysisHistoryItem, UserStats } from '../types';
import { useAuth } from '../contexts/AuthContext';

export const DashboardPage: React.FC = () => {
  const { user, isAuthenticated, isLoading: isAuthLoading } = useAuth();

  const [history, setHistory] = useState<AnalysisHistoryItem[]>([]);
  const [stats, setStats] = useState<UserStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<number | null>(null);

  const fetchDashboardData = async () => {
    if (!isAuthenticated) return;
    setIsLoading(true);
    setError(null);
    try {
      const [historyData, statsData] = await Promise.all([
        api.getAnalysisHistory(),
        api.getUserStats(),
      ]);
      setHistory(historyData);
      setStats(statsData);
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to load dashboard data from database.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (isAuthenticated) {
      fetchDashboardData();
    }
  }, [isAuthenticated]);

  const handleDeleteHistory = async (id: number) => {
    if (!window.confirm('Are you sure you want to delete this analysis record? This action cannot be undone.')) {
      return;
    }
    setDeletingId(id);
    try {
      await api.deleteAnalysis(id);
      setHistory((prev) => prev.filter((item) => item.id !== id));
      if (stats) {
        setStats({
          ...stats,
          total_analyses: Math.max(0, stats.total_analyses - 1),
        });
      }
    } catch {
      alert('Failed to delete analysis record.');
    } finally {
      setDeletingId(null);
    }
  };

  const handleDownloadPdf = async (id: number) => {
    try {
      const blob = await api.downloadReportPdf(id);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `codewithanil-analysis-${id}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch {
      alert('Failed to download report.');
    }
  };

  // If user is not authenticated, show sign-in callout
  if (!isAuthLoading && !isAuthenticated) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-16 text-center space-y-6">
        <div className="w-16 h-16 rounded-2xl bg-electric-500/10 border border-electric-500/20 text-electric-400 flex items-center justify-center mx-auto">
          <Lock className="w-8 h-8" />
        </div>
        <h2 className="text-2xl font-bold text-white">Private User Dashboard</h2>
        <p className="text-sm text-slate-400 max-w-md mx-auto">
          Create a free account or sign in to track your personal analysis history, view real database metrics, and export audit PDF reports.
        </p>
        <div className="flex items-center justify-center gap-4 pt-2">
          <Link
            to="/login"
            className="px-6 py-2.5 rounded-xl bg-slate-800 text-slate-200 hover:text-white font-semibold text-sm border border-slate-700 transition-colors"
          >
            Sign In
          </Link>
          <Link
            to="/register"
            className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-electric-500 to-brandPurple-600 text-white font-semibold text-sm shadow-md transition-all"
          >
            Create Account
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      {/* Top Profile Bar */}
      <div className="flex flex-wrap items-center justify-between gap-4 p-6 rounded-2xl bg-navy-900/60 backdrop-blur-xl border border-slate-800 shadow-xl">
        <div className="flex items-center gap-4">
          <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-electric-500 to-brandPurple-500 flex items-center justify-center text-white font-bold text-xl shadow-lg shadow-electric-500/20">
            {user?.name?.[0]?.toUpperCase() || 'U'}
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-bold text-white">{user?.name}</h1>
              <span className="text-[11px] font-mono px-2 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
                Verified Account
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-0.5">{user?.email}</p>
            <span className="text-[10px] text-slate-500 flex items-center gap-1 mt-1">
              <Calendar className="w-3 h-3" /> Member since {user?.created_at ? new Date(user.created_at).toLocaleDateString() : 'Today'}
            </span>
          </div>
        </div>

        <Link
          to="/detector"
          className="px-4 py-2 rounded-xl text-xs font-semibold text-white bg-electric-500 hover:bg-electric-400 flex items-center gap-2 transition-colors"
        >
          <span>Run New Analysis</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </Link>
      </div>

      {/* Real Database Statistics Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-5 rounded-2xl bg-navy-900/50 border border-slate-800">
          <span className="text-xs text-slate-400 font-semibold block mb-1">TOTAL ANALYSES</span>
          <div className="text-3xl font-extrabold text-white font-mono">
            {stats ? stats.total_analyses : 0}
          </div>
          <span className="text-[11px] text-slate-500 mt-1 block">Saved in local SQLite / DB</span>
        </div>

        <div className="p-5 rounded-2xl bg-navy-900/50 border border-slate-800">
          <span className="text-xs text-brandPurple-400 font-semibold block mb-1">AI-DOMINANT SIGNALS</span>
          <div className="text-3xl font-extrabold text-brandPurple-300 font-mono">
            {stats ? stats.ai_count : 0}
          </div>
          <span className="text-[11px] text-slate-500 mt-1 block">Classified as synthetic pattern</span>
        </div>

        <div className="p-5 rounded-2xl bg-navy-900/50 border border-slate-800">
          <span className="text-xs text-emerald-400 font-semibold block mb-1">HUMAN-DOMINANT SIGNALS</span>
          <div className="text-3xl font-extrabold text-emerald-300 font-mono">
            {stats ? stats.human_count : 0}
          </div>
          <span className="text-[11px] text-slate-500 mt-1 block">Classified as human pattern</span>
        </div>

        <div className="p-5 rounded-2xl bg-navy-900/50 border border-slate-800">
          <span className="text-xs text-electric-400 font-semibold block mb-1">WORDS ANALYZED</span>
          <div className="text-3xl font-extrabold text-white font-mono">
            {stats ? stats.total_words_analyzed : 0}
          </div>
          <span className="text-[11px] text-slate-500 mt-1 block">Total tokens processed</span>
        </div>
      </div>

      {/* Recent Analysis History Table */}
      <div className="rounded-2xl bg-navy-900/50 backdrop-blur-xl border border-slate-800 p-6 space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <FileText className="w-4 h-4 text-electric-400" />
              Analysis History & Audit Reports
            </h3>
            <p className="text-xs text-slate-400">
              Only submissions you explicitly chose to save are stored in the database.
            </p>
          </div>
        </div>

        {error && (
          <div className="p-3 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 text-xs">
            {error}
          </div>
        )}

        {isLoading ? (
          <div className="py-12 text-center text-slate-400 text-xs">
            <div className="w-5 h-5 border-2 border-electric-400 border-t-transparent rounded-full animate-spin mx-auto mb-2" />
            Loading records from database...
          </div>
        ) : history.length === 0 ? (
          <div className="py-12 text-center rounded-xl bg-navy-950 border border-slate-800/80 space-y-2">
            <ShieldCheck className="w-8 h-8 text-slate-600 mx-auto" />
            <p className="text-xs text-slate-400">No saved analyses yet.</p>
            <p className="text-[11px] text-slate-500">
              When analyzing text or documents, check "Save to my dashboard history" to archive them here.
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-navy-950/80 text-slate-400 uppercase font-mono text-[10px] border-b border-slate-800">
                <tr>
                  <th className="p-3">Snippet</th>
                  <th className="p-3">Classification</th>
                  <th className="p-3">AI Score</th>
                  <th className="p-3">Length</th>
                  <th className="p-3">Date</th>
                  <th className="p-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {history.map((item) => (
                  <tr key={item.id} className="hover:bg-slate-800/30 transition-colors">
                    <td className="p-3 max-w-xs truncate text-slate-200 font-sans" title={item.snippet}>
                      {item.snippet}
                    </td>
                    <td className="p-3">
                      <span className={`px-2 py-0.5 rounded-full font-mono text-[10px] border ${
                        item.prediction === 'AI-Generated'
                          ? 'bg-purple-500/10 border-purple-500/30 text-brandPurple-300'
                          : item.prediction === 'Inconclusive'
                          ? 'bg-amber-500/10 border-amber-500/30 text-amber-300'
                          : 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'
                      }`}>
                        {item.prediction}
                      </span>
                    </td>
                    <td className="p-3 font-mono font-bold text-slate-200">
                      {Math.round(item.model_score * 100)}%
                    </td>
                    <td className="p-3 text-slate-400 font-mono">
                      {item.word_count} words
                    </td>
                    <td className="p-3 text-slate-500 whitespace-nowrap">
                      {new Date(item.created_at).toLocaleDateString()}
                    </td>
                    <td className="p-3 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={() => handleDownloadPdf(item.id)}
                          className="p-1.5 rounded hover:bg-slate-800 text-electric-400 hover:text-electric-300 transition-colors"
                          title="Download PDF Audit Report"
                        >
                          <Download className="w-3.5 h-3.5" />
                        </button>
                        <button
                          onClick={() => handleDeleteHistory(item.id)}
                          disabled={deletingId === item.id}
                          className="p-1.5 rounded hover:bg-red-500/10 text-slate-500 hover:text-red-400 transition-colors"
                          title="Delete record"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
