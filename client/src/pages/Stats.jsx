import GlobalSecurityOverview from "../components/stats/GlobalSecurityOverview";

function Stats() {
  return (
    <div className="p-8 space-y-6">
      <h1 className="text-2xl font-bold">
        Security Statistics
      </h1>

      <GlobalSecurityOverview />
    </div>
  );
}

export default Stats;
