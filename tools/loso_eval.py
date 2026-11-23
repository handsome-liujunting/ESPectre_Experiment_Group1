"""Fit the pilot classifier, evaluate by capture, and export JSON model weights."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import shlex
import subprocess
import sys

import numpy as np
import sklearn
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, precision_recall_fscore_support
from sklearn.preprocessing import StandardScaler

from presence import FEATURE_VERSION, LABELS, STRESS, predict, states, windows
from validate_sessions import check_session, load_metadata, sha256_file

SEED = 42
STATE_NAMES = ("UNOCCUPIED", "OCCUPIED", "UNKNOWN")


def ratio(top, bottom):
    return float(top / bottom) if bottom else None


def resolve_commit(explicit, root):
    """The commit this code was run from. Never guessed: git, then --commit, then None."""
    if explicit:
        return explicit, "--commit"
    try:
        found = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root,
                               capture_output=True, text=True, timeout=10)
        if found.returncode == 0 and found.stdout.strip():
            return found.stdout.strip(), "git"
    except (OSError, subprocess.SubprocessError):
        pass
    return None, "unknown"


def fit(sessions, data_hash):
    x = np.concatenate([session["features"] for session in sessions])
    y = np.concatenate([
        np.full(len(session["features"]), LABELS.index(session["label"]))
        for session in sessions
    ])
    valid = np.isfinite(x).all(axis=1)
    scaler = StandardScaler().fit(x[valid])
    classifier = LogisticRegression(max_iter=1000, random_state=SEED)
    classifier.fit(scaler.transform(x[valid]), y[valid])
    if classifier.classes_.tolist() != [0, 1, 2]:
        raise ValueError("Training sessions need valid windows for each class.")
    return {
        "feature_version": FEATURE_VERSION, "labels": list(LABELS), "seed": SEED,
        "input": "64 per-subcarrier amplitudes, timestamps in seconds, 10 packets/s target",
        "mean": scaler.mean_.tolist(), "scale": scaler.scale_.tolist(),
        "coefficient": classifier.coef_.tolist(), "intercept": classifier.intercept_.tolist(),
        "training_sha256": data_hash, "training_sessions": len(sessions),
        "status": "pilot_offline",
    }


def evaluate(model, session):
    probs = predict(model, session["features"])
    valid = np.isfinite(probs).all(axis=1)
    label = session["label"]
    decisions = list(states(probs[:, 1:].sum(axis=1)))
    labels = Counter(decision for decision, _ in decisions)
    smoothed_flips = sum(
        previous != current and previous != "UNKNOWN" and current != "UNKNOWN"
        for (_, previous), (_, current) in zip(decisions, decisions[1:])
    )
    per_class = np.bincount(probs[valid].argmax(axis=1), minlength=len(LABELS))
    return {
        "path": session["path"], "label": label, "sha256": session["sha256"],
        "classified_windows": int(valid.sum()), "classifier_counts": per_class.tolist(),
        "state_counts": {name: labels[name] for name in STATE_NAMES},
        "known_state_flips": smoothed_flips,
    }


def aggregate(rows):
    if not rows:
        return {
            "sessions": 0, "classifier_confusion": np.zeros((3, 3), dtype=int).tolist(),
            "classifier_scores": {label: {"precision": None, "recall": None, "f1": None}
                                  for label in LABELS},
            "stable_state_confusion": np.zeros((3, 3), dtype=int).tolist(),
            "presence_recall": None, "static_presence_recall": None,
            "false_positive_rate": None, "presence_f1": None,
            "known_state_coverage": None, "sessions_detail": [],
        }
    classes = np.zeros((3, 3), dtype=int)
    stable = np.zeros((3, 3), dtype=int)
    for row in rows:
        index = LABELS.index(row["label"])
        classes[index] += row["classifier_counts"]
        stable[index] += [row["state_counts"][name] for name in STATE_NAMES]
    occupied = stable[1:, 1].sum()
    false_positive = stable[0, 1]
    missed = stable[1:].sum() - occupied
    y_true = [label for label, counts in enumerate(classes) for _ in range(sum(counts))]
    y_pred = [prediction for counts in classes for prediction, n in enumerate(counts)
              for _ in range(n)]
    precision, recall, f1, _ = precision_recall_fscore_support(
        y_true, y_pred, labels=[0, 1, 2], zero_division=0
    )
    return {
        "sessions": len(rows), "classifier_confusion": classes.tolist(),
        "classifier_scores": {
            label: {"precision": float(p), "recall": float(r), "f1": float(f)}
            for label, p, r, f in zip(LABELS, precision, recall, f1)
        },
        "stable_state_confusion": stable.tolist(),
        "presence_recall": ratio(occupied, stable[1:].sum()),
        "static_presence_recall": ratio(stable[1, 1], stable[1].sum()),
        "false_positive_rate": ratio(false_positive, stable[0].sum()),
        "presence_f1": ratio(2 * occupied, 2 * occupied + false_positive + missed),
        "known_state_coverage": ratio(stable[:, :2].sum(), stable.sum()),
        "sessions_detail": rows,
    }


def read_sessions(root):
    sessions = []
    skipped = []
    hashes = set()
    for path in sorted(root.rglob("*.npz")):
        row = check_session(path, root)
        metadata = load_metadata(path)
        role = metadata.get("source_role")
        if role == "exclude" or row["status"] not in ("PASS", "SHORT"):
            skipped.append({"path": row["path"], "status": row["status"], "role": role,
                            "notes": row["notes"]})
            continue
        if row["label"] not in (*LABELS, *STRESS, "interference_wifi"):
            raise ValueError(f"Unsupported session label: {path}")
        digest = sha256_file(path)
        _, features = windows(path)
        if digest in hashes or not np.isfinite(features).all(axis=1).any():
            raise ValueError(f"Duplicate recording or no valid window: {path}")
        hashes.add(digest)
        sessions.append({
            "path": row["path"], "label": row["label"], "features": features,
            "role": role, "status": row["status"], "sha256": digest,
        })
    return sessions, skipped


def fingerprint(sessions):
    manifest = "\n".join(f"{row['path']} {row['sha256']}" for row in sessions)
    return hashlib.sha256(manifest.encode()).hexdigest()


def save_json(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def report(metrics):
    def pct(value):
        return "not measured" if value is None else f"{100 * value:.1f}%"

    lines = [
        "# ESPectre pilot evaluation", "", f"Command: `{metrics['command']}`",
        "", f"Source commit: `{metrics['source_commit'] or 'not recorded'}`.",
        "", f"Dataset SHA-256: `{metrics['data_sha256']}`. Seed: {SEED}.",
        "", "| Evaluation | Sessions | Presence recall | Static recall | Idle false-positive rate | Presence F1 | Known-state coverage |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for title, key in (("Pilot LOSO", "loso"), ("Original catalogue holdout", "holdout")):
        row = metrics[key]
        values = [row[key] for key in ("presence_recall", "static_presence_recall",
                                       "false_positive_rate", "presence_f1",
                                       "known_state_coverage")]
        lines.append(f"| {title} | {row['sessions']} | " + " | ".join(map(pct, values)) + " |")
    lines += [
        "", "Recall and F1 count UNKNOWN on occupied windows as misses. Empty UNKNOWN",
        "windows remain in the false-positive-rate denominator. Read coverage alongside FPR.",
        "", "LOSO fits the scaler and logistic regression anew in each training fold. The",
        "exported model fits the original training recordings and evaluates the original",
        "holdout separately. The original exclusions remain excluded. State thresholds",
        "stay fixed at the values specified in the PRD.",
        "", "The approximately 60-second recordings are SHORT and support a pilot estimate.",
        "Full-duration LOSO acceptance, capture-to-display latency, transition latency,",
        "CPU and memory, and live hardware verification are pending.",
        "", "These recordings describe one device, one dorm environment and one collection",
        "date. Whole-capture splitting leaves time-of-day and collection-order effects intact.",
        "", "## Interference stress with frozen model", "",
        "| Condition | Available sessions | Sessions short of minimum | False-positive rate |",
        "| --- | ---: | ---: | ---: |",
    ]
    for label, row in metrics["stress"].items():
        lines.append(f"| {label} | {row['sessions']} | {row['missing']} | "
                     f"{pct(row['false_positive_rate'])} |")
    lines += ["", "See loso_metrics.json for per-capture outcomes and confusion matrices."]
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--commit", default=None,
                        help="git commit this run corresponds to, if the tree is not a clone")
    args = parser.parse_args()
    commit, commit_source = resolve_commit(args.commit, Path(__file__).resolve().parents[1])
    sessions, skipped = read_sessions(args.data)
    if sessions and not any(item["role"] for item in sessions):
        print("NOTE: no session carries source_role (missing .json sidecars?), so "
              "every capture is treated as training data and the holdout set is empty.")
    clean = [item for item in sessions if item["label"] in LABELS]
    training = [item for item in clean if item["role"] in (None, "train")]
    holdout = [item for item in clean if item["role"] == "holdout"]
    if any(item["role"] not in (None, "train", "holdout") for item in clean):
        parser.error("Unexpected source_role in clean data.")
    if min(Counter(item["label"] for item in training)[label] for label in LABELS) < 2:
        parser.error("At least two usable training captures per class are required.")
    folds = []
    for item in training:
        rest = [other for other in training if other is not item]
        folds.append(evaluate(fit(rest, fingerprint(rest)), item))
    model = fit(training, fingerprint(training))
    stress = {}
    for label in (*STRESS, "interference_wifi"):
        rows = [evaluate(model, item) for item in sessions if item["label"] == label]
        counts = Counter()
        for row in rows:
            counts.update(row["state_counts"])
        stress[label] = {
            "sessions": len(rows), "missing": max(0, 2 - len(rows)),
            "false_positive_rate": ratio(counts["OCCUPIED"], sum(counts.values())),
            "known_state_coverage": ratio(counts["OCCUPIED"] + counts["UNOCCUPIED"],
                                          sum(counts.values())),
            "sessions_detail": rows,
        }
    metrics = {
        "command": shlex.join(["python", *sys.argv]),
        "source_commit": commit, "source_commit_source": commit_source,
        "data_sha256": fingerprint(sessions), "seed": SEED,
        "numpy_version": np.__version__, "sklearn_version": sklearn.__version__,
        "status_counts": dict(Counter(item["status"] for item in sessions)),
        "classes": list(LABELS), "state_columns": list(STATE_NAMES),
        "loso": aggregate(folds),
        "holdout": aggregate([evaluate(model, item) for item in holdout]),
        "excluded": skipped, "stress": stress,
    }
    args.output.mkdir(parents=True, exist_ok=True)
    save_json(args.output / "presence_model.json", model)
    save_json(args.output / "loso_metrics.json", metrics)
    (args.output / "LOSO-REPORT.md").write_text(report(metrics), encoding="utf-8")
    print(report(metrics))


if __name__ == "__main__":
    main()
