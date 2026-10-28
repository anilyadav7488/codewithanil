import React from 'react';
import { ShieldCheck, AlertTriangle, HelpCircle, CheckCircle2 } from 'lucide-react';
import { DetectionLabel } from '../types';

interface ScoreGaugeProps {
  aiScore: number; // 0.0 - 1.0
  humanScore: number; // 0.0 - 1.0
  prediction: DetectionLabel;
  isInconclusive: boolean;
  confidenceLevel: 'Low' | 'Medium' | 'High';
  processingTimeMs: number;
  wordCount: number;
}

export const ScoreGauge: React.FC<ScoreGaugeProps> = ({
  aiScore,
  humanScore,
  prediction,
  isInconclusive,
  confidenceLevel,
  processingTimeMs,
  wordCount,
}) => {
  const aiPercentage = Math.round(aiScore * 100);
  const humanPercentage = Math.round(humanScore * 100);

  // Determine badge styling based on prediction
  const getPredictionBadge = () => {
    if (isInconclusive) {
      return {
        bg: 'bg-amber-500/10 border-amber-500/30 text-amber-400',
        icon: <HelpCircle className="w-5 h-5 text-amber-400" />,
        label: 'Inconclusive Result',
        desc: 'Model scores lie in the uncertainty margin (40% - 60%). We advise manual review.',
      };
    }
    if (prediction === 'AI-Generated') {
      return {
        bg: 'bg-purple-500/10 border-purple-500/30 text-brandPurple-400',
        icon: <AlertTriangle className="w-5 h-5 text-brandPurple-400" />,
        label: 'Likely AI-Generated Signals',
        desc: 'Statistical patterns strongly resemble synthetic language models (e.g. ChatGPT, Claude).',
      };
    }
    return {
      bg: 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400',
      icon: <CheckCircle2 className="w-5 h-5 text-emerald-400" />,
      label: 'Likely Human-Written Signals',
      desc: 'Linguistic variation and perplexity characteristics align with human authorship.',
    };
  };

  const badge = getPredictionBadge();

  return (
    <div className="rounded-2xl bg-navy-900/60 backdrop-blur-xl border border-slate-800 p-6 shadow-2xl relative overflow-hidden">
      {/* Background ambient glow */}
      <div 
        className={`absolute -top-24 -right-24 w-60 h-60 rounded-full blur-3xl opacity-20 pointer-events-none transition-colors ${
          isInconclusive 
            ? 'bg-amber-500' 
            : prediction === 'AI-Generated' 
              ? 'bg-brandPurple-500' 
              : 'bg-emerald-500'
        }`}
      />

      {/* Header status */}
      <div className="flex flex-wrap items-center justify-between gap-4 mb-6 pb-4 border-b border-slate-800/80">
        <div className="flex items-center gap-3">
          <div className={`p-2.5 rounded-xl border ${badge.bg}`}>
            {badge.icon}
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-lg font-bold text-white">{badge.label}</h3>
              <span className={`text-[11px] font-mono px-2 py-0.5 rounded-full border ${
                confidenceLevel === 'High' 
                  ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400' 
                  : confidenceLevel === 'Medium'
                  ? 'bg-sky-500/10 border-sky-500/30 text-sky-400'
                  : 'bg-amber-500/10 border-amber-500/30 text-amber-400'
              }`}>
                {confidenceLevel} Confidence
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-0.5">{badge.desc}</p>
          </div>
        </div>

        <div className="flex items-center gap-4 text-xs font-mono text-slate-400 bg-navy-950/60 px-3 py-2 rounded-lg border border-slate-800">
          <div>
            <span className="text-slate-500 block text-[10px]">INFERENCE TIME</span>
            <span className="text-slate-200 font-semibold">{processingTimeMs} ms</span>
          </div>
          <div className="w-[1px] h-6 bg-slate-800" />
          <div>
            <span className="text-slate-500 block text-[10px]">INPUT LENGTH</span>
            <span className="text-slate-200 font-semibold">{wordCount} words</span>
          </div>
        </div>
      </div>

      {/* Probability Bars */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        {/* AI-Associated Pattern Score */}
        <div className="bg-navy-950/70 border border-slate-800/80 rounded-xl p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-brandPurple-400 flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-brandPurple-500"></span>
              AI-Associated Probability
            </span>
            <span className="text-lg font-mono font-bold text-white">
              {aiPercentage}%
            </span>
          </div>
          <div className="w-full bg-slate-800/80 rounded-full h-3 overflow-hidden p-0.5">
            <div
              className="bg-gradient-to-r from-brandPurple-500 to-electric-400 h-full rounded-full transition-all duration-1000 ease-out"
              style={{ width: `${aiPercentage}%` }}
            />
          </div>
          <p className="text-[11px] text-slate-400 mt-2">
            Softmax calibrated probability of synthetic text patterns.
          </p>
        </div>

        {/* Human-Associated Pattern Score */}
        <div className="bg-navy-950/70 border border-slate-800/80 rounded-xl p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-emerald-400 flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
              Human-Associated Probability
            </span>
            <span className="text-lg font-mono font-bold text-white">
              {humanPercentage}%
            </span>
          </div>
          <div className="w-full bg-slate-800/80 rounded-full h-3 overflow-hidden p-0.5">
            <div
              className="bg-gradient-to-r from-teal-500 to-emerald-400 h-full rounded-full transition-all duration-1000 ease-out"
              style={{ width: `${humanPercentage}%` }}
            />
          </div>
          <p className="text-[11px] text-slate-400 mt-2">
            Softmax calibrated probability of human linguistic variation.
          </p>
        </div>
      </div>

      {/* Scientific Distinction Notice */}
      <div className="rounded-xl bg-slate-950/40 border border-slate-800/60 p-3 text-xs text-slate-400 flex items-start gap-2.5">
        <ShieldCheck className="w-4 h-4 text-electric-400 shrink-0 mt-0.5" />
        <div>
          <span className="font-semibold text-slate-300">Calibration Notice: </span>
          Scores represent model output calibrated over benchmark validation sets. They are probabilistic indicators, not definitive proof of authorship. High formal conformity or technical writing can elevate AI scores on human work.
        </div>
      </div>
    </div>
  );
};
