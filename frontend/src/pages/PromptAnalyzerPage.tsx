import React, { useState } from 'react';
import { 
  Sparkles, 
  CheckCircle, 
  AlertTriangle, 
  Lightbulb, 
  Copy, 
  Check, 
  HelpCircle,
  TrendingUp
} from 'lucide-react';
import { api } from '../services/api';
import { PromptAnalysisResponse } from '../types';

export const PromptAnalyzerPage: React.FC = () => {
  const [promptText, setPromptText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<PromptAnalysisResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [copiedImproved, setCopiedImproved] = useState(false);

  const samplePrompts = [
    {
      label: 'Vague Prompt',
      text: 'Write a python script to parse some data and make it fast.',
    },
    {
      label: 'Well-Structured Prompt',
      text: 'You are a senior data engineer. Write a Python script using pandas and multiprocessing to parse a 2GB CSV file of server logs. Include type annotations, error handling for corrupted rows, and output the top 10 IP addresses by request volume in Markdown table format.',
    },
  ];

  const handleAnalyzePrompt = async () => {
    if (!promptText.trim()) {
      setError('Please provide a prompt to analyze.');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const data = await api.analyzePrompt(promptText);
      setResult(data);
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to evaluate prompt quality.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCopyImproved = () => {
    if (!result?.improved_prompt) return;
    navigator.clipboard.writeText(result.improved_prompt);
    setCopiedImproved(true);
    setTimeout(() => setCopiedImproved(false), 2000);
  };

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-10">
      {/* Page Title & Intro */}
      <div className="text-center max-w-3xl mx-auto space-y-3">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-brandPurple-500/10 border border-brandPurple-500/20 text-xs font-semibold text-brandPurple-400">
          <Sparkles className="w-4 h-4" /> Prompt Engineering Audit & Optimization
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-white">
          Prompt Analyzer & Refiner
        </h1>
        <p className="text-sm text-slate-400">
          Audit your AI instructions across 7 structural dimensions. Get concrete suggestions and a production-ready refactored prompt.
        </p>
      </div>

      {/* Distinction Warning Banner */}
      <div className="rounded-xl bg-slate-900/60 border border-slate-800 p-4 text-xs text-slate-400 flex items-start gap-3">
        <HelpCircle className="w-5 h-5 text-electric-400 shrink-0 mt-0.5" />
        <div>
          <strong className="text-slate-200">Domain Note: </strong>
          Prompt Quality Analysis evaluates structural completeness and clarity for Large Language Models. It is completely independent of AI authorship detection and does not predict whether the prompt itself was authored by an AI or human.
        </div>
      </div>

      {/* Input Section */}
      <div className="rounded-2xl bg-navy-900/60 backdrop-blur-xl border border-slate-800 shadow-2xl p-6 sm:p-8 space-y-6">
        <div className="flex flex-wrap items-center justify-between gap-3 text-xs">
          <span className="text-slate-400 font-medium">Try standard examples:</span>
          <div className="flex gap-2">
            {samplePrompts.map((sp, idx) => (
              <button
                key={idx}
                onClick={() => setPromptText(sp.text)}
                className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors"
              >
                {sp.label}
              </button>
            ))}
          </div>
        </div>

        <div>
          <textarea
            value={promptText}
            onChange={(e) => setPromptText(e.target.value)}
            rows={6}
            placeholder="Paste your prompt here to evaluate clarity, specificity, constraints, context, and formatting..."
            className="w-full rounded-xl bg-navy-950/90 border border-slate-800 p-4 text-sm text-slate-100 placeholder:text-slate-500 focus:outline-none focus:border-brandPurple-500 focus:ring-1 focus:ring-brandPurple-500 transition-all font-sans leading-relaxed"
          />
        </div>

        <div className="flex items-center justify-between">
          <button
            onClick={() => {
              setPromptText('');
              setResult(null);
            }}
            disabled={!promptText}
            className="text-xs text-slate-400 hover:text-slate-200 disabled:opacity-30"
          >
            Clear input
          </button>

          <button
            onClick={handleAnalyzePrompt}
            disabled={isLoading || !promptText.trim()}
            className="px-7 py-3 rounded-xl text-sm font-semibold text-white bg-gradient-to-r from-brandPurple-600 via-indigo-600 to-electric-500 hover:from-brandPurple-500 hover:to-electric-400 shadow-lg shadow-brandPurple-500/25 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 transition-all"
          >
            {isLoading ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                <span>Evaluating Prompt Rubric...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                <span>Analyze Prompt Quality</span>
              </>
            )}
          </button>
        </div>

        {error && (
          <div className="p-3 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 text-xs">
            {error}
          </div>
        )}
      </div>

      {/* Results Workspace */}
      {result && (
        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
          {/* Top Score Banner */}
          <div className="rounded-2xl bg-navy-900/60 backdrop-blur-xl border border-slate-800 p-6 shadow-xl flex flex-col sm:flex-row items-center justify-between gap-6">
            <div className="space-y-1 text-center sm:text-left">
              <span className="text-xs text-slate-400 uppercase tracking-wider font-semibold">
                Overall Prompt Quality Score
              </span>
              <h3 className="text-2xl font-bold text-white">
                {result.overall_score >= 80 ? 'Production-Ready Prompt' : result.overall_score >= 50 ? 'Moderate Prompt' : 'Underspecified Prompt'}
              </h3>
              <p className="text-xs text-slate-400 max-w-xl">
                {result.analysis_summary}
              </p>
            </div>

            <div className="flex items-center gap-3">
              <div className="w-24 h-24 rounded-full border-4 border-slate-800 flex flex-col items-center justify-center bg-navy-950 shadow-inner">
                <span className="text-3xl font-extrabold text-white font-mono">
                  {result.overall_score}
                </span>
                <span className="text-[10px] text-slate-500">/ 100</span>
              </div>
            </div>
          </div>

          {/* 7-Dimension Rubric Breakdown Grid */}
          <div className="rounded-2xl bg-navy-900/60 backdrop-blur-xl border border-slate-800 p-6 space-y-4">
            <h4 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-electric-400" /> Rubric Evaluation Dimensions
            </h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {Object.entries(result.metrics).map(([key, score]) => {
                const label = key.replace(/_/g, ' ').toUpperCase();
                return (
                  <div key={key} className="bg-navy-950/70 border border-slate-800/80 rounded-xl p-3.5">
                    <div className="flex items-center justify-between text-xs mb-1.5">
                      <span className="text-slate-300 font-semibold">{label}</span>
                      <span className={`font-mono font-bold ${
                        score >= 75 ? 'text-emerald-400' : score >= 50 ? 'text-amber-400' : 'text-red-400'
                      }`}>
                        {score}%
                      </span>
                    </div>
                    <div className="w-full bg-slate-800/80 rounded-full h-2 overflow-hidden">
                      <div
                        className={`h-full rounded-full ${
                          score >= 75 ? 'bg-emerald-500' : score >= 50 ? 'bg-amber-500' : 'bg-red-500'
                        }`}
                        style={{ width: `${score}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Strengths & Weaknesses */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Strengths */}
            <div className="rounded-2xl bg-navy-900/50 border border-slate-800 p-6 space-y-3">
              <h4 className="text-sm font-bold text-emerald-400 flex items-center gap-2">
                <CheckCircle className="w-4 h-4" /> Detected Strengths
              </h4>
              <ul className="space-y-2 text-xs text-slate-300">
                {result.strengths.length > 0 ? (
                  result.strengths.map((str, idx) => (
                    <li key={idx} className="flex items-start gap-2 bg-emerald-500/5 p-2.5 rounded-lg border border-emerald-500/10">
                      <span className="text-emerald-400 font-bold">•</span>
                      <span>{str}</span>
                    </li>
                  ))
                ) : (
                  <li className="text-slate-500 italic">No specific strengths identified in this prompt draft.</li>
                )}
              </ul>
            </div>

            {/* Weaknesses */}
            <div className="rounded-2xl bg-navy-900/50 border border-slate-800 p-6 space-y-3">
              <h4 className="text-sm font-bold text-amber-400 flex items-center gap-2">
                <AlertTriangle className="w-4 h-4" /> Identified Weaknesses
              </h4>
              <ul className="space-y-2 text-xs text-slate-300">
                {result.weaknesses.length > 0 ? (
                  result.weaknesses.map((w, idx) => (
                    <li key={idx} className="flex items-start gap-2 bg-amber-500/5 p-2.5 rounded-lg border border-amber-500/10">
                      <span className="text-amber-400 font-bold">•</span>
                      <span>{w}</span>
                    </li>
                  ))
                ) : (
                  <li className="text-slate-500 italic">Prompt is well-formed with minimal structural deficiencies.</li>
                )}
              </ul>
            </div>
          </div>

          {/* Actionable Suggestions */}
          <div className="rounded-2xl bg-navy-900/50 border border-slate-800 p-6 space-y-3">
            <h4 className="text-sm font-bold text-electric-400 flex items-center gap-2">
              <Lightbulb className="w-4 h-4" /> Improvement Suggestions
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {result.suggestions.map((sug, idx) => (
                <div key={idx} className="bg-navy-950/80 p-3 rounded-xl border border-slate-800 text-xs text-slate-300 flex items-start gap-2">
                  <span className="text-electric-400 font-bold mt-0.5">•</span>
                  <span>{sug}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Improved Prompt Version */}
          <div className="rounded-2xl bg-gradient-to-tr from-navy-900/90 to-brandPurple-950/30 border border-brandPurple-500/30 p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h4 className="text-base font-bold text-white flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-brandPurple-400" />
                  Recommended Refactored Version
                </h4>
                <p className="text-xs text-slate-400">
                  Enhanced with role persona, explicit context, formatting boundaries, and edge constraints.
                </p>
              </div>

              <button
                onClick={handleCopyImproved}
                className="px-3 py-1.5 rounded-lg bg-brandPurple-500/20 hover:bg-brandPurple-500/30 border border-brandPurple-500/40 text-brandPurple-200 text-xs font-semibold flex items-center gap-1.5 transition-colors"
              >
                {copiedImproved ? (
                  <>
                    <Check className="w-3.5 h-3.5 text-emerald-400" /> Copied!
                  </>
                ) : (
                  <>
                    <Copy className="w-3.5 h-3.5" /> Copy Refactored Prompt
                  </>
                )}
              </button>
            </div>

            <div className="p-4 rounded-xl bg-navy-950 border border-slate-800 text-sm font-mono text-slate-200 whitespace-pre-wrap leading-relaxed select-all">
              {result.improved_prompt}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
