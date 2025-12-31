import { PieChart, Pie, Cell, Tooltip } from "recharts";

function DetectionDistributionDonut({ data }) {
  const attack = data?.attack ?? 0;
  const benign = data?.benign ?? 0;
  const total = attack + benign || 1;

  const attackPercent = ((attack / total) * 100).toFixed(1);

  const chartData = [
    { name: "Benign", value: benign },
    { name: "Attack", value: attack },
  ];

  /* 🎨 ML-NIDS Theme Colors */
  const COLORS = {
    Benign: "#10b981",
    Attack: "#ef4444",
  };

  return (
    <div className="bg-white rounded-xl p-6 shadow-sm border h-[340px]">
      <h3 className="font-semibold mb-3 text-gray-700">
        Detection Distribution
      </h3>

      <div className="relative flex justify-center">
        <PieChart width={210} height={210}>
          <Pie
            data={chartData}
            dataKey="value"
            cx="50%"
            cy="50%"
            innerRadius={70}
            outerRadius={90}
            paddingAngle={2}
            stroke="#f9fafb"
            strokeWidth={4}
          >
            {chartData.map((entry) => (
              <Cell
                key={entry.name}
                fill={COLORS[entry.name]}
              />
            ))}
          </Pie>

          {/* ✅ Styled Tooltip */}
          <Tooltip
            formatter={(v, name) => [`${v} alerts`, name]}
            contentStyle={{
              background: "#111827",
              border: "none",
              borderRadius: "8px",
              color: "#f9fafb",
              fontSize: "12px",
            }}
          />
        </PieChart>

        {/* Center Text */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <p className="text-xl font-bold text-red-600">
            {attackPercent}%
          </p>
          <p className="text-xs text-gray-500">
            Attack Ratio
          </p>
        </div>
      </div>

      {/* Legend */}
      <div className="text-sm text-gray-500 text-center mt-1">
        <span className="text-red-600 font-medium">
          🔴 Attack: {attack}
        </span>
        <span className="mx-3 text-gray-300">•</span>
        <span className="text-green-600 font-medium">
          🟢 Benign: {benign}
        </span>
      </div>

      {/* Insight */}
      <p className="text-xs text-gray-500 text-center mt-2">
        Overall detection outcome across monitored traffic
      </p>
    </div>
  );
}

export default DetectionDistributionDonut;
