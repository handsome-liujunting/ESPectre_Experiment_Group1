"""Reproduce the v2 headline with leave-one-session-out on the dorm-v2 recordings.

`results/v2/CSI-feature-comparison.csv` reports the row the headline rests on
(`normalized_temporal`): 83 of 270 empty windows occupied (30.7 %) and 174 of 270
seated windows occupied (64.4 %). That table was written by a script that was not
committed, so until now nobody could check it. This script regenerates the row.

It does not reimplement the pipeline. The features come from
`presence_v2.extract()` and the hysteresis comes from `presence.states()`, so a
change in either moves this output too.

Run from the repository root:

    python tools/v2_compare.py --data data/dorm-v2 --output results/v2/v2-loso-reproduced.csv
"""

import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np

from presence import states
from presence_v2 import extract

# The dorm-v2 set is flat: the class lives in the file name, not in a folder.
IDLE = ("idle-01", "idle-02", "idle-03")
SEATED = ("static-presence-01", "static-presence-02", "static-presence-03")

PUBLISHED_FP = 83
PUBLISHED_SEATED = 174


def catalogue():
    return [(name, 0) for name in IDLE] + [(name, 1) for name in SEATED]


def fit_and_score(train, held_features, seed):
    """Fit scaler and classifier on the training folds, return the held-out states.

    `train` is a list of (feature_matrix, label) pairs, one per training session.
    """
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler

    train_features = []
    train_targets = []
    for matrix, label in train:
        usable = matrix[np.isfinite(matrix).all(axis=1)]
        train_features.append(usable)
        train_targets.extend([label] * len(usable))

    stacked = np.concatenate(train_features)
    scaler = StandardScaler().fit(stacked)
    classifier = LogisticRegression(random_state=seed).fit(
        scaler.transform(stacked), train_targets)

    valid = np.isfinite(held_features).all(axis=1)
    score = np.full(len(held_features), np.nan)
    if valid.any():
        score[valid] = classifier.predict_proba(
            scaler.transform(held_features[valid]))[:, 1]
    # presence.states() yields (instant_decision, stable_state); the stable state is
    # what the dashboard shows, so that is what the published table counts.
    return [stable for _, stable in states(score)]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, required=True,
                        help="directory holding <label>-NN-raw.npz")
    parser.add_argument("--output", type=Path, help="CSV destination; stdout if omitted")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args(argv)

    features = {}
    for name, _ in catalogue():
        path = args.data / (name + "-raw.npz")
        if not path.exists():
            parser.error("missing " + str(path))
        features[name] = extract(path)

    rows = []
    totals = Counter()
    for held, held_label in catalogue():
        train = [(features[n], l) for n, l in catalogue() if n != held]
        sequence = fit_and_score(train, features[held], args.seed)
        counts = Counter(sequence)
        rows.append({
            "feature": "normalized_temporal",
            "session": held,
            "label": held_label,
            "windows": len(sequence),
            "occupied": counts["OCCUPIED"],
            "unoccupied": counts["UNOCCUPIED"],
            "unknown": counts["UNKNOWN"],
        })
        if held_label == 0:
            totals["empty"] += len(sequence)
            totals["empty_occupied"] += counts["OCCUPIED"]
        else:
            totals["seated"] += len(sequence)
            totals["seated_occupied"] += counts["OCCUPIED"]

    fields = ("feature", "session", "label", "windows",
              "occupied", "unoccupied", "unknown")
    handle = args.output.open("w", newline="", encoding="utf-8") if args.output else sys.stdout
    try:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    finally:
        if args.output:
            handle.close()

    fpr = 100.0 * totals["empty_occupied"] / totals["empty"]
    recall = 100.0 * totals["seated_occupied"] / totals["seated"]
    summary = {
        "evaluation": "leave-one-session-out",
        "feature": "normalized_temporal",
        "sessions": len(rows),
        "seed": args.seed,
        "idle_false_positives": "%d/%d" % (totals["empty_occupied"], totals["empty"]),
        "idle_false_positive_rate_pct": round(fpr, 1),
        "seated_detected": "%d/%d" % (totals["seated_occupied"], totals["seated"]),
        "seated_recall_pct": round(recall, 1),
    }
    print(json.dumps(summary, indent=2))
    print()
    print("Published: %d/%d (30.7 %%) and %d/%d (64.4 %%)."
          % (PUBLISHED_FP, totals["empty"], PUBLISHED_SEATED, totals["seated"]))
    matched = (totals["empty_occupied"] == PUBLISHED_FP
               and totals["seated_occupied"] == PUBLISHED_SEATED)
    print("Match:", matched)
    return 0 if matched else 1


if __name__ == "__main__":
    sys.exit(main())
