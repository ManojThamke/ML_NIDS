import React from "react";
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from "recharts";

/**
 * Enhanced AttackBenignDonut Component
 * Version 3.2 - Standardized Height for Dashboard Symmetry
 * Features: SVG Gradients, Glassmorphism Tooltips, and Semantic Progress Bars.
 */

const GRADIENTS = ["url(#attackGradient)", "url(#benignGradient)"];

const AttackBenignDonut = ({ stats }) => {
  // 1. Data Processing
  const attack = stats?.attack || 0;
  const benign = stats?.benign || 0;
  const total = Math.max(stats?.total || 0, 1);

  const benignPercent = ((benign / total) * 100).toFixed(1);
  const attackPercent = ((attack / total) * 100).toFixed(1);

  const data = [
    { name: "Attack", value: attack || 0.001 },
    { name: "Benign", value: benign || 0.001 },
  ];

  const isHighRisk = parseFloat(attackPercent) > 5.0;
  const isAttackDominant = attack > benign;

  return (
    <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100 h-[380px] flex flex-col transition-all hover:shadow-xl animate-fade-in group">
      
      {/* HEADER: Standardized spacing */}
      <div className="flex justify-between items-center mb-4">
        <div>
          <h3 className="font-bold text-gray-800 text-lg tracking-tight leading-none">Traffic Distribution</h3>
          <p className="text-[10px] text-gray-400 font-bold uppercase tracking-widest mt-1">NETWORK TELEMETRY</p>
        </div>
        {isHighRisk && (
          <span className="animate-pulse bg-red-100 text-red-600 text-[10px] px-2.5 py-1 rounded-md font-black uppercase tracking-wider border border-red-200">
            Critical
          </span>
        )}
      </div>

      {/* CHART AREA: Using flex-grow to fill the 380px container */}
      <div className="relative flex-grow flex items-center justify-center min-h-0">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <defs>
              <linearGradient id="attackGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#f87171" stopOpacity={0.8} />
                <stop offset="95%" stopColor="#ef4444" stopOpacity={1} />
              </linearGradient>
              <linearGradient id="benignGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#34d399" stopOpacity={0.8} />
                <stop offset="95%" stopColor="#10b981" stopOpacity={1} />
              </linearGradient>
            </defs>
            
            <Pie
              data={data}
              dataKey="value"
              innerRadius="70%"
              outerRadius="90%"
              paddingAngle={8}
              cornerRadius={12}
              stroke="none"
              isAnimationActive={true}
              animationDuration={1800}
              animationEasing="ease-out"
            >
              {data.map((_, i) => (
                <Cell 
                  key={`cell-${i}`} 
                  fill={GRADIENTS[i]} 
                  className="hover:opacity-80 transition-opacity cursor-pointer focus:outline-none"
                />
              ))}
            </Pie>

            <Tooltip
              content={({ active, payload }) => {
                if (active && payload && payload.length) {
                  const isAttack = payload[0].name === "Attack";
                  return (
                    <div className="bg-gray-900/95 backdrop-blur-md text-white p-3 rounded-xl shadow-2xl border border-gray-700 text-xs animate-in zoom-in-95 duration-200">
                      <p className="font-bold border-b border-gray-700 mb-1.5 pb-1 flex items-center gap-2">
                        <span className={`w-2 h-2 rounded-full ${isAttack ? 'bg-red-500' : 'bg-green-500'}`}></span>
                        {payload[0].name}
                      </p>
                      <p className="text-gray-400">Total: <span className="text-white font-mono">{payload[0].value.toLocaleString()}</span></p>
                      <p className={`font-bold mt-0.5 ${isAttack ? 'text-red-400' : 'text-green-400'}`}>
                        Share: {isAttack ? attackPercent : benignPercent}%
                      </p>
                    </div>
                  );
                }
                return null;
              }}
            />
          </PieChart>
        </ResponsiveContainer>

        {/* CENTER OVERLAY: Dynamic metrics */}
        <div className="absolute flex flex-col items-center justify-center pointer-events-none text-center">
          <span className="text-3xl font-black text-gray-800 tabular-nums leading-none">
            {isAttackDominant ? attackPercent : benignPercent}%
          </span>
          <span className={`text-[10px] font-black uppercase tracking-[0.2em] mt-2 ${isAttackDominant ? 'text-red-500' : 'text-green-500'}`}>
            {isAttackDominant ? "Critical" : "Secure"}
          </span>
        </div>
      </div>

      {/* FOOTER LEGEND: Standardized with Progress Bars */}
      <div className="grid grid-cols-2 gap-6 mt-6 pt-4 border-t border-gray-50">
        <div className="flex flex-col">
          <div className="flex justify-between text-[11px] mb-1.5 px-0.5">
            <span className="text-gray-400 font-bold uppercase">Attack</span>
            <span className="text-red-600 font-black">{attackPercent}%</span>
          </div>
          <div className="w-full bg-gray-100 h-1.5 rounded-full overflow-hidden">
            <div 
              className="bg-red-500 h-full rounded-full transition-all duration-1000" 
              style={{ width: `${attackPercent}%` }} 
            />
          </div>
        </div>

        <div className="flex flex-col">
          <div className="flex justify-between text-[11px] mb-1.5 px-0.5">
            <span className="text-gray-400 font-bold uppercase">Benign</span>
            <span className="text-green-600 font-black">{benignPercent}%</span>
          </div>
          <div className="w-full bg-gray-100 h-1.5 rounded-full overflow-hidden">
            <div 
              className="bg-green-500 h-full rounded-full transition-all duration-1000" 
              style={{ width: `${benignPercent}%` }} 
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default AttackBenignDonut;