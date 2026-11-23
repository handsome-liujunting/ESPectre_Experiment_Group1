# AI / Engineering Decision Log

One entry per decision that a reader might otherwise assume was arbitrary.
Newest at the bottom. Append, never rewrite history — supersede instead.

---

## D-001 — Evaluate leave-one-session-out, never random windows
**Date:** 2026-11-12 · **Status:** accepted
**Context:** the earlier experiment reported 76.3 % CV F1 but failed its deployment
gate (occupancy 70 % ⇒ recall 0.00 %). The gap suggests the split, not the model.
**Decision:** every reported number comes from LOSO over whole sessions.
**Alternatives:** random window split (rejected: windows from one session share
the same person, room and gain, so the test fold is memorised); k-fold grouped by
file (rejected: with 8 sessions per class, folds are too small and the hold-out
definition drifts between runs).
**Consequences:** fewer training sessions per fold ⇒ noisier numbers. Accepted:
a noisy honest number beats a stable fake one.

## D-002 — Keep three classes internally, output two states
**Date:** 2026-11-12 · **Status:** accepted
**Context:** the brief requires still-person detection; collapsing to binary too
early loses the evidence that separates "empty" from "still".
**Decision:** classify `idle`/`static`/`motion`, then sum the two occupied
probabilities and smooth.
**Alternatives:** binary classifier trained directly (rejected: it hides which
error is being made); separate still-detector gated by motion (rejected: two
models, two failure modes, no benefit at this data size).
**Consequences:** three classes must each have enough sessions; 8 per class is the
current minimum.

## D-003 — Asymmetric hysteresis: enter fast, leave slow
**Date:** 2026-11-12 · **Status:** accepted
**Context:** naive per-window output flaps; operators stop trusting a flapping
sensor.
**Decision:** enter `OCCUPIED` after 2 consecutive high windows (≈ 2 s); leave only
after 10 s below threshold.
**Alternatives:** symmetric debounce (rejected: a person pausing at the door would
turn the lights off); Kalman/HSMM smoothing (rejected: unjustifiable complexity at
10 pps with 24 sessions).
**Consequences:** up to 10 s of wasted energy after a room empties. Documented in
PRD BR-3 rather than hidden.

## D-004 — Interference is a stress table, not a headline metric
**Date:** 2026-11-12 · **Status:** accepted
**Context:** no interference sessions exist yet; merging them into one F1 would
hide the failure the project is actually about.
**Decision:** train and report the headline number on clean sessions; report the
stress set separately, per scenario.
**Alternatives:** include interference in training (rejected for now: 0 sessions,
and it would let the model learn the room instead of the phenomenon).
**Consequences:** the report will contain a visibly bad table. That is intended.

## D-005 — Write our own pipeline instead of fixing the inherited script
**Date:** 2026-11-12 · **Status:** accepted
**Context:** `code/train_ml_model.py` is upstream ESPectre code; it imports
`tools.lib.*` which is not in this repo. It cannot run here at all.
**Decision:** `tools/` contains a minimal, self-contained pipeline; the upstream
file stays as reference only.
**Alternatives:** vendor the missing `tools/lib` (rejected: thousands of lines of
someone else's research code that nobody on the team can defend in a viva);
rewrite the import shim (rejected: hides that the file is unusable).
**Consequences:** fewer features than upstream, all of them explainable.

## D-006 — Documents in English, conversation in Chinese
**Date:** 2026-11-12 · **Status:** accepted
**Context:** assessment guidelines and the mentor's lab material are English; the
team works in Chinese.
**Decision:** submitted docs in English; chat, commit discussion and this log's
informal notes may be Chinese.
**Alternatives:** bilingual duplicates (rejected: two sources of truth that drift,
and the guidelines explicitly penalise padded documents).

## D-007 — One root README, delete the nested duplicate
**Date:** 2026-11-12 · **Status:** accepted
**Context:** the experiment repo has `README.md` at root and an identical one
inside `ESPectre_Experiment_Group1/`.
**Decision:** single root README; the nested folder keeps only data and code.
**Consequences:** links from the old inner README must be updated in the same commit.

## D-008 — Revise targets, never silently lower them
**Date:** 2026-11-12 · **Status:** accepted
**Context:** PRD targets (recall ≥ 0.90, FPR ≤ 0.10) are guesses until the first
LOSO run exists.
**Decision:** if the baseline misses them, report the measured value, keep the old
target visible with a dated revision note, and change it only with the mentor.
**Consequences:** the report may show targets the project does not meet. That is
the point of having targets.

## D-009 — No model export until the metrics exist
**Date:** 2026-11-12 · **Status:** accepted
**Context:** the earlier run never exported a model because it gated export on
thresholds it did not meet.
**Decision:** export the model together with the metrics file that justifies it,
in the same commit; the dashboard refuses a model without metrics.
**Consequences:** no "demo model" that cannot be traced to a number.

## D-010 — Freeze the capture campaign; state the missing conditions as limitations
**Date:** 2026-11-23 · **Status:** accepted
**Context:** the submission has 24 pilot and 8 `dorm-v2` sessions: empty, seated,
walking and through-door. Curtain, corridor, external Wi-Fi, a fan and 300-second
captures do not exist, and another campaign is not affordable before the deadline.
**Decision:** the dataset is final. Do not record more conditions, do not promise
them in the PRD, and do not describe their absence as work in progress. They are
listed as not measured in `traceability.md`, the PRD and the demo page.
**Alternatives:** a token curtain/Wi-Fi capture (rejected: two 90 s sessions cannot
support a per-scenario false-alarm claim, and a thin table invites more questions
than an honest gap); extending every session to 300 s (rejected: new hardware time,
and the existing 60/90 s numbers would still be the only ones with a full pipeline).
**Consequences:** FR-07 stays partial (one of four conditions), the 300-second
acceptance target stays unmet, and the report says both. The marks lost here are
smaller than the marks lost to a claim that cannot be reproduced.

## D-011 — When two committed results disagree, the newest replay wins
**Date:** 2026-11-23 · **Status:** accepted
**Context:** `results/v2/CSI-8-session-results.csv` (pilot model on the eight
`dorm-v2` captures) reports 37 occupied windows on `balcony-01`; the v2 replay
reports 0. The pilot `loso_metrics.json` also predates the balcony captures and
reports zero sessions for every stress condition.
**Decision:** the newer replay is authoritative. The demo stress table reads the v2
balcony replays; the older CSV stays in the repository for history and is marked
superseded in `results/README.md`. Do not edit the old numbers by hand.
**Alternatives:** delete the old CSV (rejected: results are never deleted, only
superseded); average the two (rejected: they come from different models and
different protocols, so an average is meaningless).
**Consequences:** a reader who opens the old file sees a pointer to the current one;
a reader who opens the README sees which number to quote.

## D-012 — The demo is an offline replay page, not a live dashboard
**Date:** 2026-11-23 · **Status:** accepted
**Context:** `tools/live_dashboard.py` was specified but never written. The upstream
live tooling needs a board and a network, and the stationary-presence path is not
published upstream. A live demo would add failure modes without adding evidence.
**Decision:** the demo is one HTML file plus one data file, opened from disk. Every
curve is computed in advance from committed captures by `demo/build_demo_data.py`.
**Alternatives:** build the live dashboard (rejected: one and a half days for a
display layer, no new evidence); drive the demo from a terminal (rejected: the
assessor cannot see the waterfall or the state ribbon).
**Consequences:** the demo cannot fail because of Wi-Fi, and it cannot show anything
the committed data does not contain. PRD FR-05 is marked not started, not "demoed".
