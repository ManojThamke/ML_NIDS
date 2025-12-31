import { useEffect, useState } from "react";
import {
    getDetectionDistribution,
    getProbabilityBands,
} from "../../api";

import DetectionDistributionDonut from "./DetectionDistributionDonut";
import ProbabilityConfidenceBands from "./ProbabilityConfidenceBands";

function GlobalSecurityOverview() {
    const [distribution, setDistribution] = useState(null);
    const [bands, setBands] = useState([]);

    useEffect(() => {
        getDetectionDistribution()
            .then((res) => setDistribution(res.data))
            .catch(console.error);

        getProbabilityBands()
            .then((res) => setBands(res.data))
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
        <div className="grid grid-cols-12 gap-6">
            <div className="col-span-3">
                <DetectionDistributionDonut data={distribution} />
            </div>
            <div className="col-span-6">
                <ProbabilityConfidenceBands data={bands} />
            </div>
        </div>
    );
}

export default GlobalSecurityOverview;
