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
| `PASS` | ≥ 500 packets, ≥ 5 pps, no gaps > 2 s |
| `SHORT` | 300–499 packets — usable, excluded from the headline metric |
| `DEGRADED` | rate < 5 pps |
| `FAIL` | < 300 packets, gaps, mixed labels, NaN, missing key, label ≠ folder |

The 500-packet floor is ~50 s at 10 packets/s: about 50 one-second windows, enough
for a per-session estimate with a wide error bar, which is what a sixty-second pilot
capture can honestly support. The **acceptance target is 300 s (~3000 packets)**;
judge against it with `--min-ok-packets 3000`, which flags every capture in the
repository today as `SHORT`. Do not describe the pilot numbers as acceptance evidence.

## Provenance in generated results

`loso_eval.py` writes `source_commit` into `loso_metrics.json`, taken from
`git rev-parse HEAD` inside the checkout. Running from a downloaded ZIP is not a
clone, so pass the commit explicitly:

```bash
python tools/loso_eval.py --data data/pilot-20261029 \
    --output results/pilot-20261029 --commit <sha shown on GitHub>
```

If neither is available the field is `null` with `source_commit_source: "unknown"`,
which is a visible gap rather than a guess.

