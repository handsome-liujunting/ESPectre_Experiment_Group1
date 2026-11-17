# results/

Generated artefacts only. Nothing here is written by hand, except this README.

| Path | Produced by | Status |
| --- | --- | --- |
| `v2/presence-v2.json` | `tools/presence_v2.py train` | current model, exported weights |
| `v2/CSI-8-session-results.csv` | `tools/presence_v2.py replay` | frozen pilot model on the eight `dorm-v2` captures |
| `v2/CSI-feature-comparison.csv` | `tools/presence_v2.py` | LOSO feature comparison, 3 idle + 3 seated |
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

**Known breach of that rule:** `pilot-20261029/loso_metrics.json` records the command,
the seed, the dataset hash and library versions, but **not** the git commit. Adding it
needs a rerun with `git rev-parse HEAD` plumbed into `loso_eval.py`.
