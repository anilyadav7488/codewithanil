import React, { useState } from 'react';
import { 
  ShieldCheck, 
  Copy, 
  Trash2, 
  ClipboardPaste, 
  AlertCircle, 
  Check, 
  Info,
  Cpu
} from 'lucide-react';
import { ScoreGauge } from '../components/ScoreGauge';
import { SentenceHighlighter } from '../components/SentenceHighlighter';
import { api } from '../services/api';
import { TextAnalysisResponse } from '../types';
import { useAuth } from '../contexts/AuthContext';

export const DetectorPage: React.FC = () => {
  const [inputText, setInputText] = useState('');
  const [includeSentences, setIncludeSentences] = useState(true);
  const [saveToHistory, setSaveToHistory] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<TextAnalysisResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  const { isAuthenticated } = useAuth();

  // Word and character count calculation
  const words = inputText.trim() ? inputText.trim().split(/\s+/).filter(Boolean).length : 0;
  const characters = inputText.length;

  const handlePaste = async () => {
    try {
      const clipText = await navigator.clipboard.readText();
      setInputText(clipText);
    } catch {
      // Fallback
      setError('Could not access clipboard. Please paste manually into the text box.');
    }
  };

  const handleCopy = () => {
    if (!inputText) return;
    navigator.clipboard.writeText(inputText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleClear = () => {
    setInputText('');
    setResult(null);
    setError(null);
  };

  const handleAnalyze = async () => {
    if (!inputText.trim()) {
      setError('Please provide text to analyze.');
      return;
    }
    if (words < 15) {
      setError('Input text is too short. Please provide at least 15 words for meaningful model feature extraction.');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const data = await api.analyzeText(
        inputText,
        includeSentences,
        saveToHistory && isAuthenticated
      );
      setResult(data);
    } catch (err: any) {
      setError(
        err?.response?.data?.detail ||
          'Failed to perform inference. Ensure the backend server and model service are running.'
      );
    } finally {
      setIsLoading(false);
    }
  };

  // Sample texts for user testing
  const loadSample = (type: 'ai' | 'human' | 'inconclusive') => {
    if (type === 'ai') {
      setInputText(
        'Furthermore, it is imperative to acknowledge that artificial intelligence systems operate by parsing immense textual repositories to discern intricate probabilistic relationships between linguistic units. Consequently, the synthetic output frequently maintains elevated structural uniformity, balanced syntactic clause structures, and lower lexical variance across extensive paragraph generations.'
      );
    } else if (type === 'human') {
      setInputText(
        'Honestly, when I first started learning how to program back in the 90s, we didn\'t have all these fancy autocompletions or stack overflow threads. My cousin gave me a crumpled printout of Turbo C++ exercises, and I spent three full evenings tracking down a missing semicolon in my nested while loop. It was frustrating as heck, but nothing beats that rush when the screen finally compiled.'
      );
    } else {
      setInputText(
        'The committee met yesterday afternoon to discuss revised municipal guidelines concerning zoning amendments. Several stakeholders submitted written comments, while department heads reviewed infrastructural dependencies. Further deliberations will continue next Tuesday.'
      );
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-10">
      {/* Page Title & Intro */}
      <div className="text-center max-w-3xl mx-auto space-y-3">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-electric-500/10 border border-electric-500/20 text-xs font-semibold text-electric-400">
          <ShieldCheck className="w-4 h-4" /> Real Transformer Detection Workspace
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-white">
          AI Text Detector
        </h1>
        <p className="text-sm text-slate-400">
          Paste text to analyze distributional patterns, perplexity cues, and sentence-level signals with local RoBERTa inference.
        </p>
      </div>

      {/* Main Detector Card */}
      <div className="rounded-2xl bg-navy-900/60 backdrop-blur-xl border border-slate-800 shadow-2xl p-6 sm:p-8 space-y-6">
        {/* Quick Sample Selectors */}
        <div className="flex flex-wrap items-center justify-between gap-3 text-xs pb-2 border-b border-slate-800">
          <span className="text-slate-400 font-medium">Load reference benchmark:</span>
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => loadSample('ai')}
              className="px-2.5 py-1 rounded-lg bg-brandPurple-500/15 border border-brandPurple-500/30 text-brandPurple-300 hover:bg-brandPurple-500/25 transition-colors font-medium"
            >
              Synthetic Style Sample
            </button>
            <button
              onClick={() => loadSample('human')}
              className="px-2.5 py-1 rounded-lg bg-emerald-500/15 border border-emerald-500/30 text-emerald-300 hover:bg-emerald-500/25 transition-colors font-medium"
            >
              Human Style Sample
            </button>
            <button
              onClick={() => loadSample('inconclusive')}
              className="px-2.5 py-1 rounded-lg bg-amber-500/15 border border-amber-500/30 text-amber-300 hover:bg-amber-500/25 transition-colors font-medium"
            >
              Neutral Formal Sample
            </button>
          </div>
        </div>

        {/* Text Area */}
        <div className="relative">
          <textarea
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            rows={10}
            placeholder="Paste or write your text here for real machine learning evaluation (minimum 15 words)..."
            className="w-full rounded-xl bg-navy-950/90 border border-slate-800 p-4 text-sm text-slate-100 placeholder:text-slate-500 focus:outline-none focus:border-electric-500 focus:ring-1 focus:ring-electric-500 transition-all font-sans leading-relaxed"
          />

          {/* Quick Action Overlay inside textarea */}
          <div className="absolute top-3 right-3 flex items-center gap-1 bg-navy-900/90 backdrop-blur border border-slate-800 rounded-lg p-1">
            <button
              onClick={handlePaste}
              className="p-1.5 rounded hover:bg-slate-800 text-slate-400 hover:text-white transition-colors"
              title="Paste from clipboard"
            >
              <ClipboardPaste className="w-4 h-4" />
            </button>
            <button
              onClick={handleCopy}
              disabled={!inputText}
              className="p-1.5 rounded hover:bg-slate-800 text-slate-400 hover:text-white disabled:opacity-30 transition-colors"
              title="Copy text"
            >
              {copied ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
            </button>
            <button
              onClick={handleClear}
              disabled={!inputText}
              className="p-1.5 rounded hover:bg-slate-800 text-slate-400 hover:text-red-400 disabled:opacity-30 transition-colors"
              title="Clear text"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Counter and Options Row */}
        <div className="flex flex-wrap items-center justify-between gap-4 text-xs">
          {/* Word and character counters */}
          <div className="flex items-center gap-4 text-slate-400 font-mono">
            <span>
              <strong className="text-slate-200">{words}</strong> words
            </span>
            <span className="text-slate-600">•</span>
            <span>
              <strong className="text-slate-200">{characters}</strong> characters
            </span>
            {words > 0 && words < 15 && (
              <span className="text-amber-400 flex items-center gap-1 font-sans">
                <AlertCircle className="w-3.5 h-3.5" /> (Recommended min: 15 words)
              </span>
            )}
          </div>

          {/* Additional Options */}
          <div className="flex items-center gap-5">
            <label className="flex items-center gap-2 cursor-pointer text-slate-300 hover:text-white">
              <input
                type="checkbox"
                checked={includeSentences}
                onChange={(e) => setIncludeSentences(e.target.checked)}
                className="rounded border-slate-700 bg-navy-950 text-electric-500 focus:ring-0"
              />
              <span>Sentence-level breakdown</span>
            </label>

            {isAuthenticated && (
              <label className="flex items-center gap-2 cursor-pointer text-slate-300 hover:text-white">
                <input
                  type="checkbox"
                  checked={saveToHistory}
                  onChange={(e) => setSaveToHistory(e.target.checked)}
                  className="rounded border-slate-700 bg-navy-950 text-brandPurple-500 focus:ring-0"
                />
                <span>Save to my dashboard history</span>
              </label>
            )}
          </div>
        </div>

        {/* Analyze Button */}
        <div className="flex justify-end pt-2">
          <button
            onClick={handleAnalyze}
            disabled={isLoading || !inputText.trim()}
            className="w-full sm:w-auto px-8 py-3.5 rounded-xl text-sm font-semibold text-white bg-gradient-to-r from-electric-500 via-indigo-600 to-brandPurple-600 hover:from-electric-400 hover:to-brandPurple-500 shadow-lg shadow-electric-500/25 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2.5 transition-all transform hover:-translate-y-0.5"
          >
            {isLoading ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                <span>Running Transformer Inference...</span>
              </>
            ) : (
              <>
                <ShieldCheck className="w-5 h-5" />
                <span>Analyze Text Authenticity</span>
              </>
            )}
          </button>
        </div>

        {/* Error notification */}
        {error && (
          <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/30 text-red-300 text-xs flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-400 shrink-0" />
            <div>
              <strong className="block font-semibold">Inference Notification:</strong>
              {error}
            </div>
          </div>
        )}
      </div>

      {/* Results Dashboard Section */}
      {result && (
        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
          <div className="flex items-center justify-between pb-2 border-b border-slate-800">
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <Cpu className="w-5 h-5 text-electric-400" />
              Model Inference Results
            </h2>
            <div className="text-xs font-mono text-slate-400">
              Model: <span className="text-slate-200">{result.model_name}</span> ({result.model_version})
            </div>
          </div>

          {/* Primary Score & Probability Gauge */}
          <ScoreGauge
            aiScore={result.ai_score}
            humanScore={result.human_score}
            prediction={result.prediction}
            isInconclusive={result.is_inconclusive}
            confidenceLevel={result.confidence_level}
            processingTimeMs={result.processing_time_ms}
            wordCount={result.word_count}
          />

          {/* Sentence-Level Breakdown */}
          {result.sentence_analyses && result.sentence_analyses.length > 0 && (
            <SentenceHighlighter
              sentences={result.sentence_analyses}
              originalText={result.input_text}
            />
          )}

          {/* Limitations and Model Guardrails */}
          <div className="rounded-2xl bg-navy-900/40 border border-slate-800 p-6 space-y-3">
            <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-2">
              <Info className="w-4 h-4 text-electric-400" /> Model Context & Operational Bounds
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs text-slate-400">
              {result.limitations.map((lim, idx) => (
                <div key={idx} className="flex items-start gap-2 bg-navy-950/60 p-3 rounded-lg border border-slate-800/60">
                  <span className="text-electric-400 font-bold">•</span>
                  <span>{lim}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
