import React from 'react';
import { Cpu, BookOpen, AlertCircle, FileCheck2, Scale } from 'lucide-react';
import { ModelInfoResponse } from '../types';

interface ModelTransparencyCardProps {
  modelInfo?: ModelInfoResponse | null;
}

export const ModelTransparencyCard: React.FC<ModelTransparencyCardProps> = ({ modelInfo }) => {
  return (
    <div className="rounded-2xl bg-navy-900/50 backdrop-blur-xl border border-slate-800 p-6 shadow-xl">
      <div className="flex items-center gap-3 mb-6 pb-4 border-b border-slate-800">
        <div className="p-2.5 rounded-xl bg-electric-500/10 border border-electric-500/20 text-electric-400">
          <Scale className="w-5 h-5" />
        </div>
        <div>
          <h3 className="text-lg font-bold text-white">Model Card & Ethical Transparency</h3>
          <p className="text-xs text-slate-400">
            Full documentation of the neural architecture, training provenance, and operational boundaries.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
        <div className="bg-navy-950/70 border border-slate-800/80 rounded-xl p-4">
          <div className="flex items-center gap-2 text-xs font-semibold text-slate-300 mb-1">
            <Cpu className="w-4 h-4 text-electric-400" /> Model Identifier
          </div>
          <div className="font-mono text-sm text-electric-300 font-medium">
            {modelInfo?.model_name || 'Hello-SimpleAI/chatgpt-detector-roberta'}
          </div>
          <div className="text-[11px] text-slate-500 mt-1">
            RoBERTa Sequence Classification (125M parameters)
          </div>
        </div>

        <div className="bg-navy-950/70 border border-slate-800/80 rounded-xl p-4">
          <div className="flex items-center gap-2 text-xs font-semibold text-slate-300 mb-1">
            <BookOpen className="w-4 h-4 text-brandPurple-400" /> Training Provenance
          </div>
          <div className="text-xs text-slate-200">
            HC3 Benchmark (Human ChatGPT Comparison Corpus)
          </div>
          <div className="text-[11px] text-slate-500 mt-1">
            Peer-reviewed open dataset across QA, Wikipedia, and Reddit
          </div>
        </div>

        <div className="bg-navy-950/70 border border-slate-800/80 rounded-xl p-4">
          <div className="flex items-center gap-2 text-xs font-semibold text-slate-300 mb-1">
            <FileCheck2 className="w-4 h-4 text-emerald-400" /> License & Inference
          </div>
          <div className="text-xs text-slate-200">
            Apache 2.0 / MIT Open License
          </div>
          <div className="text-[11px] text-slate-500 mt-1">
            PyTorch CPU-optimized float32 / no GPU required
          </div>
        </div>
      </div>

      {/* Known Limitations Block */}
      <div className="bg-slate-950/50 rounded-xl border border-slate-800/80 p-4">
        <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2 flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-amber-400" /> Documented System Limitations
        </h4>
        <ul className="text-xs text-slate-400 space-y-1.5 list-disc list-inside">
          <li>
            <strong>Short Inputs (&lt; 50 words):</strong> Token sample size is too limited for reliable distributional estimation.
          </li>
          <li>
            <strong>Non-Native English:</strong> Authors writing English as a second language often use more formulaic sentence structures, which may trigger elevated false positives.
          </li>
          <li>
            <strong>Adversarial Paraphrasing:</strong> Prompting techniques, homoglyph replacement, or heavy paraphrasing can intentionally degrade detection signals.
          </li>
          <li>
            <strong>No Authorship Attribution:</strong> This model estimates stylistic overlap with generative outputs; it cannot pinpoint which specific model or person created a text.
          </li>
        </ul>
      </div>
    </div>
  );
};
