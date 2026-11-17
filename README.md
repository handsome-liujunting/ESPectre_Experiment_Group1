# ESPectre — Wi-Fi Presence Detection That Survives Interference

Project for **1105 Project-Based Course** (Tianjin University / PolyU Joint School).
Host lab: **Huawei 2012 Wireless Lab**. Mentor: 龚政.

> One room, one ESP32-C6, one laptop. Detect whether a person is in the room using
> Wi-Fi channel state information (CSI), without changing hardware, without cameras,
> and without being fooled by fans, curtains, pets or traffic through the wall.

**Headline result — occupancy model v2.** Across six leave-one-session-out folds on the
`dorm-v2` recordings the model produced **83 false positives out of 270 empty windows
(30.7 %)** and **detected 174 of 270 seated windows (64.4 %)**. The same frozen model
produced **0 occupied windows on both held-out balcony sessions**.
[Reproduce it](docs/START-V2.md)

---

## What this repo contains

| Path | What it is |
| --- | --- |
| `docs/PROPOSAL-ESpectre-v1.0.md` | 1–2 page problem / evidence / solution / plan |
| `docs/PRD-ESpectre-MVP-v1.0.md` | 3–5 page MVP spec: scope, FR-01–FR-08, acceptance criteria |
| `docs/TechDesign-ESpectre-MVP-v1.0.md` | 2–3 page technical design: pipeline, data model, failure handling |
| `docs/DEMO-SCRIPT.md` | The 3-minute demo, word by word, with fallbacks |
| `docs/DATA-COLLECTION-PLAN.md` | Exact procedure for the measurement laptop |
| `docs/START-V2.md` | **Current model**: replay, measured limits, how to retrain |
| `docs/PILOT-20261029.md` | The 24-session October pilot, and why it is superseded |
| `docs/ai-decision-log.md` | Decisions, alternatives, why |
| `docs/traceability.md` | FR → module → evidence → status (honest) |
| `tools/` | Validator, feature and model code, LOSO evaluator |
| `AGENTS.md`, `MEMORY.md`, `REVIEW-CHECKLIST.md` | Repo rules, compact facts, pre-push checklist |

## Quick start

```bash
pip install -r requirements.txt -r requirements-train.txt
python tools/validate_sessions.py --data data/pilot-20261029 --manifest data/pilot-20261029/manifest.csv
python tools/loso_eval.py --data data/pilot-20261029 --output results/pilot-20261029
python tools/presence_v2.py replay --model results/v2/presence-v2.json --input data/dorm-v2/balcony-01-raw.npz
```

## Where the numbers come from

| Experiment | Data | Idle false-positive rate | Seated recall | Quotable? |
| --- | --- | ---: | ---: | --- |
| v2 LOSO | 6 `dorm-v2` sessions, 90 s | 30.7 % (83/270) | 64.4 % (174/270) | **Yes — headline** |
| v2 frozen model, balcony | 2 held-out sessions | 0 % occupied | n/a | Yes, as a null result |
| Pilot LOSO (2026-10-29) | 18 pilot sessions, 60 s | 0.0 % | 98.3 % | **No** |
| Pilot holdout | 4 pilot sessions | 0.0 % | 3.3 % | Only the 3.3 % |

The pilot LOSO figure is not evidence of generalisation. All 24 pilot sessions were
recorded in one evening in one dorm room, and every one of the 18 folds produced an
almost identical state sequence: idle → 51 `UNOCCUPIED` + 9 `UNKNOWN`, seated and motion
→ 59 `OCCUPIED` + 1 `UNKNOWN`, zero state flips in 60 s. The classifier was separating
recordings, not occupancy. The single independent seated session in the pilot holdout
scored **3.3 %**, which is the honest measure of how far that model generalised.

## Data in hand

32 sessions, one ESP32-C6, channel 11, decimated to 10 packets/s:

| Set | Sessions | Duration | Classes |
| --- | ---: | --- | --- |
| `data/pilot-20261029/` | 24 | 60 s | 8 idle, 8 static, 8 motion |
| `data/dorm-v2/` | 8 | 90 s | 3 idle, 3 static, 2 through-door (balcony) |

They clear the validator's 500-packet pilot floor but are `SHORT` against the 300 s
acceptance target, so the figures above are pilot-grade with wide error bars, and
`results/` says so on every line that quotes them.

## Scope

Classify 1-second windows of CSI into `idle` / `static_presence` / `motion`, smooth
them into `OCCUPIED` / `UNOCCUPIED` with a hysteresis state machine, and evaluate
leave-one-session-out. Everything else (multi-person counting, localisation, AP
firmware, cross-vendor support, month-long drift) is explicitly out of scope.

## Interference coverage — state it, do not hide it

| Condition | Sessions | Status |
| --- | ---: | --- |
| Through-door / through-wall (balcony, door closed) | 2 | recorded; model reports 0 occupied |
| Fan | 0 | **dropped 2026-11-17 — no fan available in the test room** |
| Curtain | 0 | not recorded |
| External Wi-Fi | 0 | not recorded |

The project title promises anti-interference. Three of the four conditions are still
unmeasured, and the one that is measured produced a null result.

## License / third-party code

`code/train_ml_model.py` in the original experiment repo is copied from the upstream
ESPectre project (GPL-3.0) and cannot run standalone here. It is kept for reference
only. Our own pipeline lives in `tools/` and does not import it.
