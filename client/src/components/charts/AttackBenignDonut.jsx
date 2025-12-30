import { PieChart, Pie, Cell, Tooltip } from "recharts";

function AttackBenignDonut({ stats }) {
  const attack = stats?.attack || 0;
  const benign = stats?.benign || 0;
  const total = stats?.total || 1;

  const benignPercent = ((benign / total) * 100).toFixed(1);
  const attackPercent = ((attack / total) * 100).toFixed(1);

  const data = [
    { name: "Attack", value: attack },
    { name: "Benign", value: benign },
  ];

  const COLORS = ["#ef4444", "#10b981"];

  return (
    <div className="bg-white rounded-xl p-6 shadow-sm border h-[340px]">
      <h3 className="font-semibold mb-4 text-gray-700">
        Benign vs Attack
      </h3>

      <div className="relative flex justify-center">
        <PieChart width={220} height={220}>
          <Pie
            data={data}
            dataKey="value"
            cx="50%"
            cy="50%"
            innerRadius={70}
            outerRadius={90}
            paddingAngle={2}
          >
            {data.map((_, i) => (
              <Cell key={i} fill={COLORS[i]} />
            ))}
          </Pie>
          <Tooltip />
        </PieChart>

        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <p className="text-xl font-bold text-green-600">
            {benignPercent}%
          </p>
          <p className="text-xs text-gray-500">Benign</p>
        </div>
      </div>

      <p className="text-m text-gray-500 text-center mt-3">
        <span className="text-red-500">{attackPercent}% Attack🔴</span> 🔹  <span className="text-green-500"> {benignPercent}% Benign🟢</span>
      </p>
    </div>
  );
}

export default AttackBenignDonut;
