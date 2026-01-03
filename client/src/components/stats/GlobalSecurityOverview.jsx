import { useEffect, useState } from "react";
import {
  getDetectionDistribution,
  getProbabilityBands,
  getPerModelAverageProbability,
  getModelDominanceFrequency,
  getModelAgreementMatrix,
  getEnsembleVsBestModel,
  getAttackTimeline,
  getTopAttackedDestinations,
} from "../../api";

import DetectionDistributionDonut from "./DetectionDistributionDonut";
import ProbabilityConfidenceBands from "./ProbabilityConfidenceBands";
import PerModelAverageProbabilityChart from "./PerModelAverageProbability";
import ModelDominanceFrequencyChart from "./ModelDominanceFrequency";
import ModelAgreementHeatmap from "./ModelAgreementHeatmap";
import EnsembleVsBestModelChart from "./EnsembleVsBestModel";
import AttackTimelineChart from "./AttackTimelineChart";
import TopAttackedDestinationsChart from "./TopAttackedDestinationsChart";

function GlobalSecurityOverview() {
  const [distribution, setDistribution] = useState(null);
  const [bands, setBands] = useState([]);
  const [avgprob, setAvgProb] = useState([]);
  const [dominance, setDominance] = useState([]);
  const [agreement, setAgreement] = useState({ models: [], matrix: {} });
  const [ensembleCompare, setEnsembleCompare] = useState([]);
  const [timeline, setTimeline] = useState([]);
  const [topDestinations, setTopDestinations] =useState([]);

  useEffect(() => {
    getDetectionDistribution()
      .then(res => setDistribution(res.data))
      .catch(console.error);

    getProbabilityBands()
      .then(res => setBands(res.data))
      .catch(console.error);

    getPerModelAverageProbability()
      .then(res => setAvgProb(res.data))
      .catch(console.error);

    getModelDominanceFrequency()
      .then(res => setDominance(res.data))
      .catch(console.error);

    getModelAgreementMatrix()
      .then(res => setAgreement(res.data))
      .catch(err => {
        console.error("Agreement matrix error:", err);
        setAgreement({ models: [], matrix: {} });
      });

    getEnsembleVsBestModel()
      .then(res => setEnsembleCompare(res.data))
      .catch(console.error);

    // ⏱ Use wider window for meaningful timeline
    getAttackTimeline("24h")
      .then(res => setTimeline(res.data))
      .catch(console.error);

    getTopAttackedDestinations(5)
      .then(res => setTopDestinations(res.data))
      .catch(console.error);
  }, []);

  if (!distribution) {
    return (
      <p className="text-sm text-gray-500">
        Loading security overview…
      </p>
    );
  }

  return (
    <div className="space-y-10">

      {/* =======================
          SECTION 1 — GLOBAL OVERVIEW
      ======================= */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <DetectionDistributionDonut data={distribution} />
        <ProbabilityConfidenceBands data={bands} />
      </div>

      {/* =======================
          SECTION 2 — MODEL INTELLIGENCE
      ======================= */}
      <div className="space-y-6">
        {/* Row 1 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <PerModelAverageProbabilityChart data={avgprob} />
          <ModelDominanceFrequencyChart data={dominance} />
        </div>

        {/* Row 2 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <ModelAgreementHeatmap data={agreement} />
          <EnsembleVsBestModelChart data={ensembleCompare} />
        </div>
      </div>

      {/* =======================
          SECTION 3 — ATTACK BEHAVIOR
      ======================= */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <AttackTimelineChart data={timeline} />
        <TopAttackedDestinationsChart data={topDestinations}/>
      </div>

    </div>
  );
}

export default GlobalSecurityOverview;
