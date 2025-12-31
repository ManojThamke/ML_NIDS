function Stats({ stats, monitoring }) {
  const total = stats?.total || 0;
  const benign = stats?.benign || 0;
  const attack = stats?.attack || 0;

  return (
    <div className="grid grid-cols-4 gap-6 mb-8">

      {/* Total Packets */}
      <div className="bg-white rounded-xl p-5 border shadow-sm 
                  transition-all duration-300
                  hover:shadow-xl  hover:scale-[1.02]">
        <p className="text-sm text-gray-500">Total Packets Captured</p>
        <p className="text-3xl font-bold mt-2">{total}</p>
      </div>

      {/* Benign */}
      <div className="bg-green-50 rounded-xl p-5 border border-green-100
                  transition-all duration-300
                  hover:shadow-xl  hover:scale-[1.02]">
        <p className="text-sm text-green-700">Benign Traffic</p>
        <p className="text-3xl font-bold text-green-800 mt-2">
          {total ? ((benign / total) * 100).toFixed(1) : 0}%
        </p>
      </div>

      {/* Attack */}
      <div className="bg-red-50 rounded-xl p-5 border border-red-100
                  transition-all duration-300
                  hover:shadow-xl hover:scale-[1.02]">
        <p className="text-sm text-red-700">Attack Traffic</p>
        <p className="text-3xl font-bold text-red-800 mt-2">
          {total ? ((attack / total) * 100).toFixed(1) : 0}%
        </p>
      </div>

      {/* Live Status */}
      <div className="bg-white rounded-xl p-5 border shadow-sm
                  transition-all duration-300
                  hover:shadow-xl hover:scale-[1.02]">
        <p className="text-sm text-gray-500">Live Status</p>
        <p
          className={`text-lg font-semibold mt-2 ${monitoring ? "text-green-600" : "text-red-600"
            }`}
        >
          {monitoring ? "Monitoring..." : "Stopped"}
        </p>
      </div>

    </div>

  );
}

export default Stats;
