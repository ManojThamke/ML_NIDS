import React from "react";
import ControlStats from "../components/ControlStats";
import AttackBenignDonut from "../components/charts/AttackBenignDonut";
import AttackConfidenceArea from "../components/charts/AttackConfidenceArea";
import EnsembleVotingStatus from "../components/EnsembleVotingStatus"; // New Component
import TrafficTimelineChart from "../components/charts/TrafficTimelineChart";
import TopAttackedDestinationsChart from "../components/charts/TopAttackedDestinationsChart";
import DetectionTable from "../components/DetectionTable";

function Dashboard({ alerts, stats, monitoring, setMonitoring }) {
  return (
    <div className="p-4 space-y-8 bg-gray-50/30 min-h-screen">
      
      {/* 🚀 No Header here anymore - it is now handled by Topbar.jsx */}

      {/* Stats Cards Section */}
      <ControlStats stats={stats} monitoring={monitoring} />

      {/* Primary Row — FULLY BALANCED (3-6-3) */}
      <div className="grid grid-cols-12 gap-6 items-stretch">
        <div className="col-span-12 lg:col-span-3">
          <AttackBenignDonut stats={stats} />
        </div>

        <div className="col-span-12 lg:col-span-6">
          <AttackConfidenceArea alerts={alerts} />
        </div>

        <div className="col-span-12 lg:col-span-3">
          <EnsembleVotingStatus monitoring={monitoring} />
        </div>
      </div>

      {/* Secondary Row — Temporal & Asset (8-4) */}
      <div className="grid grid-cols-12 gap-6 items-stretch">
        <div className="col-span-12 lg:col-span-8">
          <TrafficTimelineChart />
        </div>
        <div className="col-span-12 lg:col-span-4">
          <TopAttackedDestinationsChart />
        </div>
      </div>

      {/* Forensic Table Section */}
      <DetectionTable />
    </div>
  );
}

export default Dashboard;