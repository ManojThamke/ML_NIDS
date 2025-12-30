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

const COLORS = [
  "#ec4899",
  "#f43f5e",
  "#fb7185",
  "#fda4af",
  "#fecdd3",
];

function TopAttackedDestinationsChart() {
  const [data, setData] = useState([]);

  useEffect(() => {
    getTopDestinations()
      .then((res) => setData(res.data))
      .catch(console.error);
  }, []);

  if (!data.length) return null;

  return (
    <div className="bg-white rounded-xl p-6 shadow-sm border h-[380px]">
      <h3 className="font-semibold mb-4 text-gray-700">
        Top Attacked Destinations
      </h3>

      <ResponsiveContainer width="100%" height={240}>
        <BarChart data={data} layout="vertical">
          {/* Grid */}
          <CartesianGrid
            strokeDasharray="4 4"
            horizontal={false}
            stroke="#e5e7eb"
          />

          {/* X Axis */}
          <XAxis
            type="number"
            allowDecimals={false}
            tick={{ fontSize: 11, fill: "#6b7280" }}
          />

          {/* Y Axis */}
          <YAxis
            type="category"
            dataKey="destination"
            width={130}
            tick={{ fontSize: 11, fill: "#374151" }}
          />

          {/* Tooltip */}
          <Tooltip
            cursor={{ fill: "rgba(236,72,153,0.08)" }}
            contentStyle={{
              backgroundColor: "#111827",
              border: "none",
              borderRadius: "10px",
              color: "#f9fafb",
              fontSize: "12px",
            }}
          />

          {/* Bars */}
          <Bar dataKey="count" radius={[0, 8, 8, 0]}>
            {data.map((_, index) => (
              <Cell
                key={`cell-${index}`}
                fill={COLORS[index % COLORS.length]}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export default TopAttackedDestinationsChart;
