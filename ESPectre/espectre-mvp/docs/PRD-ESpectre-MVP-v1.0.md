# ESPectre MVP — Product Requirements Document

**Version 1.0 — 2026-11-12** · Owner: _[袁培淞 刘俊廷]* · Mentor: 龚政 (Huawei 2012 Wireless Lab)
Companion docs: [Proposal](PROPOSAL-ESpectre-v1.0.md) · [Tech Design](TechDesign-ESpectre-MVP-v1.0.md) · [Demo script](DEMO-SCRIPT.md)

---

## 1. Overview

ESPectre turns a pair of commodity Wi-Fi devices into an occupancy sensor. One
ESP32-C6 sends frames; a laptop reads the channel state information (CSI) and
decides whether the room is occupied, with the person either moving or sitting
still. The MVP proves this on **one room, one device pair, one laptop**, and
publishes a number that can be reproduced by re-running one command.

**MVP in one sentence:** given 60 s of CSI, output `OCCUPIED` / `UNOCCUPIED` /
`UNKNOWN` with a confidence, and report recall, false-positive rate and latency
measured leave-one-session-out.

## 2. Users and top tasks

| User | Top task | Success looks like |
| --- | --- | --- |
| Lab engineer (primary) | Record a session, train, evaluate, get a metrics table | One command in, one report out, no manual bookkeeping |
| Building operator (secondary, by proxy) | Know whether a room is occupied | A state that is right, and does not flap |
| Course assessor | Reproduce a claim | `python tools/loso_eval.py` reproduces the number in the report |

There is **one** persona in the MVP. The operator is represented by the mentor's
requirement, not by a shipped UI for them.

## 3. Scope

### In scope (v1)

- Single room, single ESP32-C6, packets arriving at ~10/s.
- Labels: `idle` (no one), `static_presence` (person present, not moving),
  `motion` (person walking / shifting).
- Window-level 3-class classification; output-level binary occupancy.
- Temporal smoothing with an explicit state machine (no per-window output shown
  to the user as truth).
- Live dashboard on the laptop.
- Offline evaluation, leave-one-session-out, plus a separate interference stress
  table.
- A committed session manifest so any claim can be traced to files.

### Out of scope (v1) — and why

| Not doing | Reason |
| --- | --- |
| Counting people | Needs a different label set and far more data |
| Localisation / room mapping | Multi-AP, different hardware |
| Firmware or protocol changes | The brief says "do not modify hardware" |
| Phone app, cloud service | Not needed to prove the sensing claim; adds deployment surface |
| Cross-vendor / cross-chip | No second chip model available this term |
| Weeks-long drift, furniture changes | No time-series long enough to claim it |
| Through-wall *detection* | Through-wall movement is treated as **interference to reject**, not as a feature |

## 4. User journey (MVP)

1. Engineer opens the laptop, runs `python tools/capture_session.py --label motion --minutes 5`.
2. The tool prints packet rate and a live sparkline; at the end it writes
   `data/motion/motion_labA_c6-01_20261112-1410.npz` plus a `.json` sidecar.
3. Engineer runs `python tools/validate_sessions.py --data data` — every session
   is either `PASS` or `FAIL` with a reason.
4. Engineer runs `python tools/loso_eval.py --data data` — trains once per held-out
   session, writes `results/loso_metrics.json` and `results/LOSO-REPORT.md`.
5. Engineer runs `python tools/live_dashboard.py` and walks in, sits still 60 s,
   walks out. The dashboard shows `UNOCCUPIED → OCCUPIED → UNOCCUPIED` and the
   latency of each transition.
6. That is the demo. Nothing is edited by hand afterwards.

## 5. Functional requirements

Stable IDs. Do not renumber; mark removed requirements `dropped` instead.

| ID | Requirement | Priority | Status (2026-11-12) |
| --- | --- | --- | --- |
| **FR-01** | Record a labelled CSI session with one command, writing `.npz` (`csi_data`, `label`) + `.json` metadata (room, device, rate, duration, packets, notes) | P0 | not started |
| **FR-02** | Validate every session against the data contract and emit `data/manifest.csv` | P0 | **implemented** (`tools/validate_sessions.py`) |
| **FR-03** | Extract windowed features (1 s window, 1 s hop) from raw CSI and classify each window into `idle` / `static` / `motion` | P0 | not started |
| **FR-04** | Convert window probabilities into `OCCUPIED` / `UNOCCUPIED` / `UNKNOWN` via hysteresis, with enter/leave debounce and a stale-sensor timeout | P0 | not started |
| **FR-05** | Show live state, confidence, recent history and transition latency on a laptop dashboard | P0 | not started |
| **FR-06** | Evaluate leave-one-session-out and publish recall, false-positive rate, F1, per-class confusion, onset/clear latency, CPU and memory | P0 | not started |
| **FR-07** | Run an interference stress set (fan on, curtain moving, corridor movement) and report it as a separate table, never merged into the headline number | P1 | not started |
| **FR-08** | Emit a machine-readable metrics JSON with seed, data hash and command line | P1 | not started |

**Minimum shippable set:** FR-01, FR-02, FR-03, FR-04, FR-06. If time runs out,
FR-05 is replaced by a terminal readout and FR-07 by "collected, not yet evaluated".

## 6. Business rules and edge cases

| # | Rule |
| --- | --- |
| BR-1 | A window is only classified if it contains ≥ 0.7 s of packets; otherwise the window is `UNKNOWN` and inherits the previous state. |
| BR-2 | `OCCUPIED` requires the smoothed occupancy probability ≥ 0.60 for 2 consecutive windows. |
| BR-3 | `UNOCCUPIED` requires the smoothed probability ≤ 0.40 continuously for 10 s (leave debounce). This is deliberately asymmetric: a missed exit wastes energy, a missed entry breaks the feature. |
| BR-4 | If no packet arrives for 5 s, the state becomes `UNKNOWN` and is displayed as such; it must never silently stay `OCCUPIED`. |
| BR-5 | `static_presence` counts as occupied. A detector that only sees motion does not satisfy the brief. |
| BR-6 | Sessions are the unit of splitting. A window is never in train and test at once, even across folds. |
| BR-7 | Thresholds are chosen on validation sessions and then frozen; the test fold is touched once. |
| BR-8 | Interference sessions are excluded from the headline metric and reported separately. |

## 7. Acceptance criteria

Written as Given/When/Then so they can be turned into tests.

**FR-02 — validation**
- Given a directory of sessions, when `validate_sessions.py` runs, then every
  session gets `PASS`/`FAIL` with a reason and the process exits non-zero if any
  session fails.

**FR-03 — classification**
- Given 24 held-out sessions (8 per class), when LOSO evaluation runs, then
  **presence recall ≥ 0.90 and false-positive rate ≤ 0.10**.
- Given the `static_presence` fold, when evaluated, then **static recall ≥ 0.80**.
- These are *targets to freeze after the first baseline*. If the first baseline
  misses them, the number is reported as measured and the target is revised with
  the mentor — it is not quietly lowered in the report.

**FR-04 — state machine**
- Given a stream that switches from idle to motion, when the person enters,
  then `OCCUPIED` appears within **2 s**.
- Given a stream that switches from static to idle, when the person leaves, then
  `UNOCCUPIED` appears within **10 s** and no earlier than 3 s.
- Given a steady occupied room, when observed for 5 minutes, then the state does
  not flap more than **2 transitions per minute**.

**FR-05 — dashboard**
- Given the dashboard is running, when the classifier emits a window, then the
  displayed state updates within **1 s** and the last 60 s of probability is visible.

**FR-06 — evaluation report**
- Given the same data and seed, when `loso_eval.py` runs twice, then the metrics
  JSON is identical.
- Given the report, when an assessor reads it, then every number names the
  command, the data hash and the number of sessions behind it.

**FR-07 — interference**
- Given the stress sessions, when evaluated with the frozen model, then the report
  states per-scenario false-alarm rate, including the cases where it is bad.

## 8. Non-functional requirements

| Area | Requirement |
| --- | --- |
| Rate | Works at 10 packets/s; degrades gracefully (not crash) at 5 packets/s |
| Latency | End-to-end decision latency < 2 s at 10 pps on the laptop CPU |
| Compute | < 25 % of one core, < 300 MB RSS during live operation |
| Portability | Python 3.10+, Windows and Linux, CPU only, no GPU, no cloud |
| Reproducibility | Fixed seed; data hash in every metrics file; no manual edits to results |
| Privacy | CSI only; no camera, no audio, no per-person identification |
| Failure | Every failure mode in Tech Design §6 has a defined user-visible behaviour |

## 9. Success metrics

| Metric | Target | How measured |
| --- | --- | --- |
| Presence recall (LOSO) | ≥ 0.90 | `results/loso_metrics.json` |
| False-positive rate (LOSO) | ≤ 0.10 | same |
| Static-presence recall | ≥ 0.80 | same, `static_presence` fold |
| Onset latency | ≤ 2 s | timestamped transitions in a recorded replay |
| Clear latency | ≤ 10 s | same |
| Flap rate | ≤ 2 / min | same |
| Reproducibility | identical JSON on rerun | diff of two runs |

Any metric we cannot measure is listed as "not measured" rather than estimated.

## 10. Constraints, assumptions, open questions

**Constraints**
- Do not modify hardware or firmware; the sensing device is used as shipped.
- Low measurement rate (~10 pps), not a research-grade CSI collector.
- One room this term; a second room only if the lab grants access.

**Assumptions (unvalidated)**
- A1. The room has one dominant person; multi-person is out of scope.
- A2. The ESP32-C6 stays powered and associated for the whole session.
- A3. 300 s per session is enough for a stable per-session decision.
- A4. The three labelled classes cover the mentor's "still, walking, absent" cases.

**Open questions**
- Q1. Is one device pair enough for the first review, or is multi-link fusion
  expected now?
- Q2. Which interference class should the stress set prioritise?
- Q3. May we record in a real office/hotel room, or only in the lab?
- Q4. Deadline and team split — not yet confirmed; the plan in the Proposal uses
  placeholder owners.
