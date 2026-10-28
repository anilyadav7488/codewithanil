import React from 'react';
import { 
  ShieldCheck, 
  Cpu, 
  BookOpen, 
  Scale,
  FileCode2
} from 'lucide-react';

export const AboutPage: React.FC = () => {
  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12 space-y-12">
      {/* Header */}
      <div className="space-y-4 text-center">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-electric-500/10 border border-electric-500/20 text-xs font-semibold text-electric-400">
          <BookOpen className="w-4 h-4" /> Technical & Ethical Architecture
        </div>
        <h1 className="text-3xl sm:text-5xl font-extrabold text-white">
          About CodeWithAnil
        </h1>
        <p className="text-sm sm:text-base text-slate-300 max-w-2xl mx-auto leading-relaxed">
          A modern, transparent, and reproducible full-stack text analysis platform designed to distinguish statistical linguistic signals with machine learning.
        </p>
      </div>

      {/* Core Mission */}
      <div className="rounded-2xl bg-navy-900/60 backdrop-blur-xl border border-slate-800 p-6 sm:p-8 space-y-4">
        <h2 className="text-xl font-bold text-white flex items-center gap-2">
          <ShieldCheck className="w-5 h-5 text-electric-400" />
          The Guiding Philosophy: Transparency Over Black Boxes
        </h2>
        <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
          Many commercial AI detectors claim 99.9% accuracy or promote themselves as definitive lie detectors. In reality, large language model detection is fundamentally a problem of statistical inference.
          CodeWithAnil was built to provide developers, educators, and authors with an honest, fully transparent alternative that runs real PyTorch neural networks locally on your machine.
        </p>
        <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
          We never simulate percentages, we never claim legal certainty, and we explicitly highlight the mathematical limitations of sequence classification.
        </p>
      </div>

      {/* Scientific Concepts Explained */}
      <div className="rounded-2xl bg-navy-900/60 backdrop-blur-xl border border-slate-800 p-6 sm:p-8 space-y-6">
        <h2 className="text-xl font-bold text-white flex items-center gap-2">
          <Cpu className="w-5 h-5 text-brandPurple-400" />
          How Transformer Classifiers Detect AI Text
        </h2>
        <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
          Modern Large Language Models (like GPT-4, Claude, or LLaMA) generate text by predicting the next most probable token given the preceding sequence. This generative process produces distinctive statistical artifacts:
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 rounded-xl bg-navy-950/80 border border-slate-800 space-y-2">
            <h4 className="font-semibold text-white text-sm text-electric-300">1. Perplexity & Token Predictability</h4>
            <p className="text-xs text-slate-400 leading-relaxed">
              Perplexity measures how surprised a language model is by a sequence of words. AI generated text typically exhibits lower perplexity because models select high-probability tokens. Human writing displays high variability and idiosyncratic phrase choices.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-navy-950/80 border border-slate-800 space-y-2">
            <h4 className="font-semibold text-white text-sm text-brandPurple-300">2. Burstiness & Sentence Variation</h4>
            <p className="text-xs text-slate-400 leading-relaxed">
              Human authors naturally alternate between short, punchy sentences and long, complex clauses. Generative AI models often produce uniformly structured sentences with consistent cadence and clause length.
            </p>
          </div>
        </div>
      </div>

      {/* Limitations & Ethical Guardrails */}
      <div className="rounded-2xl bg-amber-500/5 border border-amber-500/20 p-6 sm:p-8 space-y-4">
        <h2 className="text-xl font-bold text-amber-200 flex items-center gap-2">
          <Scale className="w-5 h-5 text-amber-400" />
          Critical Limitations You Must Know
        </h2>
        <div className="space-y-3 text-xs sm:text-sm text-amber-300/80 leading-relaxed">
          <div className="flex items-start gap-2">
            <span className="text-amber-400 font-bold">•</span>
            <span>
              <strong>Non-native English Authors:</strong> Studies show that ESL (English as a Second Language) writers frequently use more formulaic syntactic structures, which can trigger unwarranted false positives.
            </span>
          </div>
          <div className="flex items-start gap-2">
            <span className="text-amber-400 font-bold">•</span>
            <span>
              <strong>Short Excerpts:</strong> Inputs with fewer than 50 words do not provide enough token distribution context for meaningful sequence classification.
            </span>
          </div>
          <div className="flex items-start gap-2">
            <span className="text-amber-400 font-bold">•</span>
            <span>
              <strong>Academic Integrity Policy:</strong> Automated detection scores should never be used as sole disciplinary grounds. They should only serve as a starting point for pedagogical dialogue.
            </span>
          </div>
        </div>
      </div>

      {/* Tech Stack Blueprint */}
      <div className="rounded-2xl bg-navy-900/60 backdrop-blur-xl border border-slate-800 p-6 sm:p-8 space-y-4">
        <h2 className="text-xl font-bold text-white flex items-center gap-2">
          <FileCode2 className="w-5 h-5 text-teal-400" />
          Full-Stack Architectural Stack
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
          <div className="bg-navy-950 p-4 rounded-xl border border-slate-800 space-y-1">
            <strong className="text-slate-200 block text-sm">Frontend Engineering</strong>
            <p className="text-slate-400">React 18, TypeScript, Tailwind CSS, Vite, Lucide Icons, Recharts, Framer Motion</p>
          </div>
          <div className="bg-navy-950 p-4 rounded-xl border border-slate-800 space-y-1">
            <strong className="text-slate-200 block text-sm">Backend Engine</strong>
            <p className="text-slate-400">Python 3.11+, FastAPI, Uvicorn, Pydantic v2, SQLAlchemy, SlowAPI Rate Limiting</p>
          </div>
          <div className="bg-navy-950 p-4 rounded-xl border border-slate-800 space-y-1">
            <strong className="text-slate-200 block text-sm">Machine Learning Pipeline</strong>
            <p className="text-slate-400">Hugging Face Transformers, PyTorch CPU, RoBERTa sequence classifier, scikit-learn metrics</p>
          </div>
          <div className="bg-navy-950 p-4 rounded-xl border border-slate-800 space-y-1">
            <strong className="text-slate-200 block text-sm">Document & Report Generation</strong>
            <p className="text-slate-400">pypdf, python-docx, ReportLab (PDF Audit Certificates), SQLite (local) / PostgreSQL (prod)</p>
          </div>
        </div>
      </div>
    </div>
  );
};
