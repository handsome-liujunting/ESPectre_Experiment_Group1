# Traceability — requirement to evidence

Every requirement in the PRD, where it lives, what proves it, and its real status.
Update this file in the same commit that changes the status. `not started` is a
valid, honest status.

**Last updated:** 2026-11-23 (scope frozen; documents aligned to the v2 result)

| FR | Requirement (short) | Module / file | Evidence in repo | Status |
| --- | --- | --- | --- | --- |
| FR-01 | Record a labelled session with one command | `tools/capture_session.py` (specified) | none | **not started** — downgraded to P2 by D-010; captures are committed, not recorded live |
| FR-02 | Validate sessions + build manifest | `tools/validate_sessions.py`, `tools/import_pilot.py` | `data/pilot-20261029/manifest.csv`; 24 sessions, 8/8/8, `PASS` at the 500-packet floor, `SHORT` against the 300 s target | **implemented** |
| FR-03 | Window features + 3-class classifier | `tools/presence.py`, `tools/presence_v2.py` | `results/pilot-20261029/presence_model.json`, `results/v2/presence-v2.json` | **implemented (pilot), changed to v2** — 16 values, logistic regression |
| FR-04 | Hysteresis state machine | `tools/presence.py` `states()` | state counts in `results/pilot-20261029/loso_metrics.json` | **offline replay implemented**; timed live transitions not measured |
| FR-05 | Live dashboard | `tools/live_dashboard.py` (specified) | offline replay page (`demo/index.html`) | **not started** — replaced by the offline page, D-012 |
| FR-06 | LOSO evaluation + report | `tools/loso_eval.py`, `tools/v2_compare.py` | `results/pilot-20261029/LOSO-REPORT.md`, `results/v2-loso-reproduced.csv` | **pilot evaluated**; v2 headline reproducible by one command; full-duration acceptance not met |
| FR-07 | Interference stress table | `tools/presence_v2.py` replay | `results/v2/CSI-v2-balcony-01.csv`, `CSI-v2-balcony-02.csv` | **partial — 1 of 4 conditions** (through-door, 2 sessions, null result); fan dropped, curtain/corridor/external Wi-Fi not recorded (D-010) |
| FR-08 | Machine-readable metrics with seed + hash | `tools/loso_eval.py` | metrics JSON header | **implemented**; `source_commit` written from `git rev-parse HEAD` or `--commit` |

## Document-level traceability

| Document | Requirement from guidelines | Where satisfied |
| --- | --- | --- |
| Proposal | problem, user, evidence, solution, feasibility, plan | `docs/PROPOSAL-ESpectre-v1.0.md` §1–§9 |
| PRD | 3–5 core functions, out of scope, journey, FR IDs, rules, acceptance, NFR, metrics | `docs/PRD-ESpectre-MVP-v1.0.md` §3–§9 |
| Tech Design | structure, choices + simpler alternative, data model, key impl, failure, run, cost | `docs/TechDesign-ESpectre-MVP-v1.0.md` §1–§7 |
| AGENTS.md | repository instructions | `AGENTS.md` |
| Decision record | why, alternatives | `docs/ai-decision-log.md` D-001…D-012 |

## Known gaps (stated, not hidden)

- **Headline is 30.7 % idle false positives and 64.4 % seated recall** (v2, six
  `dorm-v2` sessions). Anything better comes from the pilot, which is superseded.
- Every capture is `SHORT` against the 300 s / 3000-packet acceptance target. The
  500-packet floor they do pass is a pilot floor, not an acceptance bar.
- FR-07: only the through-door condition was recorded (2 sessions, 0 of 162 decided
  windows occupied). The fan condition was **dropped** (no fan in the test room,
  2026-11-17); curtain, corridor and external Wi-Fi were **not recorded**, and
  D-010 closes the campaign rather than promising them.
- 0 / 3 practitioner interviews. Proposal §3(c) says so.
- Team split and deadline unconfirmed; plan owners are placeholders.
- `results/v2/CSI-feature-comparison.csv` came from a script that is not in the
  repository. Its `normalized_temporal` row — the one the headline rests on — is
  reproduced exactly by `tools/v2_compare.py`. The other three rows are exploration.
- `results/v2/CSI-8-session-results.csv` is superseded: it applies the pilot model
  to the eight `dorm-v2` captures and reports 37 occupied windows on `balcony-01`,
  while the newer v2 replay reports 0. Cite the v2 replay, not that file (D-011).

## How to update a row

1. Change `Status` to `implemented` only if the evidence file exists in the repo.
2. Add the file path and, for numbers, the data hash + seed.
3. If a requirement changed, write `changed` and link the decision-log entry.
4. Never delete a row. Mark `dropped` and say why.
