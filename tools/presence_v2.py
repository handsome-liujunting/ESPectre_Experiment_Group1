"""Fit or replay the dorm-room pilot using normalized temporal CSI features."""
import argparse
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
import sys

import numpy as np

from presence import states


def extract(path):
    with np.load(path, allow_pickle=False) as capture:
        iq = capture["iq_raw"]
        times = capture["timestamps"].astype(float)
    if (times.ndim != 1 or len(times) < 2 or iq.shape != (len(times), 128)
            or not np.isfinite(times).all() or not np.isfinite(iq).all()
            or (np.diff(times) <= 0).any()):
        raise ValueError("Expected timestamped 64-subcarrier raw I/Q data")
    times -= times[0]
    amplitude = np.linalg.norm(iq.reshape(-1, 64, 2).astype(float), axis=2)
    shape = amplitude / np.maximum(np.linalg.norm(amplitude, axis=1, keepdims=True), 1)
    limit = int(times[-1] + 0.3)
    boundaries = np.searchsorted(times, np.arange(limit + 1))
    features = np.full((limit, 16), np.nan)
    for i, (start, stop) in enumerate(zip(boundaries, boundaries[1:])):
        if stop - start < 4 or times[stop - 1] - times[start] < 0.7:
            continue
        block = shape[start:stop]
        spread = block.std(axis=0).reshape(8, 8).mean(axis=1)
        change = np.abs(np.diff(block, axis=0)).mean(axis=0).reshape(8, 8).mean(axis=1)
        features[i] = np.r_[spread, change]
    return features


def fit(captures):
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler

    samples = []
    targets = []
    source = {}
    for target, files in enumerate(captures):
        for path in files:
            values = extract(path)
            values = values[np.isfinite(values).all(axis=1)]
            samples.append(values)
            targets.extend([target] * len(values))
            source[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    x = np.concatenate(samples)
    scaler = StandardScaler().fit(x)
    classifier = LogisticRegression(random_state=42).fit(scaler.transform(x), targets)
    return dict(feature_version=2, seed=42, status="pilot", sources=source,
                mean=scaler.mean_.tolist(), scale=scaler.scale_.tolist(),
                coefficient=classifier.coef_[0].tolist(), intercept=float(classifier.intercept_[0]))


def replay(model, path):
    features = extract(path)
    score = np.full(len(features), np.nan)
    valid = np.isfinite(features).all(axis=1)
    logits = (features[valid] - model["mean"]) / model["scale"] @ model["coefficient"]
    score[valid] = np.exp(-np.logaddexp(0, -(logits + model["intercept"])))
    return [(i, f"{p:.6f}" if np.isfinite(p) else "", decision, stable)
            for i, (p, (decision, stable)) in enumerate(zip(score, states(score)), 1)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    trainer = commands.add_parser("train")
    trainer.add_argument("--idle", type=Path, nargs="+", required=True)
    trainer.add_argument("--seated", type=Path, nargs="+", required=True)
    tester = commands.add_parser("replay")
    tester.add_argument("--input", type=Path, required=True)
    tester.add_argument("--output", type=Path)
    for command in (trainer, tester):
        command.add_argument("--model", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "train":
        model = fit((args.idle, args.seated))
        args.model.write_text(json.dumps(model, indent=2) + "\n", encoding="utf-8")
        return
    model = json.loads(args.model.read_text(encoding="utf-8"))
    if model["feature_version"] != 2:
        parser.error("Expected feature version 2")
    rows = replay(model, args.input)
    if args.output:
        with args.output.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(("end_s", "occupancy_probability", "decision", "stable_state"))
            writer.writerows(rows)
        print(dict(Counter(row[2] for row in rows)))
    else:
        writer = csv.writer(sys.stdout)
        writer.writerow(("end_s", "occupancy_probability", "decision", "stable_state"))
        writer.writerows(rows)


if __name__ == "__main__":
    main()
