# ESPectre — Wi-Fi Presence Detection That Survives Interference

Project for **1105 Project-Based Course** (Tianjin University / PolyU Joint School).
Host lab: **Huawei 2012 Wireless Lab**. Mentor: 龚政.

> One room, one ESP32-C6, one laptop. Detect whether a person is in the room using
> Wi-Fi channel state information (CSI), without changing hardware, without cameras,
> and without being fooled by fans, curtains, pets or traffic through the wall.

**Status: Week 1 — documents written, pilot data collected, baseline not yet run.**
Nothing in this repo has been validated end to end yet. See
[docs/traceability.md](docs/traceability.md) for what is real and what is not.

---

## What this repo contains

| Path | What it is |
| --- | --- |
| `docs/PROPOSAL-ESpectre-v1.0.md` | 1–2 page problem / evidence / solution / plan |
| `docs/PRD-ESpectre-MVP-v1.0.md` | 3–5 page MVP spec: scope, FR-01…FR-06, acceptance criteria |
| `docs/TechDesign-ESpectre-MVP-v1.0.md` | 2–3 page technical design: pipeline, data model, failure handling |
| `docs/DEMO-SCRIPT.md` | The 3-minute demo, word by word, with fallbacks |
| `docs/DATA-COLLECTION-PLAN.md` | Exact procedure for the measurement laptop |
| `docs/ai-decision-log.md` | Decisions, alternatives, why |
| `docs/traceability.md` | FR → module → evidence → status (honest) |
| `tools/validate_sessions.py` | Checks every `.npz` session against the data contract |
| `AGENTS.md` | Rules for AI assistants working in this repo |
| `MEMORY.md` | Compact project facts (numbers, paths, gotchas) |
| `REVIEW-CHECKLIST.md` | Pre-push checklist |

## Quick start

```bash
pip install -r requirements.txt
python tools/validate_sessions.py --data data --manifest data/manifest.csv
```

Expected: one row per session, a per-class summary, and exit code 0. Any `FAIL`
line means the session is unusable for training and must be re-recorded.

## The one-sentence scope

**Classify 1-second windows of CSI into `idle` / `static` / `motion`, then smooth
them into `OCCUPIED` / `UNOCCUPIED` with a hysteresis state machine — evaluated
leave-one-session-out.**

Everything else (multi-person counting, localisation, AP firmware, cross-vendor
support, month-long drift) is explicitly out of scope for the MVP.

## Dataset in hand

24 pilot sessions recorded on a separate machine: 8 `idle`, 8 `static_presence`,
8 `motion`, 10 packets/s, ~300 s each. They are **not** in this repo yet —
see `docs/DATA-COLLECTION-PLAN.md` for how to export and validate them.

## License / third-party code

`code/train_ml_model.py` in the original experiment repo is copied from the
upstream ESPectre project (GPL-3.0) and cannot run standalone here. It is kept
for reference only. Our own pipeline lives in `tools/` and does not import it.
