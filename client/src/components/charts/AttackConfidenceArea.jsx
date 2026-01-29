import { useEffect, useState, useMemo } from "react";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from "recharts";
import { getAlertLogs } from "../../api";

/**
 * Enhanced AttackConfidenceArea
 * Version 3.2 - Standardized Height (380px)
 * Features: Dynamic Risk Gradients, Auto-scaling Y-Axis, and Real-time Polling.
 */

function AttackConfidenceArea() {
  const [data, setData] = useState([]);

  useEffect(() => {
    let mounted = true;
    const fetchData = async () => {
      try {
        const res = await getAlertLogs({ page: 1, limit: 20 });
        if (!mounted) return;

        const formatted = res.data.logs
          .slice()
          .reverse()
          .map((log, index) => ({
            index: index + 1,
            confidence: Number(log.confidence ?? 0),
            isAttack: Number(log.confidence ?? 0) > 0.5,
          }));

        setData(formatted);
      } catch (err) {
        console.error("AttackConfidenceArea error:", err);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, []);

  const maxConfidence = useMemo(() => {
    return Math.max(...data.map((d) => d.confidence), 0);
  }, [data]);

  // Adaptive Y-Axis scaling for better visual resolution of low-level data
  const yMax = maxConfidence < 0.1 ? 0.1 : maxConfidence < 0.3 ? 0.4 : 1;
  const chartKey = data.length;
  const isCurrentlyHighRisk = maxConfidence > 0.5;

  return (
    <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100 h-[380px] flex flex-col transition-all hover:shadow-xl group animate-fade-in">
      
      {/* HEADER: Standardized with Subtitle */}
      <div className="flex justify-between items-start mb-6">
        <div>
          <h3 className="font-bold text-gray-800 text-lg tracking-tight leading-none">
            Ensemble Confidence Trend
          </h3>
          <p className="text-[10px] text-gray-400 font-bold uppercase tracking-widest mt-1">
            Real-time Model Certainty
          </p>
        </div>
        <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-gray-50 border border-gray-100">
           <span className={`w-2 h-2 rounded-full ${isCurrentlyHighRisk ? 'animate-ping bg-red-500' : 'bg-green-500'}`}></span>
           <span className="text-[10px] font-black text-gray-500 uppercase tracking-wider">
             {isCurrentlyHighRisk ? 'Critical' : 'Stable'}
           </span>
        </div>
      </div>

      {/* CHART AREA: flex-grow ensures matching height with siblings */}
      <div className="flex-grow w-full min-h-0">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} key={chartKey} margin={{ top: 10, right: 10, left: -25, bottom: 0 }}>
            <defs>
              <linearGradient id="trendGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={isCurrentlyHighRisk ? "#ef4444" : "#10b981"} stopOpacity={0.3} />
                <stop offset="95%" stopColor={isCurrentlyHighRisk ? "#ef4444" : "#10b981"} stopOpacity={0} />
              </linearGradient>
            </defs>

            <CartesianGrid strokeDasharray="4 4" vertical={false} stroke="#f1f5f9" />

            <XAxis 
              dataKey="index" 
              hide={data.length === 0}
              axisLine={false} 
              tickLine={false} 
              tick={{ fontSize: 10, fill: "#94a3b8", fontWeight: 700 }}
            />

            <YAxis 
              domain={[0, yMax]} 
              tickFormatter={(v) => `${Math.round(v * 100)}%`} 
              axisLine={false} 
              tickLine={false} 
              tick={{ fontSize: 10, fill: "#94a3b8", fontWeight: 700 }}
            />

            <Tooltip
              content={({ active, payload }) => {
                if (active && payload && payload.length) {
                  const val = payload[0].value;
                  const highRisk = val > 0.5;
                  return (
                    <div className="bg-gray-900/95 backdrop-blur-md text-white p-3 rounded-xl shadow-2xl border border-gray-700 animate-in fade-in zoom-in-95 duration-200">
                      <p className="text-[9px] text-gray-500 font-black uppercase mb-1 tracking-widest">
                        Sequence #{payload[0].payload.index}
                      </p>
                      <p className={`text-xl font-black ${highRisk ? 'text-red-400' : 'text-green-400'} leading-none mb-1`}>
                        {(val * 100).toFixed(2)}%
                      </p>
                      <p className="text-[9px] text-gray-400 font-bold uppercase tracking-tight">Certainty Score</p>
                    </div>
                  );
                }
                return null;
              }}
            />

            <Area
              type="monotone"
              dataKey="confidence"
              stroke={isCurrentlyHighRisk ? "#ef4444" : "#10b981"}
              strokeWidth={3}
              fill="url(#trendGradient)"
              isAnimationActive={true}
              animationDuration={1500}
              animationEasing="ease-in-out"
              activeDot={{ r: 5, strokeWidth: 0, fill: isCurrentlyHighRisk ? "#ef4444" : "#10b981" }}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* FOOTER: Standardized Metadata row */}
      <div className="mt-4 pt-4 border-t border-gray-50 flex justify-between items-center">
        <p className="text-[10px] font-bold text-gray-400 italic">
          {yMax < 1 ? "🔍 Auto-scaling active" : "⚠️ Full-scale risk view"}
        </p>
        <div className="flex items-center gap-2 bg-gray-50 px-2 py-1 rounded border border-gray-100">
          <div className="w-2.5 h-0.5 bg-red-400 rounded-full"></div>
          <span className="text-[9px] font-black text-gray-400 uppercase tracking-tighter">
            Detection Threshold (50%)
          </span>
        </div>
      </div>
    </div>
  );
}

export default AttackConfidenceArea;