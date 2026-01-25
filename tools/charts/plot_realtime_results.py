#!/usr/bin/env python3
"""
Plot realtime detection results.

Usage:
  python tools/plot_realtime_results.py --csv logs/realtime_predictions_ensemble.csv

Outputs (saved to docs/figures/):
  - agg_prob_timeseries.png      (aggregated probability + alert markers)
  - per_model_probs.png          (per-model probability lines)
  - alerts_per_minute.png        (alerts histogram)
"""
import os
import json
import argparse
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt

def ensure_dir(p):
    d = os.path.dirname(p)
    if d and not os.path.exists(d):
        os.makedirs(d, exist_ok=True)

def parse_per_model(col):
    """col is JSON string or dict -> return dict of model:prob"""
    if pd.isna(col) or col == "" or col is None:
        return {}
    try:
        if isinstance(col, str):
            return json.loads(col)
        elif isinstance(col, dict):
            return col
    except Exception:
        # try replacing single quotes
        try:
            return json.loads(col.replace("'", '"'))
        except Exception:
            return {}
    return {}

def main(csv_path, out_dir):
    df = pd.read_csv(csv_path, low_memory=False)
    # Try common timestamp column names
    ts_col = None
    for c in ("timestamp","time","ts"):
        if c in df.columns:
            ts_col = c
            break
    if ts_col is None:
        raise SystemExit("No timestamp column found in CSV. Expected column named 'timestamp'")

    # parse timestamps
    def to_dt(v):
        try:
            return pd.to_datetime(v)
        except Exception:
            try:
                return pd.to_datetime(str(v))
            except Exception:
                return pd.NaT
    df["ts_dt"] = df[ts_col].apply(to_dt)
    df = df.dropna(subset=["ts_dt"]).reset_index(drop=True)

    # aggregated probability
    agg_col = None
    for c in ("agg_prob","aggprob","prob","proba"):
        if c in df.columns:
            agg_col = c
            break
    if agg_col is None:
        # try 'prob' or 'probability' first found
        agg_col = [c for c in df.columns if "prob" in c.lower()]
        agg_col = agg_col[0] if agg_col else None
    if agg_col is None:
        raise SystemExit("No aggregated probability column found (agg_prob etc.)")

    # alert column
    alert_col = None
    for c in ("alert","is_alert"):
        if c in df.columns:
            alert_col = c
            break

    # parse per_model JSON if present
    per_model_col = None
    for c in ("per_model","per-model","permodel","models"):
        if c in df.columns:
            per_model_col = c
            break

    per_model_df = None
    if per_model_col:
        # expand JSON dict column into dataframe
        expanded = df[per_model_col].apply(parse_per_model)
        per_model_df = pd.DataFrame(list(expanded))
        # align index
        per_model_df.index = df.index

    # Prepare out_dir
    ensure_dir(out_dir)
    fig1 = os.path.join(out_dir, "agg_prob_timeseries.png")
    fig2 = os.path.join(out_dir, "per_model_probs.png")
    fig3 = os.path.join(out_dir, "alerts_per_minute.png")

    # ----- Figure 1: aggregated probability time series -----
    plt.figure(figsize=(12,4))
    plt.plot(df["ts_dt"], df[agg_col].astype(float), label="agg_prob")
    if alert_col:
        alert_times = df[df[alert_col].astype(int) == 1]["ts_dt"]
        alert_vals = df[df[alert_col].astype(int) == 1][agg_col].astype(float)
        plt.scatter(alert_times, alert_vals, color="red", s=40, label="alert", zorder=5)
    plt.title("Aggregated Attack Probability — Time series 🚨")
    plt.xlabel("Timestamp")
    plt.ylabel("Aggregated probability")
    plt.grid(alpha=0.2)
    plt.legend()
    plt.tight_layout()
    plt.savefig(fig1)
    print("Saved:", fig1)
    plt.show()

    # ----- Figure 2: per-model probabilities -----
    if per_model_df is not None and not per_model_df.dropna(how="all").empty:
        plt.figure(figsize=(12,4))
        # plot each model line
        for col in per_model_df.columns:
            try:
                plt.plot(df["ts_dt"], per_model_df[col].astype(float), label=str(col))
            except Exception:
                pass
        plt.title("Per-model probabilities (LGB / RF / XGB / SVM ...) 📈")
        plt.xlabel("Timestamp")
        plt.ylabel("Probability")
        plt.grid(alpha=0.2)
        plt.legend(ncol=2, fontsize="small")
        plt.tight_layout()
        plt.savefig(fig2)
        print("Saved:", fig2)
        plt.show()
    else:
        print("No per-model data to plot (per_model column missing/empty).")

    # ----- Figure 3: alerts per minute histogram -----
    if alert_col:
        df["minute"] = df["ts_dt"].dt.floor("T")
        alerts_per_min = df[df[alert_col].astype(int) == 1].groupby("minute").size()
        plt.figure(figsize=(10,4))
        alerts_per_min.plot(kind="bar")
        plt.title("Alert counts per minute 📊")
        plt.xlabel("Minute")
        plt.ylabel("Number of alerts")
        plt.tight_layout()
        plt.savefig(fig3)
        print("Saved:", fig3)
        plt.show()
    else:
        print("No alert column found; skipping alerts-per-minute chart.")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--csv", required=True, help="Path to realtime CSV (e.g. logs/realtime_predictions_ensemble.csv)")
    p.add_argument("--out", default="docs/figures", help="Output folder for saved charts")
    args = p.parse_args()
    main(args.csv, args.out)