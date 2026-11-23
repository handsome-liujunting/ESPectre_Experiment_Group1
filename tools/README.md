# tools/

Our own pipeline. Nothing here imports the upstream ESPectre `tools.lib` package.

| Script | Status | Purpose |
| --- | --- | --- |
| `validate_sessions.py` | **implemented** | Check every `.npz` against the data contract, print a table, write `manifest.csv` |
| `import_pilot.py` | **implemented** | Convert a recorder catalogue into `data/pilot-*` sessions + sidecars |
| `presence.py` | **implemented** | 1 s windows to 16 log features; hysteresis state machine; replay one capture |
| `loso_eval.py` | **implemented** | Fit, leave-one-session-out, write `loso_metrics.json` + `LOSO-REPORT.md` |
| `presence_v2.py` | **implemented** | v2 feature/model: train, replay, export JSON |
| `v2_compare.py` | **implemented** | Regenerate the v2 LOSO headline: 83/270 false positives, 174/270 seated |
| `capture_session.py` | not written | FR-01: record one labelled session |
| `live_dashboard.py` | not written | FR-05: live state display |

`features.py`, `train.py` and `state_machine.py` from the original plan were folded
into `presence.py`; do not create them as separate files.

`v2_compare.py` imports `extract()` from `presence_v2.py` and `states()` from
`presence.py` rather than copying them, so a change in either moves the headline
number too. It exits non-zero if the result drifts from the published 83/174.

Do not mark a script `implemented` until it runs on the real data and its output is
committed under `results/`.

## Validator usage

```bash
python tools/validate_sessions.py --data data/pilot-20261029 \
    --manifest data/pilot-20261029/manifest.csv
python tools/validate_sessions.py --data data/pilot-20261029 --strict   # warnings fail
```

Point it at **one campaign**, not at `data/`. `data/dorm-v2/` stores `iq_raw`
(128 interleaved I/Q columns), which this validator does not read; passing the
whole `data/` folder reports those eight sessions as `FAIL` and is a false alarm
about the data, not a finding.

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

`loso_eval.py` needs the `.json` sidecar next to each `.npz`: the holdout/exclude
role lives only in the sidecar. When the sidecars are missing it prints a note and
reports the holdout as "not measured" instead of failing — but the numbers are then
training-only, so treat a sidecar-less run as a smoke test, not a result.

