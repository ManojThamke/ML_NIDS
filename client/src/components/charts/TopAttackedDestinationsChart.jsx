import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Cell,
} from "recharts";
import { useEffect, useState } from "react";
import { getAlertTopDestinations } from "../../api";

const RED_GRADIENT = ["#dc2626", "#ef4444", "#f87171", "#fca5a5", "#fee2e2"];

const CustomTooltip = ({ active, payload }) => {
  if (!active || !payload || !payload.length) return null;
  const { destination, count } = payload[0].payload;

  return (
    <div className="bg-gray-900/95 backdrop-blur-md border border-gray-700 rounded-xl px-4 py-3 shadow-2xl animate-in fade-in zoom-in-95 duration-200">
      <p className="text-[10px] uppercase tracking-widest font-bold text-gray-400 mb-1">Target Identity</p>
      <p className="text-sm font-black text-white mb-1.5">{destination}</p>
      <div className="flex items-center gap-2">
        <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
        <p className="text-xs text-gray-300">
          Incidents: <span className="font-bold text-white">{count.toLocaleString()}</span>
        </p>
      </div>
    </div>
  );
};

function TopAttackedDestinationsChart() {
  const [data, setData] = useState([]);

  useEffect(() => {
    getAlertTopDestinations()
      .then((res) => setData(res.data))
      .catch(console.error);
  }, []);

  if (!data.length) {
    return (
      <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100 h-[380px] flex items-center justify-center">
        <div className="text-center">
          <p className="text-xs font-bold text-gray-400 uppercase tracking-widest">No Active Threats Detected</p>
        </div>
      </div>
    );
  }

  return (
    /* Increased height slightly to h-[380px] for better breathing room */
    <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100 h-[380px] flex flex-col transition-all hover:shadow-xl group">
      
      {/* 1. Header */}
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="font-bold text-gray-800 text-lg tracking-tight">Top Attacked Destinations</h3>
          <p className="text-[10px] text-gray-400 font-bold uppercase tracking-widest">Asset Risk Profiling</p>
        </div>
        <div className="bg-red-50 px-2 py-1 rounded-md border border-red-100">
           <span className="text-[10px] font-black text-red-600 uppercase tracking-wider">Live Intel</span>
        </div>
      </div>

      {/* 2. Responsive Chart Area - flex-grow ensures it takes available space */}
      <div className="flex-grow w-full overflow-hidden">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={data}
            layout="vertical"
            /* Reduced bottom margin to 0 to prevent pushing the footer out */
            margin={{ top: 5, right: 35, left: 10, bottom: 0 }}
            barCategoryGap="20%"
          >
            <CartesianGrid strokeDasharray="4 4" horizontal={false} stroke="#f1f5f9" />
            <XAxis type="number" hide />
            <YAxis
              type="category"
              dataKey="destination"
              width={90}
              axisLine={false}
              tickLine={false}
              tick={{ fontSize: 10, fill: "#64748b", fontWeight: 700 }}
            />
            <Tooltip 
              content={<CustomTooltip />} 
              cursor={{ fill: '#f8fafc', radius: 8 }}
            />
            <Bar
              dataKey="count"
              radius={[0, 6, 6, 0]}
              isAnimationActive={true}
              animationDuration={2000}
            >
              {data.map((_, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={RED_GRADIENT[index % RED_GRADIENT.length]}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* 3. Perfected Footer - Added mt-2 for consistent gap */}
      <div className="mt-2 pt-3 border-t border-gray-100 w-full">
        <p className="text-[10.5px] text-gray-400 font-medium italic text-center leading-relaxed">
          Prioritizing destinations by total incident frequency.
        </p>
      </div>
    </div>
  );
}

export default TopAttackedDestinationsChart;