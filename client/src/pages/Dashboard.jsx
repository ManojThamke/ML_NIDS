import MonitoringControl from "../components/MonitoringControl";
import Stats from "../components/Stats";
import AttackBenignDonut from "../components/charts/AttackBenignDonut";
import AttackProbabilityArea from "../components/charts/AttackProbabilityArea";
import AlertsTable from "../components/AlertsTable";
import ModelComparisonChart from "../components/charts/ModelComparisonChart";

function Dashboard({ alerts, stats, monitoring, setMonitoring }) {
  return (
    <div className="p-8 space-y-6">

      {/* Start / Stop Monitoring */}
      <MonitoringControl
        monitoring={monitoring}
        setMonitoring={setMonitoring}
      />

      {/* Stats Cards */}
      <Stats stats={stats} monitoring={monitoring} />

      {/* Charts Row — EXACTLY 3 CHARTS */}
      <div className="grid grid-cols-12 gap-6">

        {/* Donut */}
        <div className="col-span-3">
          <AttackBenignDonut type="donut" alerts={alerts} stats={stats} />
        </div>

        {/* Line */}
        <div className="col-span-4">
          <AttackProbabilityArea alerts={alerts} />
        </div>

        {/* Bar (ONLY ONCE) */}
        <div className="col-span-5">
          <ModelComparisonChart />
        </div>

      </div>

      {/* Live Traffic Table */}
      <AlertsTable />

    </div>
  );
}

export default Dashboard;
