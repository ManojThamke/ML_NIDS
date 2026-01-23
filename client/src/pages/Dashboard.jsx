import MonitoringControl from "../components/MonitoringControl";
import ControlStats from "../components/ControlStats";
import AttackBenignDonut from "../components/charts/AttackBenignDonut";
import AttackProbabilityArea from "../components/charts/AttackProbabilityArea";
// import ModelComparisonChart from "../components/charts/ModelComparisonChart";
import TrafficTimelineChart from "../components/charts/TrafficTimelineChart";
import TopAttackedDestinationsChart from "../components/charts/TopAttackedDestinationsChart";
import DetectionTable from "../components/DetectionTable";
function Dashboard({ alerts, stats, monitoring, setMonitoring }) {
  return (
    <div className="p-8 space-y-6">

      {/* Start / Stop Monitoring */}
      <MonitoringControl
        monitoring={monitoring}
        setMonitoring={setMonitoring}
      />

      {/* Stats Cards */}
      <ControlStats stats={stats} monitoring={monitoring} />
      {/* Charts Row — EXACTLY 3 CHARTS */}
      <div className="grid grid-cols-12 gap-6">

        {/* Donut */}
        <div className="col-span-3">
          <AttackBenignDonut type="donut" alerts={alerts} stats={stats} />
        </div>

        {/* Line */}
        <div className="col-span-9">
          <AttackProbabilityArea alerts={alerts} />
        </div>

        {/* Bar (ONLY ONCE) */}
        {/* <div className="col-span-5">
          <ModelComparisonChart />
        </div> */}

        <div className="col-span-8">
          <TrafficTimelineChart />
        </div>
        <div className="col-span-4">
          <TopAttackedDestinationsChart />
        </div>
        
        

      </div>

      {/* Live Traffic Table */}
      <DetectionTable />

    </div>
  );
}

export default Dashboard;
