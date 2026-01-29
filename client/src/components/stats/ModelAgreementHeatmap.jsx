import React from "react";

/**
 * Enhanced Model Agreement Heatmap V3.0
 * Features: Unified numeric + percentage font sizing for maximum clarity.
 */
const MODEL_LABELS = {
  RandomForest: "Random Forest",
  GradientBoosting: "Gradient Boost",
  DecisionTree: "Decision Tree",
  LightGBM: "LightGBM",
  XGBoost: "XGBoost",
  KNN: "KNN",
  MLP: "MLP",
  NaiveBayes: "Naive Bayes",
  LogisticRegression: "Log Reg",
};

function ModelAgreementHeatmap({ data, theme = 'light' }) {
  
  // 🔹 Dashboard Shadow Architecture
  const containerStyle = theme === 'light' 
    ? "bg-white border-slate-100 shadow-[0_20px_50px_rgba(79,70,229,0.08)] shadow-indigo-100/40 text-slate-800"
    : "bg-slate-900 border-slate-800 shadow-[0_20px_60px_rgba(0,0,0,0.6)] shadow-black text-slate-100";

  // 🎨 Semantic SOC Color Scale
  const getCellStyles = (value, isDiagonal) => {
    if (isDiagonal) return theme === 'dark' ? "bg-slate-800 text-slate-400 font-black" : "bg-slate-200 text-slate-500 font-black";
    
    if (value >= 99) return "bg-emerald-500 text-white shadow-[inset_0_0_12px_rgba(0,0,0,0.1)] font-black";
    if (value >= 95) return theme === 'dark' ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30" : "bg-emerald-50 text-emerald-700 font-bold";
    if (value >= 85) return theme === 'dark' ? "bg-amber-500/20 text-amber-400 border border-amber-500/30" : "bg-amber-50 text-amber-700 font-bold";
    if (value >= 70) return theme === 'dark' ? "bg-orange-500/20 text-orange-400 border border-orange-500/30" : "bg-orange-50 text-orange-700 font-bold";
    return theme === 'dark' ? "bg-rose-500/20 text-rose-400 border border-rose-500/30" : "bg-rose-50 text-rose-700 font-bold";
  };

  if (!data || !Array.isArray(data.models) || data.models.length === 0 || !data.matrix) {
    return (
      <div className={`${containerStyle} rounded-[2.5rem] p-8 flex items-center justify-center h-[450px]`}>
        <p className="text-sm font-black uppercase tracking-widest opacity-40 italic text-center animate-pulse">Synchronizing logic matrix...</p>
      </div>
    );
  }

  const { models, matrix } = data;

  return (
    <div className={`${containerStyle} rounded-[2.5rem] p-8 flex flex-col transition-all duration-700 animate-in fade-in slide-in-from-bottom-4`}>
      
      {/* 🚀 Header Logic */}
      <div className="flex justify-between items-start mb-6">
        <div>
          <h3 className="text-sm font-black uppercase tracking-[0.2em] opacity-80">
            Ensemble Consensus Heatmap
          </h3>
          <p className="text-[11px] font-bold text-indigo-500/70 uppercase tracking-widest mt-1">
            Pairwise Logic Agreement Percentage
          </p>
        </div>
        <div className="p-2 bg-indigo-500/10 rounded-xl">
           <div className="w-2 h-2 rounded-full bg-indigo-500 animate-pulse" />
        </div>
      </div>

      {/* 📊 Heatmap Grid Mesh */}
      <div className="flex-1 overflow-hidden rounded-2xl border border-slate-100 dark:border-slate-800 shadow-inner">
        <div 
          className="grid gap-[1px] bg-slate-200 dark:bg-slate-800"
          style={{ gridTemplateColumns: `140px repeat(${models.length}, 1fr)` }}
        >
          {/* Top-Left Corner Spacer */}
          <div className={theme === 'dark' ? "bg-slate-950" : "bg-slate-100/50"} />

          {/* Column Headers */}
          {models.map((model) => (
            <div key={model} className={`py-4 px-1 flex flex-col items-center justify-center text-center leading-none ${theme === 'dark' ? 'bg-slate-950 text-slate-500' : 'bg-slate-100/80 text-slate-400'}`}>
              {MODEL_LABELS[model].split(" ").map((word, i) => (
                <span key={i} className="text-[10px] font-black uppercase tracking-tighter block">{word}</span>
              ))}
            </div>
          ))}

          {/* Data Rows */}
          {models.map((row) => (
            <React.Fragment key={row}>
              {/* Row Label Column */}
              <div className={`px-4 py-3 flex items-center text-[11px] font-black uppercase tracking-tighter ${theme === 'dark' ? 'bg-slate-950 text-slate-400' : 'bg-slate-100/50 text-slate-500'}`}>
                {MODEL_LABELS[row]}
              </div>

              {/* Data Cells */}
              {models.map((col) => {
                const value = Math.min(Math.max(matrix[row]?.[col] ?? 0, 0), 100);
                const isDiagonal = row === col;
                return (
                  <div
                    key={`${row}-${col}`}
                    className={`h-14 flex items-center justify-center transition-all duration-300 group cursor-crosshair
                      ${getCellStyles(value, isDiagonal)}`}
                  >
                    {/* 🔹 FIXED: Unified numeric font size with percentage */}
                    <div className="flex items-baseline gap-0.5">
                      <span className="text-[14px] tabular-nums font-black leading-none">
                        {value.toFixed(1)}
                      </span>
                      <span className="text-[13px] font-black opacity-80 leading-none">
                        %
                      </span>
                    </div>
                  </div>
                );
              })}
            </React.Fragment>
          ))}
        </div>
      </div>

      {/* 📑 Legend & Caption */}
      <div className="mt-8 flex flex-col items-center gap-5">
        <div className="flex flex-wrap justify-center gap-8 px-4">
          <LegendDot color="bg-emerald-500" label="Perfect Correlation" theme={theme} />
          <LegendDot color="bg-emerald-500/20" label="High Consensus" border="border-emerald-500/30" theme={theme} />
          <LegendDot color="bg-amber-500/20" label="Stable Baseline" border="border-amber-500/30" theme={theme} />
          <LegendDot color="bg-rose-500/20" label="Variance Alert" border="border-rose-500/30" theme={theme} />
        </div>
        <p className="text-[10px] font-black text-center uppercase tracking-[0.3em] opacity-40 italic border-t dark:border-slate-800 pt-4 w-full">
          Deep Green zones represent high model-to-model correlation on traffic classifications
        </p>
      </div>
    </div>
  );
}

/* Helper Components */
function LegendDot({ color, label, border = "", theme }) {
  return (
    <div className="flex items-center gap-3">
      <div className={`w-4 h-4 rounded-md shadow-sm ${color} ${border}`} />
      <span className={`text-[10px] font-black uppercase tracking-widest ${theme === 'dark' ? 'text-slate-500' : 'text-slate-400'}`}>{label}</span>
    </div>
  );
}

export default ModelAgreementHeatmap;