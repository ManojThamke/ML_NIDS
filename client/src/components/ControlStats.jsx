import React, { useEffect, useRef, useState } from "react";
import { Activity, ShieldCheck, ShieldAlert, Cpu } from "lucide-react";

/**
 * Enhanced Stats Component (V3.2 - Final)
 * Standardized: Elevation (Shadows), Flex-alignment, and Semantic Color Mapping.
 */

function useCountUp(target, duration = 1200) {
  const [value, setValue] = useState(0);
  const hasAnimated = useRef(false);

  useEffect(() => {
    if (hasAnimated.current) {
      setValue(target);
      return;
    }
    hasAnimated.current = true;
    let startTime = null;
    const animate = (timestamp) => {
      if (!startTime) startTime = timestamp;
      const progress = Math.min((timestamp - startTime) / duration, 1);
      const easedProgress = 1 - Math.pow(2, -10 * progress);
      setValue(target * (progress === 1 ? 1 : easedProgress));
      if (progress < 1) requestAnimationFrame(animate);
    };
    requestAnimationFrame(animate);
  }, [target, duration]);

  return value;
}

function Stats({ stats, monitoring }) {
  const total = stats?.total || 0;
  const benignPercent = total ? ((stats?.benign || 0) / total) * 100 : 0;
  const attackPercent = total ? ((stats?.attack || 0) / total) * 100 : 0;

  const animatedTotal = useCountUp(total);
  const animatedBenign = useCountUp(benignPercent);
  const animatedAttack = useCountUp(attackPercent);

  const CARDS = [
    {
      title: "Total Packets",
      value: Math.round(animatedTotal).toLocaleString(),
      color: "blue",
      Icon: Activity,
      subtext: "Captured & Analyzed"
    },
    {
      title: "Benign Traffic",
      value: `${animatedBenign.toFixed(1)}%`,
      color: "emerald",
      Icon: ShieldCheck,
      subtext: "Safe Communications"
    },
    {
      title: "Attack Traffic",
      value: `${animatedAttack.toFixed(1)}%`,
      color: "rose",
      Icon: ShieldAlert,
      subtext: "High-Risk Threats"
    }
  ];

  return (
    <div className="mb-10 animate-fade-in">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        
        {/* 1. Standard KPI Cards */}
        {CARDS.map(({ title, value, color, Icon, subtext }) => (
          <div key={title} className="group relative overflow-hidden bg-white rounded-2xl p-6 border border-gray-100 shadow-lg transition-all duration-500 hover:shadow-2xl hover:-translate-y-1.5">
            
            {/* Watermark Icon */}
            <div className="absolute -right-4 -bottom-4 opacity-[0.03] transform group-hover:scale-110 group-hover:-rotate-12 transition-transform duration-700 text-gray-900">
              <Icon size={120} strokeWidth={1} />
            </div>

            <div className="relative z-10 flex flex-col h-full">
              <div className="flex items-center gap-3 mb-4">
                <div className={`flex items-center justify-center p-2 rounded-xl bg-${color}-50 text-${color}-600 shadow-inner`}>
                  <Icon size={20} strokeWidth={2.5} />
                </div>
                <p className="text-[10px] font-black uppercase tracking-widest text-gray-400">{title}</p>
              </div>

              <p className="text-3xl font-black text-gray-800 tracking-tight tabular-nums leading-none">
                {value}
              </p>
              
              <div className="mt-4 flex items-center gap-2">
                <div className={`w-1.5 h-1.5 rounded-full bg-${color}-400 shadow-[0_0_8px_rgba(0,0,0,0.1)]`} />
                <p className="text-[10px] font-bold text-gray-400 uppercase italic tracking-wide">{subtext}</p>
              </div>
            </div>

            <div className={`absolute bottom-0 left-0 h-1.5 bg-${color}-500 transition-all duration-700 w-0 group-hover:w-full`} />
          </div>
        ))}

        {/* 2. System Engine Card (Fixed Shadow and State Mapping) */}
        <div className={`
          group relative overflow-hidden rounded-2xl p-6 border transition-all duration-500 
          hover:shadow-2xl hover:-translate-y-1.5 shadow-lg
          ${monitoring 
            ? "bg-white border-emerald-100 shadow-emerald-100/50" 
            : "bg-white border-amber-100 shadow-amber-100/50"}
        `}>
          <div className="relative z-10">
            <div className="flex items-center gap-3 mb-4">
              <div className={`flex items-center justify-center p-2 rounded-xl ${monitoring ? "bg-emerald-50 text-emerald-600" : "bg-amber-50 text-amber-600"}`}>
                <Cpu size={20} strokeWidth={2.5} />
              </div>
              <p className="text-[10px] font-black uppercase tracking-widest text-gray-400">System Engine</p>
            </div>

            <div className="flex items-center gap-2 mt-2">
              <p className={`text-2xl font-black tracking-tighter ${monitoring ? "text-emerald-700" : "text-amber-700"}`}>
                {monitoring ? "ONLINE" : "STANDBY"}
              </p>
              {monitoring && <div className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-ping shadow-[0_0_10px_rgba(16,185,129,0.5)]" />}
            </div>

            <div className={`mt-5 inline-flex items-center gap-2 px-3 py-1.5 rounded-lg text-[9px] font-black uppercase tracking-widest border transition-colors ${monitoring ? "bg-emerald-50 text-emerald-600 border-emerald-100" : "bg-amber-50 text-amber-700 border-amber-200"}`}>
               {monitoring ? "Connected to Live Intel" : "Engine Paused"}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Stats;