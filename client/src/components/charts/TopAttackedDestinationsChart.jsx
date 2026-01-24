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
import { getTopDestinations } from "../../api";

/* 🎨 Soft attack-themed pastel colors */
const COLORS = [
  "#ef4444", // Strong red
  "#f87171",
  "#fca5a5",
  "#fecaca",
  "#fee2e2",
];

/* Clean dashboard tooltip */
const CustomTooltip = ({ active, payload }) => {
  if (!active || !payload || !payload.length) return null;

  const { destination, count } = payload[0].payload;

  return (
    <div className="bg-gray-900 text-white rounded-lg px-4 py-2 shadow-lg">
      <p className="text-sm font-semibold mb-1">
        {destination}
      </p>
      <p className="text-sm text-gray-300">
        Attacks: <span className="font-semibold text-white">{count}</span>
      </p>
    </div>
  );
};

function TopAttackedDestinationsChart() {
  const [data, setData] = useState([]);

  useEffect(() => {
    getTopDestinations()
      .then((res) => setData(res.data))
      .catch(console.error);
  }, []);

  if (!data.length) {
    return (
      <div className="bg-white rounded-xl p-6 shadow-sm border animate-fade-in">
        <p className="text-sm text-gray-500">
          No attacked destination data available
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl p-6 shadow-sm border h-[340px] flex flex-col animate-fade-in">
      <h3 className="font-semibold mb-2 text-gray-700">
        Top Attacked Destinations
      </h3>

      {/* Chart */}
      <div className="h-[240px]">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={data}
            layout="vertical"
            margin={{ top: 10, right: 20, left: 10, bottom: 6 }}
            barCategoryGap="20%"
          >
            <CartesianGrid
              strokeDasharray="3 3"
              horizontal={false}
              stroke="#e5e7eb"
            />

            <XAxis
              type="number"
              allowDecimals={false}
              tick={{ fontSize: 11, fill: "#6b7280" }}
            />

            <YAxis
              type="category"
              dataKey="destination"
              width={120}
              tick={{ fontSize: 11, fill: "#374151" }}
            />

            <Tooltip content={<CustomTooltip />} />

            <Bar
              dataKey="count"
              radius={[0, 8, 8, 0]}
              isAnimationActive={true}
              animationBegin={200}
              animationDuration={1800}
              animationEasing="ease-in-out"
            >
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

      {/* Explanation */}
      <p className="-mt-2 text-sm text-gray-600 text-center leading-snug">
        Displays the destinations most frequently targeted by detected attacks.
      </p>
    </div>
  );
}

export default TopAttackedDestinationsChart;
