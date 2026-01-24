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

/**
 * ================================
 * DISTRIBUTION
 * ================================
 */
router.get("/detection-distribution", getDetectionDistribution);

/**
 * ================================
 * CONFIDENCE ANALYTICS
 * ================================
 */
router.get("/confidence-bands", getConfidenceBands);
router.get("/model-avg-confidence", getPerModelAverageConfidence);
router.get("/ensemble-vs-best", getEnsembleVsBestModel);

/**
 * ================================
 * MODEL BEHAVIOR ANALYTICS
 * ================================
 */
router.get("/model-dominance-frequency", getModelDominanceFrequency);
router.get("/model-agreement", getModelAgreementMatrix);

/**
 * ================================
 * ATTACK INTELLIGENCE
 * ================================
 */
router.get("/attack-timeline", getAttackTimeline);
router.get("/top-attacked-destinations", getTopAttackedDestinations);

module.exports = router;
