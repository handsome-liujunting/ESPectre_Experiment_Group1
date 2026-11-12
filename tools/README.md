# tools/

Our own pipeline. Nothing here imports the upstream ESPectre `tools.lib` package.

| Script | Status | Purpose |
| --- | --- | --- |
| `validate_sessions.py` | **implemented** | Check every `.npz` against the data contract, print a table, write `data/manifest.csv` |
| `capture_session.py` | not written | FR-01: record one labelled session |
| `features.py` | not written | 1 s windows → 8 subband features |
| `train.py` / `loso_eval.py` | not written | FR-03 / FR-06: train and evaluate LOSO |
| `state_machine.py` | not written | FR-04: hysteresis, debounce, stale timeout |
| `live_dashboard.py` | not written | FR-05: live state display |

Do not add a script to this table as "implemented" until it runs on the real data
and its output is committed under `results/`.

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
