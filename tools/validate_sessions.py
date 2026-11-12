#!/usr/bin/env python3
"""Validate ESPectre CSI session files against the data contract.

Contract (docs/TechDesign-ESpectre-MVP-v1.0.md, section 3):
  data/<label>/<label>_<room>_<device>_<YYYYMMDD-HHMMSS>.npz
      csi_data    (frames, subcarriers) or (frames, rx, subcarriers)
      label       str or scalar array, constant for the whole session
      timestamps  (frames,) optional, seconds since start
  data/<label>/<...>.json   optional sidecar metadata

Status meanings
  PASS      usable, meets the target length
  SHORT     usable, but shorter than the 300 s target -> excluded from headline metric
  DEGRADED  usable, but packet rate too low
  FAIL      not usable, re-record

Exit code: 0 if no session FAILs, 1 otherwise. --strict also fails on SHORT/DEGRADED.

Usage:
    python tools/validate_sessions.py --data data
    python tools/validate_sessions.py --data data --manifest data/manifest.csv
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

DEFAULT_RATE_PPS = 10.0
MIN_FAIL_PACKETS = 300
MIN_OK_PACKETS = 1000
MIN_RATE_PPS = 5.0
MAX_GAP_S = 2.0

KNOWN_LABELS = (
    "idle",
    "static_presence",
    "motion",
    "interference_fan",
    "interference_curtain",
    "interference_corridor",
    "interference_wifi",
)


def ascii_text(value) -> str:
    """Windows consoles choke on non-ASCII; keep stdout printable."""
    return str(value).encode("ascii", "replace").decode("ascii")


def sha256_file(path: Path, chunk: int = 1 << 20) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(chunk), b""):
            digest.update(block)
    return digest.hexdigest()


def read_label(raw) -> tuple[str | None, bool]:
    """Return (label, is_mixed). Accepts str, bytes, or per-frame arrays."""
    if raw is None:
        return None, False
    values = np.asarray(raw).ravel()
    seen = []
    for item in values:
        if isinstance(item, (bytes, np.bytes_)):
            item = item.decode("utf-8", "replace")
        text = str(item).strip()
        if text not in seen:
            seen.append(text)
        if len(seen) > 1:
            return seen[0], True
    return (seen[0] if seen else None), False


def load_metadata(npz_path: Path) -> dict:
    meta_path = npz_path.with_suffix(".json")
    if not meta_path.exists():
        return {}
    try:
        with open(meta_path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, ValueError):
        return {"_metadata_error": True}


def check_session(npz_path: Path, data_root: Path) -> dict:
    rel = npz_path.relative_to(data_root)
    result = {
        "session_id": npz_path.stem,
        "label": "",
        "path": ascii_text(rel).replace("\\", "/"),
        "packets": 0,
        "duration_s": 0.0,
        "rate_pps": 0.0,
        "subcarriers": 0,
        "label_source": "none",
        "status": "FAIL",
        "sha256": "",
        "notes": "",
    }
    notes: list[str] = []
    folder_label = npz_path.parent.name

    try:
        with np.load(npz_path, allow_pickle=False) as data:
            keys = list(data.files)
            if "csi_data" not in keys:
                notes.append("missing csi_data (keys=%s)" % ",".join(keys[:6]))
                result["notes"] = "; ".join(notes)
                return result
            csi = np.asarray(data["csi_data"])
            raw_label = data["label"] if "label" in keys else None
            timestamps = None
            if "timestamps" in keys:
                timestamps = np.asarray(data["timestamps"], dtype=float).ravel()
    except Exception as exc:  # corrupt file, pickle, truncated
        notes.append("cannot load: %s" % ascii_text(type(exc).__name__))
        result["notes"] = "; ".join(notes)
        return result

    if csi.ndim not in (2, 3):
        notes.append("csi_data has %d dims, expected 2 or 3" % csi.ndim)
        result["notes"] = "; ".join(notes)
        return result

    frames = int(csi.shape[0])
    subcarriers = int(np.prod(csi.shape[1:]))
    result["packets"] = frames
    result["subcarriers"] = subcarriers

    try:
        finite = bool(np.isfinite(csi.astype(np.float64)).all())
    except (TypeError, ValueError):
        finite = False
    if not finite:
        notes.append("nan/inf in csi_data")

    meta = load_metadata(npz_path)
    if not meta:
        notes.append("no metadata sidecar")
    elif meta.get("_metadata_error"):
        notes.append("metadata json unreadable")

    file_label, mixed = read_label(raw_label)
    if mixed:
        notes.append("mixed labels inside one session")
    if file_label:
        result["label"] = file_label
        result["label_source"] = "npz"
    else:
        result["label"] = folder_label
        result["label_source"] = "folder"

    if file_label and file_label != folder_label:
        notes.append("label '%s' != folder '%s'" % (file_label, folder_label))

    if timestamps is not None and timestamps.size > 0:
        if timestamps.size != frames:
            notes.append("timestamps length != frames")
        if frames > 1:
            span = float(timestamps[-1] - timestamps[0])
            result["duration_s"] = span
            gaps = np.diff(timestamps)
            if gaps.size and float(np.max(gaps)) > MAX_GAP_S:
                notes.append("gap %.1fs" % float(np.max(gaps)))
        rate = frames / result["duration_s"] if result["duration_s"] > 0 else 0.0
    else:
        rate_hint = meta.get("rate_pps") if isinstance(meta, dict) else None
        rate = float(rate_hint) if rate_hint else DEFAULT_RATE_PPS
        result["duration_s"] = frames / rate if rate > 0 else 0.0
        if not rate_hint:
            notes.append("no timestamps, assumed %.0f pps" % DEFAULT_RATE_PPS)

    result["rate_pps"] = round(rate, 2)

    fatal = any(
        flag in note
        for note in notes
        for flag in ("missing csi_data", "cannot load", "dim", "nan/inf", "mixed labels",
                     "!= folder", "gap ", "length !=")
    )

    if fatal:
        result["status"] = "FAIL"
    elif frames < MIN_FAIL_PACKETS:
        result["status"] = "FAIL"
        notes.append("packets < %d" % MIN_FAIL_PACKETS)
    elif rate < MIN_RATE_PPS:
        result["status"] = "DEGRADED"
    elif frames < MIN_OK_PACKETS:
        result["status"] = "SHORT"
    else:
        result["status"] = "PASS"

    if result["label"] not in KNOWN_LABELS:
        notes.append("unknown label '%s'" % result["label"])

    result["sha256"] = sha256_file(npz_path)[:16]
    result["notes"] = "; ".join(notes)
    return result


def print_table(rows: list[dict]) -> None:
    header = ("SESSION", "LABEL", "PKTS", "DUR_S", "RATE", "STATUS")
    widths = (44, 22, 6, 7, 6, 9)
    print("  ".join(name.ljust(w) for name, w in zip(header, widths)))
    print("  ".join("-" * w for w in widths))
    for row in rows:
        cells = (
            ascii_text(row["session_id"])[:44],
            ascii_text(row["label"])[:22],
            str(row["packets"]),
            "%.0f" % row["duration_s"],
            "%.1f" % row["rate_pps"],
            row["status"],
        )
        print("  ".join(cell.ljust(w) for cell, w in zip(cells, widths)))
        if row["notes"]:
            print("      note: " + ascii_text(row["notes"])[:140])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate ESPectre CSI sessions")
    parser.add_argument("--data", type=Path, default=Path("data"),
                        help="root directory containing <label>/<session>.npz")
    parser.add_argument("--manifest", type=Path, default=None,
                        help="write a CSV manifest here")
    parser.add_argument("--strict", action="store_true",
                        help="treat SHORT and DEGRADED as failures")
    args = parser.parse_args(argv)

    if not args.data.is_dir():
        print("ERROR: data directory not found: %s" % ascii_text(args.data))
        return 2

    files = sorted(p for p in args.data.rglob("*.npz") if p.is_file())
    if not files:
        print("ERROR: no .npz sessions under %s" % ascii_text(args.data))
        return 2

    rows = [check_session(path, args.data) for path in files]
    print("")
    print_table(rows)

    counts: dict[str, int] = {}
    per_label: dict[str, int] = {}
    for row in rows:
        counts[row["status"]] = counts.get(row["status"], 0) + 1
        if row["status"] != "FAIL":
            per_label[row["label"]] = per_label.get(row["label"], 0) + 1

    print("")
    print("SUMMARY  " + "  ".join("%s=%d" % (k, v) for k, v in sorted(counts.items())))
    print("USABLE   " + ("  ".join("%s=%d" % (k, v) for k, v in sorted(per_label.items())) or "none"))
    print("TOTAL    %d session(s)" % len(rows))

    if args.manifest:
        args.manifest.parent.mkdir(parents=True, exist_ok=True)
        columns = ["session_id", "label", "path", "packets", "duration_s", "rate_pps",
                   "subcarriers", "label_source", "status", "sha256", "notes"]
        with open(args.manifest, "w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=columns)
            writer.writeheader()
            for row in rows:
                writer.writerow({key: row[key] for key in columns})
        print("MANIFEST %s" % ascii_text(args.manifest))

    bad = [row for row in rows if row["status"] == "FAIL"]
    soft = [row for row in rows if row["status"] in ("SHORT", "DEGRADED")]

    print("")
    if bad:
        print("RESULT   FAIL - %d session(s) must be re-recorded:" % len(bad))
        for row in bad:
            print("         %s: %s" % (ascii_text(row["session_id"]), ascii_text(row["notes"])))
    elif soft:
        print("RESULT   PASS with %d flagged session(s) (usable, excluded from headline metric)"
              % len(soft))
    else:
        print("RESULT   PASS")

    if bad:
        return 1
    if args.strict and soft:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
