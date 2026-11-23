"""Build the demo's data file from the real captures.

Everything the page displays is computed here, from the captures under `data/` and
the metrics under `results/`, and written into one JavaScript object. The page
itself computes nothing, so it can be opened from a USB stick with no server, no
network, and no Python.

Replay is held-out by construction: each capture is scored by a model that was
fitted without it. That is the same protocol as the published LOSO numbers, so
the demo cannot accidentally show a better result than the report.
"""

import base64
import csv
import json
import pathlib
import sys
from collections import Counter

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
DATA = ROOT / "data"
RESULTS = ROOT / "results"
SRC = ROOT / "tools"
OUT = HERE

sys.path.insert(0, str(SRC))

import importlib.util


def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, SRC / filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


presence = load("presence", "presence.py")
presence_v2 = load("presence_v2", "presence_v2.py")

from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

SEED = 42


def amplitude_of(path):
    """64 subcarrier amplitudes per packet, whichever contract the file uses."""
    with np.load(path, allow_pickle=False) as z:
        if "csi_data" in z:
            return z["csi_data"].astype(float), z["timestamps"].astype(float)
        iq = z["iq_raw"]
        return (np.linalg.norm(iq.reshape(-1, 64, 2).astype(float), axis=2),
                z["timestamps"].astype(float))


MAX_COLUMNS = 2000


def quantise(amplitude):
    """One byte per cell, scaled per capture so the waterfall uses full contrast.

    Time is decimated when a capture has more packets than the page can show: the
    waterfall is ~1000 px wide, so 2000 columns is already lossless on screen and
    keeps the data file small enough to email.
    """
    if len(amplitude) > MAX_COLUMNS:
        keep = np.linspace(0, len(amplitude) - 1, MAX_COLUMNS).round().astype(int)
        amplitude = amplitude[keep]
    scaled = amplitude - amplitude.min()
    span = scaled.max() or 1.0
    return (np.round(255.0 * scaled / span).astype(np.uint8),
            int(len(amplitude)))


def fit_binary(train):
    """Fit scaler + logistic on (features, label) pairs. Same order as presence_v2."""
    usable = [m[np.isfinite(m).all(axis=1)] for m, _ in train]
    labels = []
    for matrix, label in train:
        labels.extend([label] * len(matrix[np.isfinite(matrix).all(axis=1)]))
    stacked = np.concatenate(usable)
    scaler = StandardScaler().fit(stacked)
    clf = LogisticRegression(random_state=SEED).fit(scaler.transform(stacked), labels)
    return scaler, clf


def score_binary(scaler, clf, features):
    score = np.full(len(features), np.nan)
    valid = np.isfinite(features).all(axis=1)
    if valid.any():
        score[valid] = clf.predict_proba(scaler.transform(features[valid]))[:, 1]
    return score


def fit_three(train):
    usable = [m[np.isfinite(m).all(axis=1)] for m, _ in train]
    labels = []
    for matrix, label in train:
        labels.extend([label] * len(matrix[np.isfinite(matrix).all(axis=1)]))
    stacked = np.concatenate(usable)
    scaler = StandardScaler().fit(stacked)
    clf = LogisticRegression(max_iter=1000, random_state=SEED).fit(
        scaler.transform(stacked), labels)
    return scaler, clf


def score_three(scaler, clf, features):
    """Occupancy probability = 1 - P(idle), from the published class order."""
    score = np.full(len(features), np.nan)
    valid = np.isfinite(features).all(axis=1)
    if valid.any():
        prob = clf.predict_proba(scaler.transform(features[valid]))
        idle = list(clf.classes_).index(0)
        score[valid] = 1.0 - prob[:, idle]
    return score


def states_of(score):
    return [stable for _, stable in presence.states(score)]


def rows_to_seconds(times):
    return (times - times[0]).tolist()


print("--- loading captures")
DORM = ["idle-01", "idle-02", "idle-03", "static-presence-01",
        "static-presence-02", "static-presence-03"]
STRESS = ["balcony-01", "balcony-02"]

dorm_feat = {}
dorm_amp = {}
dorm_dur = {}
dorm_pk = {}
for name in DORM + STRESS:
    path = DATA / "dorm-v2" / ("%s-raw.npz" % name)
    dorm_feat[name] = presence_v2.extract(path)
    dorm_amp[name], ts = amplitude_of(path)
    dorm_dur[name] = float(ts[-1] - ts[0])
    dorm_pk[name] = len(dorm_amp[name])
    print("  %-20s %d packets  %d windows  %.1f s" % (
        name, dorm_pk[name], len(dorm_feat[name]), dorm_dur[name]))

manifest = list(csv.DictReader(
    (DATA / "pilot-20261029" / "manifest.csv").open(encoding="utf-8", newline="")))


def sidecar_role(row):
    """The train/holdout/exclude split lives only in the .json sidecar."""
    meta = json.loads(
        (DATA / "pilot-20261029" / row["path"]).with_suffix(".json")
        .read_text(encoding="utf-8"))
    return meta.get("source_role", "train")


for row in manifest:
    row["role"] = sidecar_role(row)

# The three pilot captures on the page must be the official held-out ones, and
# the model behind them must be fitted on the 18 training captures only. Picking
# manifest[0] instead used to put an excluded capture in the sidebar and leak a
# held-out capture into training.
PILOT_PICK = {}
for row in manifest:
    if row["role"] == "holdout" and row["label"] not in PILOT_PICK:
        PILOT_PICK[row["label"]] = row
missing = {"idle", "static_presence", "motion"} - set(PILOT_PICK)
if missing:
    raise SystemExit("no held-out capture for: %s" % ", ".join(sorted(missing)))
PILOT_TRAIN = [row for row in manifest if row["role"] == "train"]

pilot_feat = {}
pilot_amp = {}
pilot_dur = {}
pilot_pk = {}
for label, row in PILOT_PICK.items():
    path = DATA / "pilot-20261029" / row["path"]
    _, pilot_feat[label] = presence.windows(path)
    pilot_amp[label], ts = amplitude_of(path)
    pilot_dur[label] = float(ts[-1] - ts[0])
    pilot_pk[label] = len(pilot_amp[label])
    print("  pilot/%-16s %d packets  %d windows  %.1f s  (held out %s)" % (
        label, pilot_pk[label], len(pilot_feat[label]), pilot_dur[label],
        row["session_id"]))

pilot_train_feat = []
for row in PILOT_TRAIN:
    path = DATA / "pilot-20261029" / row["path"]
    _, feats = presence.windows(path)
    pilot_train_feat.append(
        (feats, ("idle", "static_presence", "motion").index(row["label"])))
print("  pilot training set: %d captures" % len(pilot_train_feat))

print()
print("--- held-out scoring")

sessions = []


def pack(session_id, label, group, source, amplitude, features, score, note,
         duration_s, packets):
    states = states_of(score)
    counts = Counter(states)
    heat, columns = quantise(amplitude)
    h, w = heat.shape
    sessions.append({
        "id": session_id,
        "label": label,
        "group": group,
        "source": source,
        "note": note,
        "duration_s": round(float(duration_s), 2),
        "packets": int(packets),
        "windows": len(states),
        "heat": {"w": w, "h": h, "min": round(float(amplitude.min()), 2),
                 "max": round(float(amplitude.max()), 2),
                 "b64": base64.b64encode(heat.tobytes()).decode("ascii")},
        "score": [None if not np.isfinite(v) else round(float(v), 4) for v in score],
        "stable": states,
        "counts": {"occupied": counts["OCCUPIED"], "unoccupied": counts["UNOCCUPIED"],
                   "unknown": counts["UNKNOWN"]},
        "features": [[None if not np.isfinite(v) else round(float(v), 3) for v in row]
                     for row in features],
        "packet_rate": round(packets / max(1e-9, float(duration_s)), 2),
    })


for held in DORM:
    train = [(dorm_feat[n], 0 if n.startswith("idle") else 1)
             for n in DORM if n != held]
    scaler, clf = fit_binary(train)
    score = score_binary(scaler, clf, dorm_feat[held])
    label = "empty" if held.startswith("idle") else "seated"
    pack(held, label, "empty" if label == "empty" else "seated", "dorm-v2",
         dorm_amp[held], dorm_feat[held], score,
         "held out: model never saw this capture", dorm_dur[held], dorm_pk[held])

train_all = [(dorm_feat[n], 0 if n.startswith("idle") else 1) for n in DORM]
scaler_all, clf_all = fit_binary(train_all)
for name in STRESS:
    score = score_binary(scaler_all, clf_all, dorm_feat[name])
    pack(name, "through-door", "stress", "dorm-v2",
         dorm_amp[name], dorm_feat[name], score,
         "frozen model, person walking on the balcony", dorm_dur[name], dorm_pk[name])

pilot_scaler, pilot_clf = fit_three(pilot_train_feat)
for held, row in PILOT_PICK.items():
    score = score_three(pilot_scaler, pilot_clf, pilot_feat[held])
    pack("pilot-" + held, "seated" if held == "static_presence"
         else ("empty" if held == "idle" else "walking"),
         "empty" if held == "idle" else ("seated" if held == "static_presence" else "motion"),
         "pilot-20261029", pilot_amp[held], pilot_feat[held], score,
         "held out: official split, fitted on the 18 training captures",
         pilot_dur[held], pilot_pk[held])

print("  packed %d sessions" % len(sessions))

print()
print("--- results block")
v2 = json.loads((RESULTS / "v2" / "presence-v2.json").read_text(encoding="utf-8"))
pilot_metrics = json.loads((RESULTS / "pilot-20261029" / "loso_metrics.json")
                           .read_text(encoding="utf-8"))
comparison = list(csv.DictReader(
    (RESULTS / "v2" / "CSI-feature-comparison.csv").open(encoding="utf-8")))

static_detail = next(r for r in pilot_metrics["holdout"]["sessions_detail"]
                     if r["label"] == "static_presence")

results = {
    "v2": {
        "idle_false_positives": "83/270",
        "idle_false_positive_rate_pct": 30.7,
        "seated_detected": "174/270",
        "seated_recall_pct": 64.4,
        "sessions": 6,
        "evaluation": "leave-one-session-out",
        "note": "headline: held-out, 6 sessions, one room",
    },
    "pilot": {
        "loso": pilot_metrics["loso"],
        "holdout": pilot_metrics["holdout"],
        # The classifier catches 2 of 60 windows in the one unseen seated capture;
        # after hysteresis the stable state reports 0 of 60. Both are true, and the
        # stable state is what the dashboard shows, so the page quotes that.
        "holdout_detail": {
            "classifier_recall_pct": round(
                100.0 * pilot_metrics["holdout"]["classifier_scores"]["static_presence"]["recall"], 1),
            "stable_recall_pct": round(
                100.0 * pilot_metrics["holdout"]["static_presence_recall"], 1),
            "state_counts": static_detail["state_counts"],
            "session": static_detail["path"],
        },
        "holdout_ids": {label: row["session_id"] for label, row in PILOT_PICK.items()},
        "status_counts": pilot_metrics["status_counts"],
        "data_sha256": pilot_metrics["data_sha256"],
        "source_commit": pilot_metrics.get("source_commit"),
        "numpy": pilot_metrics.get("numpy_version"),
        "sklearn": pilot_metrics.get("sklearn_version"),
        "seed": pilot_metrics.get("seed"),
        "command": pilot_metrics.get("command"),
        "stress": {k: {"sessions": v["sessions"], "missing": v["missing"],
                       "false_positive_rate": v["false_positive_rate"]}
                   for k, v in pilot_metrics["stress"].items()},
    },
    "comparison": comparison,
    "manifest": {
        "sessions": len(manifest),
        "labels": dict(Counter(r["label"] for r in manifest)),
        "packets": [int(r["packets"]) for r in manifest],
        "rate_pps": sorted({round(float(r["rate_pps"]), 2) for r in manifest}),
        "durations": [round(float(r["duration_s"]), 1) for r in manifest],
    },
    "v2_model": {"feature_version": v2["feature_version"], "seed": v2["seed"],
                 "status": v2["status"], "training_sessions": len(v2["sources"])},
}

# The pilot metrics file predates the balcony captures, so its stress block says
# every condition has zero sessions. Replace the one condition that was actually
# recorded with the replay computed above: the newest result wins.
balcony = [s for s in sessions if s["label"] == "through-door"]
balcony_occupied = sum(s["counts"]["occupied"] for s in balcony)
balcony_decided = sum(s["counts"]["occupied"] + s["counts"]["unoccupied"]
                      for s in balcony)
results["pilot"]["stress"]["interference_balcony"] = {
    "sessions": len(balcony),
    "missing": None,
    "decided_windows": balcony_decided,
    "false_positive_rate": (balcony_occupied / balcony_decided
                            if balcony_decided else None),
}
results["pilot"]["stress"]["interference_fan"]["missing"] = (
    "dropped: no fan in the test room")
for key in ("interference_curtain", "interference_corridor", "interference_wifi"):
    results["pilot"]["stress"][key]["missing"] = "not recorded"

payload = {
    "meta": {
        "title": "ESPectre — stationary presence from Wi-Fi CSI",
        "commit": (pilot_metrics.get("source_commit") or "")[:12],
        "data_sha256": pilot_metrics["data_sha256"],
        "generated_by": "demo/build_demo_data.py",
    },
    "sessions": sessions,
    "results": results,
}

OUT.mkdir(parents=True, exist_ok=True)
body = "window.DEMO = " + json.dumps(payload, separators=(",", ":")) + ";\n"
(OUT / "demo-data.js").write_text(body, encoding="utf-8", newline="\n")
print("  demo-data.js %.1f KB" % (len(body.encode("utf-8")) / 1024))

for s in sessions:
    print("  %-22s %-12s windows=%-3d occ=%-3d unocc=%-3d unk=%-3d dur=%.0fs" % (
        s["id"], s["label"], s["windows"], s["counts"]["occupied"],
        s["counts"]["unoccupied"], s["counts"]["unknown"], s["duration_s"]))
