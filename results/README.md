# results/

Generated artefacts only. Nothing here is written by hand, except this README.

| Path | Produced by | Status |
| --- | --- | --- |
| `v2/presence-v2.json` | `tools/presence_v2.py train` | current model, exported weights |
| `v2/CSI-8-session-results.csv` | `tools/presence_v2.py replay` | **superseded**: pilot model on the eight `dorm-v2` captures; its balcony-01 row says 37 occupied, the v2 replay says 0. Cite `v2/CSI-v2-balcony-0{1,2}.csv` instead |
| `v2/CSI-feature-comparison.csv` | exploratory script, **not committed** | LOSO feature comparison, 3 idle + 3 seated |
| `v2-loso-reproduced.csv` | `tools/v2_compare.py` | the `normalized_temporal` row of the table above, regenerated |
| `v2/CSI-v2-balcony-0{1,2}.csv` | `tools/presence_v2.py replay` | held-out balcony replays |
| `pilot-20261029/loso_metrics.json` | `tools/loso_eval.py` | superseded, kept for history |
| `pilot-20261029/LOSO-REPORT.md` | `tools/loso_eval.py` | superseded, kept for history |
| `pilot-20261029/presence_model.json` | `tools/loso_eval.py` | superseded |
| `pilot-20261029/demo-motion.csv` | `tools/presence.py` | superseded |

**Which number is current:** `results/v2/` only. The `pilot-20261029/` directory is
kept because deleting results is worse than keeping superseded ones, but its LOSO
table (0.0 % false positives, 98.3 % seated recall) is not generalisation evidence —
see the trap in `MEMORY.md` and the table in `README.md`.

Every file must contain: the command line, the seed, the git commit and the sha256
of every input session. A metrics file without those is deleted, not cited.

The 2026-11 v2 replay CSVs (`CSI-8-session-results.csv`,
`CSI-v2-balcony-0{1,2}.csv`) predate that header rule. Their command is recorded
in `docs/NEXT-STEPS.md`; the model they were run with is `v2/presence-v2.json`
(seed 42, feature version 2, six source hashes). Do not invent a header for them.

`pilot-20261029/loso_metrics.json` names its `source_commit` again, because it was
regenerated after `loso_eval.py` learned to record one. That breach is closed.

**Known breach that is still open:** `v2/CSI-feature-comparison.csv` was written by a
script that is not in this repository. Only its `normalized_temporal` row can be
regenerated, and the headline rests on that row:

```bash
python tools/v2_compare.py --data data/dorm-v2 --output results/v2-loso-reproduced.csv
```

The other three rows (`raw_temporal`, `normalized_channel_shape`,
`absolute_amplitude`) are cited as exploration, not as reproducible results. Either
commit the script that produced them or delete the rows before the review; do not
leave them looking reproducible.
