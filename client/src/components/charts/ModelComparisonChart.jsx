import { useEffect, useState } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
  LabelList,
} from "recharts";
import { getModelMetrics } from "../../api";

/* 🎨 Soft theme colors (ML-NIDS palette) */
const COLORS = [
  "#93c5fd", 
  "#7dd3fc", 
  "#fdba74", 
  "#c4b5fd", 
  "#86efac", 
  "#fde68a", 
  "#a7f3d0", 
  "#fca5a5", 
  "#fbcfe8", 
  "#ddd6fe", 
  "#fecaca",


];

/* 🧠 Wrapped X-axis labels */
const CustomTick = ({ x, y, payload }) => {
  const words = payload.value.split(" ");
  return (
    <g transform={`translate(${x},${y})`}>
      <text textAnchor="middle" fill="#374151" fontSize={11}>
        {words.map((word, i) => (
          <tspan key={i} x={0} dy={i === 0 ? 0 : 12}>
            {word}
          </tspan>
        ))}
      </text>
    </g>
  );
};

function ModelComparisonChart() {
  const [data, setData] = useState([]);

  useEffect(() => {
    getModelMetrics()
      .then((res) => {
        // ✅ Convert accuracy → percentage
        const formatted = res.data.map((m) => ({
          ...m,
          accuracyPercent: +(m.accuracy * 100).toFixed(2),
        }));
        setData(formatted);
      })
      .catch(console.error);
  }, []);

  return (
    <div className="bg-white rounded-xl p-6 shadow-sm border h-[340px]">
      <h3 className="font-semibold mb-4 text-gray-700">
        Model Accuracy Comparison
      </h3>

      <ResponsiveContainer width="100%" height={260}>
        <BarChart
          data={data}
          margin={{ top: 30, right: 10, left: 0, bottom: 30 }}
          barCategoryGap="18%"
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />

          {/* ✅ Wrapped model names */}
          <XAxis
            dataKey="modelName"
            tick={<CustomTick />}
            interval={0}
            height={55}
            tickMargin={8}
          />

          {/* ✅ Correct scale */}
          <YAxis
            domain={[0, 100]}
            tickFormatter={(v) => `${v}%`}
          />

          <Tooltip
            formatter={(v) => `${v}%`}
          />

          <Bar
            dataKey="accuracyPercent"
            barSize={32}
            radius={[6, 6, 0, 0]}
          >
            {/* ✅ Percent labels above bars */}
            <LabelList
              dataKey="accuracyPercent"
              position="top"
              formatter={(v) => `${v}%`}
              fontSize={11}
              fill="#374151"
            />

            {data.map((_, index) => (
              <Cell
                key={index}
                fill={COLORS[index % COLORS.length]}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export default ModelComparisonChart;
