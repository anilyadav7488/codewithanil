import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { 
  ShieldCheck, 
  Sparkles, 
  FileSearch, 
  Cpu, 
  ArrowRight, 
  ChevronDown, 
  ChevronUp, 
  Zap
} from 'lucide-react';
import { ModelTransparencyCard } from '../components/ModelTransparencyCard';
import { ResponsibleUseDisclaimer } from '../components/ResponsibleUseDisclaimer';
import { api } from '../services/api';
import { TextAnalysisResponse } from '../types';

export const HomePage: React.FC = () => {
  // Interactive detector preview state
  const [previewText, setPreviewText] = useState(
    'Natural language processing enables machines to analyze, understand, and generate human language in a structured and efficient manner. By utilizing transformer architectures, neural networks learn rich contextual representations from extensive text corpora.'
  );
  const [previewResult, setPreviewResult] = useState<TextAnalysisResponse | null>(null);
  const [isLoadingPreview, setIsLoadingPreview] = useState(false);
  const [previewError, setPreviewError] = useState<string | null>(null);

  // FAQ accordion state
  const [openFaq, setOpenFaq] = useState<number | null>(0);

  const handleQuickPreviewAnalyze = async () => {
    if (!previewText.trim()) return;
    setIsLoadingPreview(true);
    setPreviewError(null);
    try {
      const data = await api.analyzeText(previewText, false, false);
      setPreviewResult(data);
    } catch (err: any) {
      setPreviewError(err?.response?.data?.detail || 'Inference service is currently initializing. Please try again in a few seconds.');
    } finally {
      setIsLoadingPreview(false);
    }
  };

  const sampleTexts = [
    {
      label: 'Sample 1 (Informational)',
      text: 'Deep neural networks with self-attention mechanisms allow sequence-to-sequence transformations that capture long-range contextual dependencies across linguistic structures.',
    },
    {
      label: 'Sample 2 (Personal Reflection)',
      text: 'Last winter, my grandmother taught me how to knead sourdough bread by hand. The kitchen smelled like warm yeast and flour dust, and we waited hours for the dough to rise in the sun.',
    },
  ];

  const faqs = [
    {
      q: 'Can any AI detector guarantee 100% accuracy?',
      a: 'No. Scientifically, AI text detection is a probabilistic classification task based on token distributions, perplexity, and linguistic burstiness. Factors like domain shifts, short lengths, or formal human writing can produce false positives. We strictly disclaim 100% claims and encourage contextual human review.',
    },
    {
      q: 'Which machine learning model powers CodeWithAnil?',
      a: 'CodeWithAnil utilizes an optimized RoBERTa sequence classification transformer checkpoint trained on the Human-ChatGPT Comparison Corpus (HC3). Inference is executed locally on CPU with zero data transmission to third-party proprietary APIs.',
    },
    {
      q: 'Does CodeWithAnil store the text I analyze?',
      a: 'By default, text submitted via the public detector is processed in-memory and immediately discarded. Registered users can choose to save their analysis records to their personal private dashboard for history and PDF report generation.',
    },
    {
      q: 'What is the Prompt Analyzer tool?',
      a: 'The Prompt Analyzer is a separate utility that assesses LLM prompts against 7 structural engineering dimensions (clarity, specificity, context, constraints, formatting, completeness, and ambiguity). It helps you formulate more effective instructions.',
    },
    {
      q: 'Can I upload full documents like PDFs or Word files?',
      a: 'Yes. Our Document Scanner extracts plain text from PDF, DOCX, and TXT files, validates structure and length, executes transformer analysis, and can export a downloadable PDF summary report.',
    },
  ];

  return (
    <div className="space-y-24 py-10 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
      {/* Hero Section */}
      <section className="relative text-center pt-8 pb-12">
        {/* Glow ambient decorations */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[350px] bg-gradient-to-r from-electric-500/20 via-brandPurple-500/15 to-pink-500/10 blur-[120px] rounded-full pointer-events-none" />

        <div className="relative z-10 max-w-4xl mx-auto space-y-6">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-slate-800/80 border border-slate-700/80 text-xs font-medium text-slate-300 shadow-inner">
            <span className="w-2 h-2 rounded-full bg-electric-400 animate-ping" />
            <span className="text-electric-300 font-semibold">Real Transformer Inference</span>
            <span className="text-slate-500">•</span>
            <span>No Simulated Percentages</span>
          </div>

          <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight text-white leading-tight">
            CodeWithAnil — <br className="hidden sm:inline" />
            <span className="bg-gradient-to-r from-electric-400 via-indigo-300 to-brandPurple-400 bg-clip-text text-transparent">
              AI Text Detector
            </span>
          </h1>

          <p className="text-lg sm:text-xl text-slate-300 max-w-2xl mx-auto leading-relaxed">
            "Analyze writing patterns and discover signals associated with AI-generated content using machine learning."
          </p>

          <div className="flex flex-wrap items-center justify-center gap-4 pt-4">
            <Link
              to="/detector"
              className="inline-flex items-center gap-2 px-7 py-3.5 rounded-xl font-semibold text-white bg-gradient-to-r from-electric-500 via-indigo-600 to-brandPurple-600 hover:from-electric-400 hover:to-brandPurple-500 shadow-xl shadow-electric-500/25 transition-all duration-200 transform hover:-translate-y-0.5"
            >
              <span>Detect AI Text</span>
              <ArrowRight className="w-4 h-4" />
            </Link>

            <a
              href="#features"
              className="inline-flex items-center gap-2 px-6 py-3.5 rounded-xl font-medium text-slate-200 bg-navy-900/80 hover:bg-slate-800 border border-slate-700/80 transition-all duration-200"
            >
              Explore Features
            </a>
          </div>
        </div>
      </section>

      {/* Interactive Quick Preview Card */}
      <section className="relative max-w-4xl mx-auto">
        <div className="rounded-2xl bg-navy-900/80 backdrop-blur-xl border border-slate-800 p-6 sm:p-8 shadow-2xl relative">
          <div className="flex flex-wrap items-center justify-between gap-4 mb-4">
            <div className="flex items-center gap-2">
              <Zap className="w-5 h-5 text-electric-400" />
              <h2 className="text-lg font-bold text-white">Interactive Detector Preview</h2>
            </div>
            <div className="flex gap-2 text-xs">
              {sampleTexts.map((st, i) => (
                <button
                  key={i}
                  onClick={() => setPreviewText(st.text)}
                  className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors"
                >
                  {st.label}
                </button>
              ))}
            </div>
          </div>

          <div className="relative mb-4">
            <textarea
              value={previewText}
              onChange={(e) => setPreviewText(e.target.value)}
              rows={4}
              className="w-full rounded-xl bg-navy-950 border border-slate-800 focus:border-electric-500 focus:ring-1 focus:ring-electric-500 text-slate-100 p-4 text-sm resize-none transition-all placeholder:text-slate-500"
              placeholder="Paste text here to run an instant preview analysis..."
            />
            <div className="text-right text-xs text-slate-500 mt-1">
              {previewText.trim().split(/\s+/).filter(Boolean).length} words | {previewText.length} characters
            </div>
          </div>

          <div className="flex items-center justify-between">
            <div className="text-xs text-slate-400">
              Evaluated with real local RoBERTa model
            </div>
            <button
              onClick={handleQuickPreviewAnalyze}
              disabled={isLoadingPreview || !previewText.trim()}
              className="px-5 py-2.5 rounded-lg text-sm font-semibold text-white bg-electric-500 hover:bg-electric-400 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 transition-all shadow-md shadow-electric-500/20"
            >
              {isLoadingPreview ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Running Inference...
                </>
              ) : (
                <>
                  <ShieldCheck className="w-4 h-4" />
                  Analyze Preview
                </>
              )}
            </button>
          </div>

          {previewError && (
            <div className="mt-4 p-3 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 text-xs">
              {previewError}
            </div>
          )}

          {previewResult && (
            <div className="mt-6 pt-6 border-t border-slate-800/80 animate-in fade-in duration-300">
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-4">
                <div className="p-3 rounded-xl bg-navy-950 border border-slate-800">
                  <span className="text-xs text-slate-500 block">Classification</span>
                  <span className={`text-base font-bold ${
                    previewResult.prediction === 'AI-Generated' ? 'text-brandPurple-400' : 'text-emerald-400'
                  }`}>
                    {previewResult.prediction}
                  </span>
                </div>
                <div className="p-3 rounded-xl bg-navy-950 border border-slate-800">
                  <span className="text-xs text-slate-500 block">AI Probability</span>
                  <span className="text-base font-bold text-brandPurple-300">
                    {Math.round(previewResult.ai_score * 100)}%
                  </span>
                </div>
                <div className="p-3 rounded-xl bg-navy-950 border border-slate-800">
                  <span className="text-xs text-slate-500 block">Processing Time</span>
                  <span className="text-base font-bold text-slate-300">
                    {previewResult.processing_time_ms} ms
                  </span>
                </div>
              </div>
              <div className="text-right">
                <Link
                  to="/detector"
                  className="text-xs font-semibold text-electric-400 hover:text-electric-300 inline-flex items-center gap-1"
                >
                  Open Full Workspace with Sentence Breakdown <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            </div>
          )}
        </div>
      </section>

      {/* Features Grid */}
      <section id="features" className="space-y-12">
        <div className="text-center space-y-3 max-w-2xl mx-auto">
          <h2 className="text-2xl sm:text-3xl font-extrabold text-white">
            Engineered for Authenticity & Rigor
          </h2>
          <p className="text-sm text-slate-400">
            A comprehensive suite for students, educators, developers, and researchers.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="p-6 rounded-2xl bg-navy-900/50 border border-slate-800 hover:border-slate-700 transition-all hover:-translate-y-1">
            <div className="w-12 h-12 rounded-xl bg-electric-500/10 border border-electric-500/20 text-electric-400 flex items-center justify-center mb-4">
              <Cpu className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-white mb-2">Real PyTorch ML Inference</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              No simulated percentages or pseudo-random heuristics. Every prediction is computed on your machine via Hugging Face Transformers.
            </p>
          </div>

          <div className="p-6 rounded-2xl bg-navy-900/50 border border-slate-800 hover:border-slate-700 transition-all hover:-translate-y-1">
            <div className="w-12 h-12 rounded-xl bg-brandPurple-500/10 border border-brandPurple-500/20 text-brandPurple-400 flex items-center justify-center mb-4">
              <Sparkles className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-white mb-2">Prompt Analyzer & Refiner</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Audit prompts across 7 foundational dimensions: clarity, specificity, constraints, formatting, and context. Improve output quality with guided feedback.
            </p>
          </div>

          <div className="p-6 rounded-2xl bg-navy-900/50 border border-slate-800 hover:border-slate-700 transition-all hover:-translate-y-1">
            <div className="w-12 h-12 rounded-xl bg-teal-500/10 border border-teal-500/20 text-teal-400 flex items-center justify-center mb-4">
              <FileSearch className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-white mb-2">Multi-Format Document Scanner</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Upload PDF, DOCX, and TXT files. Safely extract plain text without macro execution, review probabilistic signals, and export PDF audit reports.
            </p>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="space-y-12">
        <div className="text-center space-y-3 max-w-2xl mx-auto">
          <h2 className="text-2xl sm:text-3xl font-extrabold text-white">How It Works</h2>
          <p className="text-sm text-slate-400">
            Transparent four-stage pipeline from raw user input to calibrated classification.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="p-5 rounded-2xl bg-navy-900/40 border border-slate-800 relative">
            <span className="text-3xl font-extrabold text-slate-800 absolute top-4 right-4">01</span>
            <div className="w-8 h-8 rounded-lg bg-electric-500/20 text-electric-400 flex items-center justify-center font-bold text-sm mb-3">1</div>
            <h4 className="font-bold text-white text-base mb-1">Text Input & Hygiene</h4>
            <p className="text-xs text-slate-400">
              Input is sanitized, stripped of hidden control tokens, and checked against minimum token thresholds.
            </p>
          </div>

          <div className="p-5 rounded-2xl bg-navy-900/40 border border-slate-800 relative">
            <span className="text-3xl font-extrabold text-slate-800 absolute top-4 right-4">02</span>
            <div className="w-8 h-8 rounded-lg bg-indigo-500/20 text-indigo-400 flex items-center justify-center font-bold text-sm mb-3">2</div>
            <h4 className="font-bold text-white text-base mb-1">Tokenization</h4>
            <p className="text-xs text-slate-400">
              The RoBERTa BPE tokenizer parses text into subword embeddings with attention masks and position encodings.
            </p>
          </div>

          <div className="p-5 rounded-2xl bg-navy-900/40 border border-slate-800 relative">
            <span className="text-3xl font-extrabold text-slate-800 absolute top-4 right-4">03</span>
            <div className="w-8 h-8 rounded-lg bg-brandPurple-500/20 text-brandPurple-400 flex items-center justify-center font-bold text-sm mb-3">3</div>
            <h4 className="font-bold text-white text-base mb-1">Transformer Forward Pass</h4>
            <p className="text-xs text-slate-400">
              Attention heads evaluate distributional perplexity and vocabulary regularity through 12 stacked layers.
            </p>
          </div>

          <div className="p-5 rounded-2xl bg-navy-900/40 border border-slate-800 relative">
            <span className="text-3xl font-extrabold text-slate-800 absolute top-4 right-4">04</span>
            <div className="w-8 h-8 rounded-lg bg-emerald-500/20 text-emerald-400 flex items-center justify-center font-bold text-sm mb-3">4</div>
            <h4 className="font-bold text-white text-base mb-1">Calibrated Estimation</h4>
            <p className="text-xs text-slate-400">
              Softmax logit calibration classifies the piece as Human, AI-Generated, or Inconclusive with uncertainty margins.
            </p>
          </div>
        </div>
      </section>

      {/* AI Model Transparency Card */}
      <section>
        <ModelTransparencyCard />
      </section>

      {/* Frequently Asked Questions */}
      <section className="space-y-8 max-w-3xl mx-auto">
        <div className="text-center space-y-2">
          <h2 className="text-2xl sm:text-3xl font-extrabold text-white">Frequently Asked Questions</h2>
          <p className="text-xs text-slate-400">Honest answers regarding model science and limitations.</p>
        </div>

        <div className="space-y-3">
          {faqs.map((faq, index) => {
            const isOpen = openFaq === index;
            return (
              <div
                key={index}
                className="rounded-xl border border-slate-800 bg-navy-900/50 overflow-hidden transition-colors"
              >
                <button
                  onClick={() => setOpenFaq(isOpen ? null : index)}
                  className="w-full p-4 text-left flex items-center justify-between gap-4 text-sm font-semibold text-white hover:text-electric-400 transition-colors"
                >
                  <span>{faq.q}</span>
                  {isOpen ? <ChevronUp className="w-4 h-4 text-electric-400" /> : <ChevronDown className="w-4 h-4 text-slate-500" />}
                </button>
                {isOpen && (
                  <div className="p-4 pt-0 text-xs text-slate-300 leading-relaxed border-t border-slate-800/40">
                    {faq.a}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </section>

      {/* Responsible-Use Disclaimer Banner */}
      <section>
        <ResponsibleUseDisclaimer />
      </section>
    </div>
  );
};
