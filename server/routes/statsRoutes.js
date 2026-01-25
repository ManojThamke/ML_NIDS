const express = require("express");
const router = express.Router();

const {
  getDetectionDistribution,
  getConfidenceBands,
  getPerModelAverageConfidence,
  getModelDominanceFrequency,
  getModelAgreementMatrix,
  getEnsembleVsBestModel,
  getAttackTimeline,
  getTopAttackedDestinations,
} = require("../controllers/statsController");

/* DISTRIBUTION */
router.get("/distribution", getDetectionDistribution);

/* CONFIDENCE */
router.get("/confidence/bands", getConfidenceBands);
router.get("/confidence/per-model", getPerModelAverageConfidence);
router.get("/confidence/ensemble-vs-best", getEnsembleVsBestModel);

/* MODEL BEHAVIOR */
router.get("/models/dominance", getModelDominanceFrequency);
router.get("/models/agreement", getModelAgreementMatrix);

/* ATTACK INTELLIGENCE */
router.get("/attacks/timeline", getAttackTimeline);
router.get("/attacks/top-destinations", getTopAttackedDestinations);

module.exports = router;
