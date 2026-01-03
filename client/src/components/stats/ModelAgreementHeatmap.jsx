import React from "react";

/* 🎨 Color scale (SOC style) */
function getColor(value) {
  if (value >= 99) return "bg-green-600 text-white";
  if (value >= 95) return "bg-green-300 text-gray-900";
  if (value >= 85) return "bg-yellow-200 text-gray-900";
  if (value >= 70) return "bg-orange-200 text-gray-900";
  return "bg-red-300 text-gray-900";
}

function ModelAgreementHeatmap({ data }) {

  /* 🔐 HARD GUARD (prevents runtime crash) */
  if (
    !data ||
    !data.models ||
    !Array.isArray(data.models) ||
    data.models.length === 0 ||
    !data.matrix
  ) {
    return (
      <div className="bg-white rounded-xl p-6 shadow-sm border h-[300px] flex items-center justify-center">
        <p className="text-sm text-gray-400">
          Loading model agreement data…
        </p>
      </div>
    );
  }

  const { models, matrix } = data;

  return (
    <div className="bg-white rounded-xl p-6 shadow-sm border">
      <h3 className="font-semibold mb-4 text-gray-700">
        Model Agreement Heatmap
      </h3>

      <div
        className="grid gap-px"
        style={{
          gridTemplateColumns: `120px repeat(${models.length}, 1fr)`
        }}
      >
        {/* Column Header */}
        <div />
        {models.map(model => (
          <div
            key={model}
            className="text-xs text-center font-semibold text-gray-600 pb-2 "
          >
            {model}
          </div>
        ))}

        {/* Rows */}
        {models.map(row => (
          <React.Fragment key={row}>
            {/* Row Header */}
            <div className="text-xs font-semibold text-gray-600 flex items-center">
              {row}
            </div>

            {models.map(col => {
              const value = matrix[row]?.[col] ?? 0;
              const isDiagonal = row === col;

              return (
                <div
                  key={`${row}-${col}`}
                  className={`h-10 flex items-center justify-center text-xs font-medium
                    ${isDiagonal
                      ? "bg-gray-200 text-gray-700 font-semibold"
                      : getColor(value)
                    }`}
                >
                  {value}%
                </div>
              );
            })}
          </React.Fragment>
        ))}
      </div>

      {/* Legend */}
      <div className="flex justify-center gap-4 mt-4 text-xs text-gray-600">
        <span className="flex items-center gap-1">
          <span className="w-3 h-3 bg-green-600 rounded"></span> ≥99%
        </span>
        <span className="flex items-center gap-1">
          <span className="w-3 h-3 bg-green-300 rounded"></span> 95–99%
        </span>
        <span className="flex items-center gap-1">
          <span className="w-3 h-3 bg-yellow-200 rounded"></span> 85–95%
        </span>
        <span className="flex items-center gap-1">
          <span className="w-3 h-3 bg-orange-200 rounded"></span> 70–85%
        </span>
      </div>

      {/* Insight */}
      <p className="text-xs text-gray-500 text-center mt-3">
        Agreement percentage between models on final classification.
        High agreement indicates stable ensemble behavior.
      </p>
    </div>
  );
}

export default ModelAgreementHeatmap;
