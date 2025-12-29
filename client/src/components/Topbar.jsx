import { useLocation } from "react-router-dom";

function Topbar({ monitoring }) {
  const location = useLocation();

  // 🔹 Dynamic title based on route
  const getTitle = () => {
    switch (location.pathname) {
      case "/":
        return "ML-NIDS Dashboard";
      case "/logs":
        return "Traffic Logs";
      case "/stats":
        return "Statistics & Insights";
      case "/models":
        return "Models & Performance";
      case "/settings":
        return "System Settings";
      default:
        return "ML-NIDS";
    }
  };

  return (
    <div className="flex justify-between items-center px-6 py-4 border-b bg-white">
      
      {/* 🔹 Dynamic Page Title */}
      <h1 className="text-xl font-semibold text-gray-800">
        {getTitle()}
      </h1>

      <div className="flex items-center gap-3">

        {/* 🔵 STATUS INDICATOR WRAPPER */}
        <div className="relative flex items-center justify-center w-5 h-5">

          {/* 🌊 Ripple Waves (only when monitoring ON) */}
          {monitoring && (
            <>
              <span className="absolute w-5 h-5 rounded-full bg-green-400 opacity-40 animate-ping" />
              <span className="absolute w-8 h-8 rounded-full bg-green-300 opacity-20 animate-ping delay-150" />
            </>
          )}

          {/* 🟢 / 🔴 Center Dot */}
          <span
            className={`relative w-3 h-3 rounded-full ${
              monitoring ? "bg-green-500" : "bg-red-500"
            }`}
          />
        </div>

        {/* 🔵 Status Text */}
        <span
          className={`text-sm font-medium ${
            monitoring ? "text-green-600" : "text-red-600"
          }`}
        >
          {monitoring ? "Live Monitoring" : "Monitoring Stopped"}
        </span>
      </div>
    </div>
  );
}

export default Topbar;
