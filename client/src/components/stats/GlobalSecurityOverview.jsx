import React, { useEffect, useState } from "react";
import {
  getDetectionDistribution,
  getConfidenceBands,
  getPerModelAverageConfidence,
  getModelDominanceFrequency,
  getModelAgreementMatrix,
  getEnsembleVsBestModel,
  getAttackTimeline,
  getTopAttackedDestinations,
} from "../../api";

import DetectionDistributionDonut from "./DetectionDistributionDonut";
import ProbabilityConfidenceBands from "./ConfidenceBandsChart";
import PerModelAverageConfidence from "./PerModelAverageConfidence";
import ModelDominanceFrequencyChart from "./ModelDominanceFrequency";
import ModelAgreementHeatmap from "./ModelAgreementHeatmap";
import EnsembleVsBestModelChart from "./EnsembleVsBestModel";
import AttackTimelineChart from "./AttackTimelineChart";
import TopAttackedDestinationsChart from "./TopAttackedDestinationsChart";

/**
 * GlobalSecurityOverview V2.0
 * Features: Staggered NOC entrance animations and theme-adaptive grid layout.
 */
function GlobalSecurityOverview({ theme = 'light' }) {
  const [distribution, setDistribution] = useState(null);
  const [bands, setBands] = useState([]);
  const [avgprob, setAvgProb] = useState([]);
  const [dominance, setDominance] = useState([]);
  const [agreement, setAgreement] = useState({ models: [], matrix: {} });
  const [ensembleCompare, setEnsembleCompare] = useState([]);
  const [timeline, setTimeline] = useState([]);
  const [topDestinations, setTopDestinations] = useState([]);

  useEffect(() => {
    // Concurrent Data Acquisition
    Promise.all([
      getDetectionDistribution().then(res => setDistribution(res.data)),
      getConfidenceBands().then(res => setBands(res.data)),
      getPerModelAverageConfidence().then(res => setAvgProb(res.data)),
      getModelDominanceFrequency().then(res => setDominance(res.data)),
      getModelAgreementMatrix().then(res => setAgreement(res.data)).catch(() => setAgreement({ models: [], matrix: {} })),
      getEnsembleVsBestModel().then(res => setEnsembleCompare(res.data)),
      getAttackTimeline("24h").then(res => setTimeline(res.data)),
      getTopAttackedDestinations(5).then(res => setTopDestinations(res.data))
    ]).catch(err => console.error("Global Intelligence Retrieval Failure:", err));
  }, []);

  if (!distribution) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] space-y-4">
        <div className="w-12 h-12 border-4 border-indigo-500/20 border-t-indigo-500 rounded-full animate-spin" />
        <p className="text-[11px] font-black uppercase tracking-[0.3em] text-slate-400 animate-pulse">
          Synchronizing Global Security Matrix...
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-12 max-w-[1700px] mx-auto pb-12">

      {/* 🛡️ SECTION 1 — GLOBAL OVERVIEW */}
      <section className="space-y-6">
        <Header label="Global Intelligence Matrix" sublabel="Real-time hybrid detection distribution & certainty bands" />
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 animate-in fade-in slide-in-from-bottom-4 duration-700 fill-mode-both">
          <DetectionDistributionDonut data={distribution} theme={theme} />
          <ProbabilityConfidenceBands data={bands} theme={theme} />
        </div>
      </section>

      {/* 🧠 SECTION 2 — MODEL INTELLIGENCE */}
      <section className="space-y-8">
        <Header label="Ensemble Logic Analytics" sublabel="Model consensus heatmaps & cross-validation stability" />
        <div className="space-y-8">
          {/* Row 1: Model Stats */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 animate-in fade-in slide-in-from-bottom-4 duration-700 delay-200 fill-mode-both">
            <PerModelAverageConfidence data={avgprob} theme={theme} />
            <ModelDominanceFrequencyChart data={dominance} theme={theme} />
          </div>

          {/* Row 2: Deep Forensics */}
          <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700 delay-300 fill-mode-both">
            <ModelAgreementHeatmap data={agreement} theme={theme} />
            <EnsembleVsBestModelChart data={ensembleCompare} theme={theme} />
          </div>
        </div>
      </section>

      {/* 🚨 SECTION 3 — ATTACK BEHAVIOR */}
      <section className="space-y-6">
        <Header label="Threat Propagation Matrix" sublabel="Temporal anomaly tracking & asset vulnerability profiling" />
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 animate-in fade-in slide-in-from-bottom-4 duration-700 delay-500 fill-mode-both">
          <AttackTimelineChart data={timeline} theme={theme} />
          <TopAttackedDestinationsChart data={topDestinations} theme={theme} />
        </div>
      </section>

    </div>
  );
}

/* ===================== Helper UI Components ===================== */

function Header({ label, sublabel }) {
  return (
    <div className="px-2 border-l-4 border-indigo-500 py-1">
      <h2 className="text-sm font-black uppercase tracking-[0.2em] text-slate-800 dark:text-white">
        {label}
      </h2>
      <p className="text-[11px] font-bold text-indigo-500/70 uppercase tracking-widest mt-1">
        {sublabel}
      </p>
    </div>
  );
}

export default GlobalSecurityOverview;