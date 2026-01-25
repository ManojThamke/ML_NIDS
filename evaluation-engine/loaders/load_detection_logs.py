from datetime import datetime
from typing import Optional
import pandas as pd


def load_detection_logs(
    collection,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
) -> pd.DataFrame:
    """
    Load and normalize detection logs from MongoDB.
    """

    query = {}

    if start_time or end_time:
        query["createdAt"] = {}
        if start_time:
            query["createdAt"]["$gte"] = start_time
        if end_time:
            query["createdAt"]["$lte"] = end_time

    cursor = collection.find(query)

    records = []

    for doc in cursor:
        records.append({
            "timestamp": doc.get("createdAt"),
            "finalLabel": doc.get("finalLabel"),
            "confidence": doc.get("confidence"),
            "severity": doc.get("severity"),
            "attackVotes": doc.get("attackVotes"),
            "totalModels": doc.get("totalModels"),
            "threshold": doc.get("threshold"),  # ✅ ADDED
            "aggregationMethod": doc.get("aggregationMethod"),
            "modelProbabilities": doc.get("modelProbabilities", {}),
        })


    df = pd.DataFrame(records)

    if df.empty:
        print("⚠️ No detection logs found")
    else:
        print(f"✅ Loaded {len(df)} detection logs")

    return df
