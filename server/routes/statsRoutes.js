const express = require("express");
const router = express.Router();
const {
    getDetectionDistribution,
    getProbabilityBands,
    getPerModelAverageProbability,
    getModelDominanceFrequency,
    getModelAgreementMatrix,
    getEnsembleVsBestModel,
    getAttackTimeline,
    getTopAttackedDestinations,
} = require("../controllers/statsController");

router.get("/detection-distribution", getDetectionDistribution);
router.get("/probability-bands", getProbabilityBands);
router.get("/model-avg-probability", getPerModelAverageProbability);
router.get("/model-dominance-frequency", getModelDominanceFrequency);
router.get("/model-agreement", getModelAgreementMatrix);
router.get("/ensemble-vs-best", getEnsembleVsBestModel);
router.get("/attack-timeline", getAttackTimeline);
router.get("/top-attacked-destination", getTopAttackedDestinations);


module.exports = router;
