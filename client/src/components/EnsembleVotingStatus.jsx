import React from 'react';
import { Layers, CheckCircle, AlertTriangle } from 'lucide-react';

function EnsembleVotingStatus({ monitoring }) {
  // Logic placeholders for the ensemble consensus
  const activeModels = monitoring ? 9 : 0;
  const agreementRate = monitoring ? 98.4 : 0;

  return (
    <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100 h-[380px] flex flex-col transition-all hover:shadow-xl group animate-fade-in">
      <div className="flex justify-between items-start mb-6">
        <div>
          <h3 className="font-bold text-gray-800 text-lg tracking-tight">Ensemble Voting</h3>
          <p className="text-[10px] text-gray-400 font-bold uppercase tracking-widest">Decision Consensus</p>
        </div>
        <div className={`p-2 rounded-xl ${monitoring ? "bg-indigo-50 text-indigo-600 shadow-inner" : "bg-gray-50 text-gray-400"}`}>
          <Layers size={20} />
        </div>
      </div>

      <div className="flex-grow flex flex-col justify-center space-y-8">
        {/* Active Models Counter */}
        <div className="flex items-center justify-between px-2">
          <div className="flex items-center gap-3">
             <CheckCircle className={monitoring ? "text-emerald-500" : "text-gray-300"} size={22} />
             <span className="text-[11px] font-black text-gray-500 uppercase tracking-tight">Active Classifiers</span>
          </div>
          <span className="text-2xl font-black text-gray-800 tabular-nums">{activeModels}/9</span>
        </div>

        {/* Agreement Gauge */}
        <div className="px-2">
          <div className="flex justify-between text-[11px] mb-3 font-black uppercase tracking-tight">
            <span className="text-gray-400">Agreement Rate</span>
            <span className="text-indigo-600">{agreementRate}%</span>
          </div>
          <div className="w-full bg-gray-100 h-2.5 rounded-full overflow-hidden shadow-inner border border-gray-50">
            <div 
              className="bg-indigo-500 h-full transition-all duration-1000 ease-out shadow-[0_0_10px_rgba(99,102,241,0.4)]" 
              style={{ width: `${agreementRate}%` }} 
            />
          </div>
        </div>

        {/* Forensic Insight */}
        <div className={`mx-2 p-4 rounded-xl border flex items-start gap-3 transition-colors ${monitoring ? "bg-blue-50/40 border-blue-100" : "bg-gray-50 border-gray-100"}`}>
           <AlertTriangle size={18} className={`mt-0.5 ${monitoring ? "text-blue-500" : "text-gray-300"}`} />
           <p className="text-[10px] font-bold text-gray-500 leading-relaxed uppercase tracking-tight">
             {monitoring 
               ? "System stability is high. Multi-model classification consensus is verified." 
               : "Awaiting live packet stream to begin voting consensus."}
           </p>
        </div>
      </div>

      <div className="mt-auto pt-4 border-t border-gray-50 flex justify-center">
        <p className="text-[10.5px] text-gray-400 font-medium italic">
          Aggregating predictions from 9 hybrid classifiers.
        </p>
      </div>
    </div>
  );
}

export default EnsembleVotingStatus;