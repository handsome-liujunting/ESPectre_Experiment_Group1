# What is left, after the scope was frozen

**Updated 2026-11-23.** The capture campaign is closed. The dataset is final: 24
pilot sessions and 8 `dorm-v2` sessions, recorded in one room on one ESP32-C6.
No further sessions — no curtain, no external Wi-Fi, no 300-second runs, no second
room — will be recorded for this submission. Those conditions are now **stated
limitations**, not open tasks. The decision and its rationale are D-010 in
`docs/ai-decision-log.md`.

What remains is packaging: make every claim reproducible from the repository and
make every document agree with the measured result. Nothing below needs the board.

---

## P0 — before the upload

### 1. Upload the patch set

The current GitHub `main` still has the old `docs/DEMO-SCRIPT.md`, the old PRD
status table, and no `tools/v2_compare.py`. Upload the files in this folder,
preserving `docs/`, `tools/` and `results/` paths. The Chinese checklist outside the
repository (`GitHub上传清单-20261123.md`) lists the exact files and commit message.

**Artefact:** `main` contains `tools/v2_compare.py`, `docs/NEXT-STEPS.md`,
`docs/PRD-ESpectre-MVP-v1.0.md`, and the corrected `docs/DEMO-SCRIPT.md`.
**Time:** 20 minutes of web upload.

### 2. Regenerate the pilot manifest

The committed `data/pilot-20261029/manifest.csv` says `SHORT` for all 24 sessions
because it was generated when the packet floor was 1000. The floor is now 500;
every session passes it and is still `SHORT` against the 300-second acceptance
target. Regenerate, do not hand-edit:

```bash
python tools/validate_sessions.py --data data/pilot-20261029 \
    --manifest data/pilot-20261029/manifest.csv
```

**Time:** 2 minutes.

### 3. Point the demo page at the same numbers as the documents

`demo/build_demo_data.py` now selects the three pilot captures from the official
held-out split, fits on the 18 training captures only, and takes the balcony stress
row from the v2 replay. Rebuild and check:

```bash
python demo/build_demo_data.py
python demo/check_page.py
```

**Artefact:** `demo-data.js` with pilot counts 0/51/9, 0/21/39, 59/0/1, and a stress
table that reads 2 sessions / 0 of 162 occupied for through-door.
**Time:** 5 minutes.

### 4. Mark the stale eight-session table

`results/v2/CSI-8-session-results.csv` applies the **pilot** model to the eight
`dorm-v2` captures. Its `balcony-01` row says 37 occupied; the v2 replay says 0.
The v2 replay is newer and is the one the report and the demo quote. The file stays
for history, but `results/README.md` now marks it superseded so nobody cites the 37.

---

## P1 — document alignment (no new evidence)

### 5. PRD status table and acceptance

`docs/PRD-ESpectre-MVP-v1.0.md` v1.1 records what was actually built: FR-03/04/06/08
implemented, FR-01/05 not built and downgraded with a dated note, FR-07 partial with
one of four conditions recorded. The 300-second acceptance target stays visible and
is marked **not met**; it is not lowered.

### 6. Tech Design and Proposal

Both now describe the shipped classifier — 16 values per second, logistic
regression — instead of the planned 8-band MLP, and the demo as an offline replay
instead of a live dashboard. The design rationale for the MLP stays as a rejected
alternative, with the reason (six training sessions).

### 7. Decision log

D-010 (scope frozen), D-011 (newest result wins when two files disagree), D-012
(offline replay is the demo form). `traceability.md` cites D-001…D-012.

---

## What is deliberately not being done

| Item | Why it is not a task |
| --- | --- |
| Curtain, corridor, external-Wi-Fi captures | The campaign is closed (D-010). Reported as not measured. |
| Fan capture | The test room has no fan. Dropped 2026-11-17, recorded in `traceability.md`. |
| 300-second sessions | Not recorded; every capture is 60 or 90 s and is marked `SHORT`. |
| Second room / second device | Not available this term; one-room scope is stated in the PRD. |
| Three practitioner interviews | Not done; Proposal §3(c) says so. Do not add invented quotes. |
| Live dashboard and one-command recorder | Not built; PRD marks FR-05/FR-01 not started. The offline replay is the demo. |

## How to answer "is it finished?"

> "The pipeline is finished and reproducible; the evidence is pilot-grade. The
> headline is 30.7 % false positives and 64.4 % seated recall over six held-out
> sessions. What is missing is longer captures and the other interference
> conditions, and those are written down rather than hidden."
