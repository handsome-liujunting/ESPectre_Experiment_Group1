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
