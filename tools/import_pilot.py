"""Convert catalogued ESPectre C6 HT20 recordings to the MVP data format."""
import argparse
import json
from pathlib import Path

import numpy as np

from validate_sessions import sha256_file


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Recorder data directory")
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    catalog = json.loads((args.source / "dataset_info.json").read_text(encoding="utf-8"))
    for source_label, records in catalog["files"].items():
        label = "idle" if source_label == "empty" else source_label
        for entry in records:
            original = args.source / source_label / entry["filename"]
            with np.load(original, allow_pickle=False) as source:
                raw = source["csi_data"]
                if (str(source["label"].item()) != source_label or raw.ndim != 2
                        or raw.shape[1] != 128 or int(source["num_subcarriers"]) != 64
                        or np.unique(source["channel"]).size != 1
                        or not np.all(source["phy_mode"] == "ht")
                        or not np.all(source["ltf_type"] == "ht-ltf")):
                    raise ValueError(f"Unexpected label or HT20 layout: {original}")
                ticks = source["device_ticks_us"].astype(np.int64)
                if ticks.shape != (len(raw),) or np.any(np.diff(ticks) <= 0):
                    raise ValueError(f"Invalid device timestamps: {original}")
                elapsed = ticks - ticks[0]
                slots = elapsed // 100_000
                # Earliest packet per 100 ms slot. Empty slots stay empty.
                _, selected = np.unique(slots, return_index=True)
                iq = raw[selected].reshape(-1, 64, 2).astype(np.float32)
                amplitude = np.hypot(iq[..., 0], iq[..., 1])
                timestamps = elapsed[selected] / 1e6
                device = str(entry["device_id"])
                capture_channel = int(source["channel"][0])
            name = original.stem.replace("empty_", "idle_", 1)
            folder = args.destination / label
            folder.mkdir(parents=True, exist_ok=True)
            np.savez_compressed(
                folder / (name + ".npz"), csi_data=amplitude, timestamps=timestamps,
                label=label,
            )
            metadata = {
                "session_id": name,
                "label": label,
                "room": entry.get("environment"),
                "device": device,
                "chip": entry.get("chip"),
                "channel": capture_channel,
                "recorded_at": entry["collected_at"],
                "source_role": entry.get("dataset_role"),
                "source_packets": len(raw),
                "source_sha256": sha256_file(original),
                "duration_s": float(timestamps[-1]),
                "packets": len(timestamps),
                "rate_pps": round((len(timestamps) - 1) / timestamps[-1], 2),
                "notes": f"Source {original.name}. {entry.get('description', '')}",
            }
            (folder / (name + ".json")).write_text(
                json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
            )


if __name__ == "__main__":
    main()
