# tools/

Our own pipeline. Nothing here imports the upstream ESPectre `tools.lib` package.

| Script | Status | Purpose |
| --- | --- | --- |
| `validate_sessions.py` | **implemented** | Check every `.npz` against the data contract, print a table, write `manifest.csv` |
| `import_pilot.py` | **implemented** | Convert a recorder catalogue into `data/pilot-*` sessions + sidecars |
| `presence.py` | **implemented** | 1 s windows to 16 log features; hysteresis state machine; replay one capture |
| `loso_eval.py` | **implemented** | Fit, leave-one-session-out, write `loso_metrics.json` + `LOSO-REPORT.md` |
| `presence_v2.py` | **implemented** | v2 feature/model: train, replay, export JSON |
| `capture_session.py` | not written | FR-01: record one labelled session |
| `live_dashboard.py` | not written | FR-05: live state display |

`features.py`, `train.py` and `state_machine.py` from the original plan were folded
into `presence.py`; do not create them as separate files.

Do not mark a script `implemented` until it runs on the real data and its output is
committed under `results/`.

## Validator usage

```bash
python tools/validate_sessions.py --data data --manifest data/manifest.csv
python tools/validate_sessions.py --data data --strict   # warnings become failures
```

Exit codes: `0` no failures, `1` at least one session failed, `2` bad arguments or
no data found.

Status thresholds:

| Status | Meaning |
| --- | --- |
| `PASS` | ≥ 1000 packets, ≥ 5 pps, no gaps > 2 s |
| `SHORT` | 300–999 packets — usable, excluded from the headline metric |
| `DEGRADED` | rate < 5 pps |
| `FAIL` | < 300 packets, gaps, mixed labels, NaN, missing key, label ≠ folder |

The 1000-packet bar was chosen before any data existed. At 10 packets/s it means
100 s, and **no capture in this repo reaches it** (pilot 601, dorm-v2 about 900).
Every published number is therefore computed on `SHORT` captures. Either accept that
and say it everywhere, or re-record at 100 s and re-run.
