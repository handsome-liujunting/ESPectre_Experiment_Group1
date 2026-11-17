"""Replay one labeled or unlabeled CSI amplitude recording with a fitted model."""
import argparse
import csv
import json
from pathlib import Path
import sys

import numpy as np

LABELS = ("idle", "static_presence", "motion")
STRESS = ("interference_fan", "interference_curtain", "interference_corridor",
          "interference_balcony")
FEATURE_VERSION = 1


def windows(path):
    """Return a one-second grid and log-transformed subband features."""
    with np.load(path, allow_pickle=False) as source:
        amplitude = source["csi_data"]
        if amplitude.ndim != 2 or amplitude.shape[1] != 64:
            raise ValueError(f"Expected 64 CSI amplitudes per packet: {path}")
        if not np.isfinite(amplitude).all() or np.any(amplitude < 0):
            raise ValueError(f"Invalid CSI amplitudes: {path}")
        timestamp = source["timestamps"].astype(float)
    if (not len(amplitude) or timestamp.shape != (len(amplitude),)
            or not np.isfinite(timestamp).all() or np.any(np.diff(timestamp) <= 0)):
        raise ValueError(f"Expected strictly increasing packet timestamps: {path}")
    timestamp -= timestamp[0]
    # Include the final bin when at least 0.7 s of it was observed.
    end = np.arange(1, int(timestamp[-1] + 0.3) + 1)
    boundaries = np.searchsorted(timestamp, np.arange(len(end) + 1))
    result = np.full((len(end), 16), np.nan)
    for index, (first, last) in enumerate(zip(boundaries, boundaries[1:])):
        times = timestamp[first:last]
        if len(times) < 4 or times[-1] - times[0] < 0.7 - 1e-9:
            continue
        values = amplitude[first:last].astype(float)
        # Temporal variability per carrier, aggregated over eight contiguous bands.
        spread = values.std(axis=0)
        mean = values.mean(axis=0)
        relative = np.divide(spread, mean, out=np.zeros(64), where=mean > 0)
        result[index] = np.log1p(np.r_[spread.reshape(8, 8).mean(axis=1),
                                     relative.reshape(8, 8).mean(axis=1)])
    return end, result


def states(probability):
    state = "UNKNOWN"
    ema = None
    above = below = missing = 0
    for value in probability:
        if not np.isfinite(value):
            missing += 1
            above = below = 0
            if missing >= 5:
                state = "UNKNOWN"
                ema = None
            yield "UNKNOWN", state
            continue
        missing = 0
        ema = value if ema is None else 0.3 * value + 0.7 * ema
        above = above + 1 if ema >= 0.60 else 0
        below = below + 1 if ema <= 0.40 else 0
        if above >= 2:
            state = "OCCUPIED"
        if below >= 10:
            state = "UNOCCUPIED"
        yield state, state


def predict(model, features):
    valid = np.isfinite(features).all(axis=1)
    probs = np.full((len(features), len(LABELS)), np.nan)
    logits = ((features[valid] - model["mean"]) / model["scale"]
              @ np.asarray(model["coefficient"]).T + model["intercept"])
    logits -= logits.max(axis=1, keepdims=True)
    exp = np.exp(logits)
    probs[valid] = exp / exp.sum(axis=1, keepdims=True)
    return probs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", required=True, type=Path)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    model = json.loads(args.model.read_text(encoding="utf-8"))
    if model["feature_version"] != FEATURE_VERSION or model["labels"] != list(LABELS):
        parser.error("Unsupported feature schema or model label order.")
    end, features = windows(args.input)
    prob = predict(model, features)
    score = prob[:, 1:].sum(axis=1)
    rows = [
        (second, f"{value:.6f}" if np.isfinite(value) else "", instant, stable)
        for second, value, (instant, stable) in zip(end, score, states(score))
    ]
    handle = args.output.open("w", encoding="utf-8", newline="") if args.output else sys.stdout
    try:
        writer = csv.writer(handle)
        writer.writerow(("end_s", "occupancy_probability", "decision", "stable_state"))
        writer.writerows(rows)
    finally:
        if args.output:
            handle.close()


if __name__ == "__main__":
    main()
