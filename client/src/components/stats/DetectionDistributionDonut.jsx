import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

/* 🎨 ML-NIDS Theme Colors */
const COLORS = {
  Benign: "#10b981", // green
  Attack: "#ef4444", // red
};

/* Tooltip */
const CustomTooltip = ({ active, payload }) => {
  if (!active || !payload?.length) return null;
  const { name, value } = payload[0];

  return (
    <div className="bg-gray-900 text-white rounded-lg px-4 py-2 shadow-lg">
      <p className="text-sm font-semibold mb-1">{name}</p>
      <p className="text-sm text-gray-300">
        Alerts: <span className="font-semibold">{Math.round(value)}</span>
      </p>
    </div>
  );
};

function DetectionDistributionDonut({ data }) {
  const attack = data?.attack ?? 0;
  const benign = data?.benign ?? 0;

  /* 🔒 keep math correct but allow render */
  const safeAttack = attack === 0 ? 0.0001 : attack;
  const safeBenign = benign === 0 ? 0.0001 : benign;

  const total = safeAttack + safeBenign;
  const attackPercent = ((safeAttack / total) * 100).toFixed(1);

  const chartData = [
    { name: "Benign", value: safeBenign },
    { name: "Attack", value: safeAttack },
  ];

  return (
    <div className="bg-white rounded-xl p-6 shadow-sm border h-[340px] flex flex-col animate-fade-in">
      <h3 className="font-semibold mb-2 text-gray-700">
        Detection Distribution
      </h3>

      {/* Donut */}
      <div className="h-[235px] flex items-center justify-center relative">
        <ResponsiveContainer width={240} height={240}>
          <PieChart>
            <Pie
              data={chartData}
              dataKey="value"
              cx="50%"
              cy="50%"
              innerRadius={72}
              outerRadius={92}
              paddingAngle={1.5}
              cornerRadius={6}
              startAngle={90}
              endAngle={-270}
              stroke="#ffffff"
              strokeWidth={3}
              isAnimationActive
              animationBegin={200}
              animationDuration={2200}
              animationEasing="ease-in-out"
            >
              {chartData.map((entry) => (
                <Cell
                  key={entry.name}
                  fill={COLORS[entry.name]}
                />
              ))}
            </Pie>

            <Tooltip content={<CustomTooltip />} />
          </PieChart>
        </ResponsiveContainer>

        {/* Center label */}
        <div className="absolute flex flex-col items-center justify-center">
          <p className="text-xl font-bold text-red-600">
            {attackPercent}%
          </p>
          <p className="text-xs text-gray-500">
            Attack Ratio
          </p>
        </div>
      </div>

      {/* Legend */}
      <div className="text-sm text-gray-600 text-center mb-1">
        <span className="font-medium text-red-600">
          ● Attack: {attack}
        </span>
        <span className="mx-3 text-gray-300">•</span>
        <span className="font-medium text-green-600">
          ● Benign: {benign}
        </span>
      </div>

      {/* Insight */}
      <p className="-mt-1 text-sm text-gray-600 text-center leading-snug">
        Shows the overall proportion of benign versus attack traffic.
      </p>
    </div>
  );
}

export default DetectionDistributionDonut;
