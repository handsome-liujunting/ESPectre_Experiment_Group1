# Traceability — requirement to evidence

Every requirement in the PRD, where it lives, what proves it, and its real status.
Update this file in the same commit that changes the status. `not started` is a
valid, honest status.

**Last updated:** 2026-11-16 (pilot import, offline model and measured evaluation)

| FR | Requirement (short) | Module / file | Evidence in repo | Status |
| --- | --- | --- | --- | --- |
| FR-01 | Record a labelled session with one command | `tools/capture_session.py` (specified) | — | **not started** |
| FR-02 | Validate sessions + build manifest | `tools/validate_sessions.py` | `data/manifest.csv`, validator stdout | **implemented** (24 imported and validated; SHORT) |
| FR-03 | Window features + 3-class classifier | `tools/presence.py`, `tools/loso_eval.py` | `results/presence_model.json` | **pilot implemented** (static holdout missed) |
| FR-04 | Hysteresis state machine | `tools/presence.py` | state counts in `results/loso_metrics.json` | **offline replay implemented** (timed live transitions pending) |
| FR-05 | Live dashboard | `tools/live_dashboard.py` (specified) | screen recording | **not started** |
| FR-06 | LOSO evaluation + report | `tools/loso_eval.py` | `results/LOSO-REPORT.md` | **pilot evaluated** (full acceptance pending) |
| FR-07 | Interference stress table | `tools/loso_eval.py` | stress section in `results/loso_metrics.json` | **pending data** (0 interference sessions) |
| FR-08 | Machine-readable metrics with seed + hash | `tools/loso_eval.py` | metrics JSON header | **implemented** |

## Document-level traceability

| Document | Requirement from guidelines | Where satisfied |
| --- | --- | --- |
| Proposal | problem, user, evidence, solution, feasibility, plan | `docs/PROPOSAL-ESpectre-v1.0.md` §1–§9 |
| PRD | 3–5 core functions, out of scope, journey, FR IDs, rules, acceptance, NFR, metrics | `docs/PRD-ESpectre-MVP-v1.0.md` §3–§9 |
| Tech Design | structure, choices + simpler alternative, data model, key impl, failure, run, cost | `docs/TechDesign-ESpectre-MVP-v1.0.md` §1–§7 |
| AGENTS.md | repository instructions | `AGENTS.md` |
| Decision record | why, alternatives | `docs/ai-decision-log.md` D-001…D-009 |

## Known gaps (stated, not hidden)

- The offline model uses 18 training captures. Four original holdouts are evaluated separately and two original exclusions are preserved. The single seated holdout was missed.
- 0 / 3 practitioner interviews. Proposal §3(c) says so.
- Interference sessions: 0 recorded. FR-07 cannot be claimed.
- Team split and deadline unconfirmed; plan owners are placeholders.

## How to update a row

1. Change `Status` to `implemented` only if the evidence file exists in the repo.
2. Add the file path and, for numbers, the data hash + seed.
3. If a requirement changed, write `changed` and link the decision-log entry.
4. Never delete a row. Mark `dropped` and say why.
