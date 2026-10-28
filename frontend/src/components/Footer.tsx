import React from 'react';
import { Link } from 'react-router-dom';
import { ShieldCheck, Cpu, Lock, AlertCircle } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer className="border-t border-slate-800/80 bg-navy-950/90 text-slate-400 text-sm mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-10">
          {/* Brand Column */}
          <div className="space-y-4 md:col-span-1">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-electric-500 to-brandPurple-500 flex items-center justify-center">
                <ShieldCheck className="w-4 h-4 text-white" />
              </div>
              <span className="font-bold text-lg text-white">CodeWithAnil</span>
            </div>
            <p className="text-slate-400 text-xs leading-relaxed">
              Detect AI Writing. Analyze Text. Explore Authenticity.
              Real machine learning classification powered by PyTorch and Hugging Face Transformers.
            </p>
            <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-mono">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              Local CPU Inference Ready
            </div>
          </div>

          {/* Quick Tools */}
          <div>
            <h4 className="font-semibold text-white text-sm mb-3">Analysis Suite</h4>
            <ul className="space-y-2 text-xs">
              <li>
                <Link to="/detector" className="hover:text-electric-400 transition-colors">
                  AI Text Detector
                </Link>
              </li>
              <li>
                <Link to="/prompts" className="hover:text-electric-400 transition-colors">
                  Prompt Analyzer & Refiner
                </Link>
              </li>
              <li>
                <Link to="/documents" className="hover:text-electric-400 transition-colors">
                  Document Scanner (PDF/DOCX)
                </Link>
              </li>
              <li>
                <Link to="/dashboard" className="hover:text-electric-400 transition-colors">
                  Analysis Dashboard
                </Link>
              </li>
            </ul>
          </div>

          {/* Machine Learning & Architecture */}
          <div>
            <h4 className="font-semibold text-white text-sm mb-3">Machine Learning</h4>
            <ul className="space-y-2 text-xs">
              <li className="flex items-center gap-1.5">
                <Cpu className="w-3.5 h-3.5 text-electric-400" />
                <span>RoBERTa Transformer Base</span>
              </li>
              <li className="flex items-center gap-1.5">
                <Lock className="w-3.5 h-3.5 text-indigo-400" />
                <span>Zero Storage by Default</span>
              </li>
              <li className="flex items-center gap-1.5">
                <AlertCircle className="w-3.5 h-3.5 text-amber-400" />
                <span>Calibrated Confidence Bounds</span>
              </li>
              <li>
                <Link to="/about" className="hover:text-electric-400 transition-colors">
                  Model Card & Limitations
                </Link>
              </li>
            </ul>
          </div>

          {/* Ethics & Transparency */}
          <div>
            <h4 className="font-semibold text-white text-sm mb-3">Ethics & Transparency</h4>
            <p className="text-slate-400 text-xs leading-relaxed mb-3">
              We never fabricate percentages or claim 100% certainty. AI text classifiers are statistical estimators that must be interpreted with human oversight.
            </p>
            <div className="text-[11px] text-slate-500">
              Tested on HC3 Human-ChatGPT Corpus.
            </div>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="pt-6 border-t border-slate-800/60 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-slate-500">
          <p>© {new Date().getFullYear()} CodeWithAnil. Built for authenticity and transparency.</p>
          <div className="flex items-center gap-4">
            <Link to="/about" className="hover:text-slate-300 transition-colors">
              About & Ethics
            </Link>
            <span>•</span>
            <span className="text-slate-400 font-mono text-[11px]">v1.0.0 (PyTorch CPU)</span>
          </div>
        </div>
      </div>
    </footer>
  );
};
