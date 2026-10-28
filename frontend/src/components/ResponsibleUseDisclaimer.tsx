import React from 'react';
import { ShieldAlert, BookCheck } from 'lucide-react';

export const ResponsibleUseDisclaimer: React.FC = () => {
  return (
    <div className="rounded-2xl border border-amber-500/30 bg-amber-500/5 backdrop-blur-md p-6">
      <div className="flex items-start gap-4">
        <div className="p-3 rounded-xl bg-amber-500/20 text-amber-400 shrink-0">
          <ShieldAlert className="w-6 h-6" />
        </div>
        <div className="space-y-2">
          <h4 className="text-base font-bold text-amber-200">
            Responsible Use & Academic Policy Disclaimer
          </h4>
          <p className="text-xs sm:text-sm text-amber-300/80 leading-relaxed">
            CodeWithAnil is designed as an investigative research tool to uncover stylistic and probabilistic markers in text.
            It must <strong>never</strong> be used as the sole basis for disciplinary, academic, legal, or employment actions.
            Statistical classifiers naturally exhibit false positives and false negatives. Always corroborate automated findings with holistic human judgment and open dialogue.
          </p>
          <div className="flex items-center gap-2 text-xs text-amber-400/90 font-medium pt-1">
            <BookCheck className="w-4 h-4" />
            <span>Recommended practice: Use alongside version history, revision diffs, and conversational evaluation.</span>
          </div>
        </div>
      </div>
    </div>
  );
};
