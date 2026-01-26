import { useEffect, useRef, useState } from "react";

/* ================= COUNT-UP HOOK (ONCE ONLY) ================= */
function useCountUp(target, duration = 800) {
  const [value, setValue] = useState(0);
  const hasAnimated = useRef(false);

  useEffect(() => {
    if (hasAnimated.current) {
      setValue(target);
      return;
    }

    hasAnimated.current = true;
    let startTime = null;

    const animate = (timestamp) => {
      if (!startTime) startTime = timestamp;
      const progress = Math.min((timestamp - startTime) / duration, 1);
      setValue(target * progress);
      if (progress < 1) requestAnimationFrame(animate);
    };

    requestAnimationFrame(animate);
  }, [target, duration]);

  return value;
}

function Stats({ stats, monitoring }) {
  const total = stats?.total || 0;
  const benign = stats?.benign || 0;
  const attack = stats?.attack || 0;

  const benignPercent = total ? (benign / total) * 100 : 0;
  const attackPercent = total ? (attack / total) * 100 : 0;

  const animatedTotal = useCountUp(total);
  const animatedBenign = useCountUp(benignPercent);
  const animatedAttack = useCountUp(attackPercent);

  return (
    <div className="mb-10">

      {/* ================= KPI CARDS ================= */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">

        {/* 🔵 Total Packets */}
        <div className="
          group relative bg-blue-50 rounded-2xl p-6 border border-blue-100
          shadow-sm transition-all duration-300
          hover:shadow-lg hover:-translate-y-0.5
        ">
          {/* Top animated line */}
          <div
            className="
              absolute top-3 left-1/2 -translate-x-1/2
              h-[2px] w-16 bg-blue-400 rounded-full
              transition-all duration-300 ease-in-out
              origin-center group-hover:w-28
            "
          />


          <p className="text-sm font-medium text-blue-700">
            Total Packets Captured
          </p>
          <p className="text-3xl font-extrabold text-blue-800 mt-3">
            {Math.round(animatedTotal)}
          </p>
        </div>

        {/* 🟢 Benign */}
        <div className="
          group relative bg-green-50 rounded-2xl p-6 border border-green-100
          shadow-sm transition-all duration-300
          hover:shadow-lg hover:-translate-y-0.5
        ">
          <div
            className="
              absolute top-3 left-1/2 -translate-x-1/2
              h-[2px] w-16 bg-green-400 rounded-full
              transition-all duration-300 ease-in-out
              origin-center group-hover:w-28
            "
          />

          <p className="text-sm font-medium text-green-700">
            Benign Traffic
          </p>
          <p className="text-3xl font-extrabold text-green-800 mt-3">
            {animatedBenign.toFixed(1)}%
          </p>
        </div>

        {/* 🔴 Attack */}
        <div className="
          group relative bg-red-50 rounded-2xl p-6 border border-red-100
          shadow-sm transition-all duration-300
          hover:shadow-lg hover:-translate-y-0.5
        ">
          <div className="
            absolute top-3 left-1/2 -translate-x-1/2
            h-[2px] w-16 bg-red-400 rounded-full
            transition-all duration-300 ease-in-out
            origin-center
            group-hover:w-28
          " />

          <p className="text-sm font-medium text-red-700">
            Attack Traffic
          </p>
          <p className="text-3xl font-extrabold text-red-800 mt-3">
            {animatedAttack.toFixed(1)}%
          </p>
        </div>

        {/* 🟣 / 🟢 Live Status (System State, NOT Traffic) */}
        <div className={`
          group relative rounded-2xl p-6 border shadow-sm
          transition-all duration-300
          hover:shadow-lg hover:-translate-y-0.5
          ${monitoring
                    ? "bg-teal-25 border-teal-100"
                    : "bg-amber-50 border-amber-200"
                  }
        `}>
          {/* Top animated line */}
          <div
              className={`
                absolute top-3 left-1/2 -translate-x-1/2
                h-[2px] w-16 rounded-full
                transition-all duration-300 ease-in-out
                origin-center group-hover:w-28
                ${monitoring
                          ? "bg-teal-400"
                          : "bg-amber-400"
                        }
            `}
          />
          <p
            className={`text-sm font-medium ${monitoring ? "text-teal-700" : "text-amber-700"
              }`}
          >
            Live Status
          </p>

          <span
            className={`
            inline-block mt-3 px-3 py-1.5 rounded-full text-xs font-semibold
            ${monitoring
                      ? "bg-teal-100 text-teal-700"
                      : "bg-amber-100 text-amber-700"
                    }
          `}
          >
            {monitoring ? "Detection Engine Running..." : "Detection Engine STOPPED"}
          </span>
        </div>


      </div>
    </div>
  );
}

export default Stats;
