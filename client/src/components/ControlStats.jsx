import { useEffect, useState } from "react";

/* ================= COUNT-UP HOOK ================= */
function useCountUp(target, duration = 800) {
  const [value, setValue] = useState(0);

  useEffect(() => {
    let start = 0;
    let startTime = null;

    const animate = (timestamp) => {
      if (!startTime) startTime = timestamp;
      const progress = Math.min((timestamp - startTime) / duration, 1);

      const current = start + (target - start) * progress;
      setValue(current);

      if (progress < 1) {
        requestAnimationFrame(animate);
      }
    };

    requestAnimationFrame(animate);

    return () => cancelAnimationFrame(animate);
  }, [target, duration]);

  return value;
}

function Stats({ stats, monitoring }) {
  const total = stats?.total || 0;
  const benign = stats?.benign || 0;
  const attack = stats?.attack || 0;

  const benignPercent = total ? (benign / total) * 100 : 0;
  const attackPercent = total ? (attack / total) * 100 : 0;

  /* ================= ANIMATED VALUES ================= */
  const animatedTotal = useCountUp(total);
  const animatedBenign = useCountUp(benignPercent);
  const animatedAttack = useCountUp(attackPercent);

  return (
    <div className="grid grid-cols-4 gap-6 mb-8">

      {/* Total Packets */}
      <div className="bg-white rounded-xl p-5 border shadow-sm
                      transition-all duration-300
                      hover:shadow-xl hover:scale-[1.02]
                      animate-fade-in">
        <p className="text-sm text-gray-500">
          Total Packets Captured
        </p>
        <p className="text-3xl font-bold mt-2">
          {Math.round(animatedTotal)}
        </p>
      </div>

      {/* Benign */}
      <div className="bg-green-50 rounded-xl p-5 border border-green-100
                      transition-all duration-300
                      hover:shadow-xl hover:scale-[1.02]
                      animate-fade-in">
        <p className="text-sm text-green-700">
          Benign Traffic
        </p>
        <p className="text-3xl font-bold text-green-800 mt-2">
          {animatedBenign.toFixed(1)}%
        </p>
      </div>

      {/* Attack */}
      <div className="bg-red-50 rounded-xl p-5 border border-red-100
                      transition-all duration-300
                      hover:shadow-xl hover:scale-[1.02]
                      animate-fade-in">
        <p className="text-sm text-red-700">
          Attack Traffic
        </p>
        <p className="text-3xl font-bold text-red-800 mt-2">
          {animatedAttack.toFixed(1)}%
        </p>
      </div>

      {/* Live Status */}
      <div className="bg-white rounded-xl p-5 border shadow-sm
                      transition-all duration-300
                      hover:shadow-xl hover:scale-[1.02]
                      animate-fade-in">
        <p className="text-sm text-gray-500">
          Live Status
        </p>
        <p
          className={`text-lg font-semibold mt-2 ${
            monitoring ? "text-green-600" : "text-red-600"
          }`}
        >
          {monitoring ? "Monitoring..." : "Stopped"}
        </p>
      </div>

    </div>
  );
}

export default Stats;
