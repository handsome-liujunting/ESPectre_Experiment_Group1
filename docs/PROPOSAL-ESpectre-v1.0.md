# ESPectre: Presence Detection That Survives Interference

**Proposal v1.0 — 2026-11-12**
1105 Project-Based Course · Team: _[袁培淞 刘俊廷]_
Host lab: Huawei 2012 Wireless Lab · Mentor: 龚政

---

## 1. Problem

Buildings spend energy on rooms that are empty. Lighting and HVAC in homes,
offices and hotels are usually scheduled by clock, not by occupancy, because
occupancy is expensive to measure:

- **PIR** is cheap but goes blind the moment a person stops moving — exactly the
  case that matters for a person reading or working at a desk.
- **Cameras** work, but people reject them in bedrooms and hotel rooms, and they
  are the first thing a privacy review removes.
- **Dedicated presence sensors** mean new wiring, new batteries and a new vendor
  for every room.

Wi-Fi is already installed in all of these rooms. When a person is in a room, the
channel state information (CSI) between two commodity Wi-Fi devices changes —
during walking, but also during breathing, typing and page-turning. So the sensing
hardware is free; the problem is entirely in the signal processing.

The hard part is not detecting a walking person. **The hard part is not being
fooled.** A fan, a curtain in a draught, a cat, a robot vacuum, a person walking
in the corridor behind the wall, or a neighbouring AP's traffic all move the
channel in ways that look like a person. A detector that fires on every curtain
is worse than no detector, because the building operator turns it off.

## 2. Who has this problem

| User | What they need | Why current tools fail |
| --- | --- | --- |
| Facility / building operator | Per-room occupancy to drive HVAC and lighting setback | Scheduling is blind; PIR misses still occupants |
| Hotel operator | Room occupied / vacant, without cameras | Camera-based systems are a privacy and legal problem |
| Smart-home resident | Lights and HVAC follow me, no wearables | Phone-based presence dies with the battery |
| The lab (this project) | A measurable, reproducible CSI sensing baseline | No shared dataset or protocol in the group yet |

**Primary user for the MVP:** one room, one ESP32-C6 transmitter/receiver pair,
one laptop. The deliverable is a detector a lab engineer can run for 10 minutes
and get a number they trust.

## 3. Evidence

Three kinds of evidence, with their status stated honestly.

**(a) Requirement evidence — recorded.** The project brief assigned by the Huawei
2012 Wireless Lab (`2026 项目汇总`, item 4) asks for presence detection including
stillness, with rejection of three interference classes: in-room appliances
(fan, curtain, pet, robot vacuum), through-wall / out-of-boundary movement, and
external wireless interference. This is a real operator requirement, not one we
invented.

**(b) Measurement evidence — recorded by us.** 24 pilot sessions, 8 per class
(`idle`, `static_presence`, `motion`), 10 packets/s, 60 s per session, single
room, single device. First observation: windowed subcarrier-amplitude variance
separates `idle` from `motion` easily, while `static_presence` sits close to
`idle` and is where a naive detector loses recall. This is why the MVP keeps
three classes internally and only collapses to occupied/unoccupied at the output.

**(c) Practitioner interviews — planned, not yet done.** We have not interviewed
facility staff. Until we do, the workflow claims in §2 are **assumptions**, and
are marked as such. Interview guide: Appendix A. Target: 3 short interviews
(1 facility/HVAC engineer, 1 hotel or dormitory manager, 1 lab researcher).

## 4. Proposed solution (MVP)

A laptop-side detector fed by one ESP32-C6 over Wi-Fi:

1. **Capture** CSI at ~10 packets/s and log a labelled session with one command
   (specified; not built — captures are committed).
2. **Classify** each 1 s window into `idle` / `static` / `motion` (16 values per
   second: 8 subcarrier bands × spread/change → logistic regression).
3. **Smooth** the per-window probabilities with a hysteresis state machine
   (enter occupied fast, leave slow) → `OCCUPIED` / `UNOCCUPIED` / `UNKNOWN`.
4. **Show** the current state, confidence and last 60 s on an offline replay page
   built from held-out captures; no live dashboard.
5. **Evaluate** offline, leave-one-session-out, and emit a metrics report.

The detector never leaves the laptop in v1. No firmware changes, no cloud, no
camera, no wearable.

## 5. Feasibility

| Question | Answer | Evidence |
| --- | --- | --- |
| Is the hardware available? | Yes — ESP32-C6 boards + laptop in the lab | Confirmed with mentor |
| Can we collect enough data? | 24 pilot + 8 `dorm-v2` sessions already collected; campaign closed | `data/pilot-20261029/manifest.csv` |
| Is the compute affordable? | Laptop CPU only, 16 values per second, logistic regression | ~10 pps input ⇒ trivial |
| Is the scope one week of work? | Documents + baseline: 1 day; full MVP: ~5 working days | See §7 |
| What is the biggest risk? | `static_presence` recall and curtain/fan false alarms | See §8 |

## 6. What we deliberately will NOT do in v1

- Multi-person counting or localisation.
- Any change to ESP32 firmware or the Wi-Fi protocol.
- Cross-vendor / cross-chip generalisation (one device model only).
- Month-scale drift, furniture rearrangement, open-plan spaces.
- A production installation or a phone app.

These are cut so that the one thing we claim — *still-person detection with
controlled false alarms* — can actually be measured in the time available.

## 7. Plan and milestones

Assumes ~5 working days after the documents are approved. **Dates to be confirmed
with the mentor and the team.**

| Day | Work | Output | Owner |
| --- | --- | --- | --- |
| D1 | Import + validate 24 sessions; freeze data contract | `data/manifest.csv`, validation report | _袁培淞_ |
| D2 | Window features + logistic-regression baseline, LOSO | baseline metrics JSON | _刘俊廷_ |
| D3 | State machine + offline replay page | demo page runs | _袁培淞_ |
| D4 | Through-door interference capture + stress replay | stress table (1 of 4 conditions) | _刘俊廷_ |
| D5 | Report, traceability table, demo rehearsal | final docs + video | _袁培淞_ |

## 8. Risks and mitigations

| # | Risk | Impact | Mitigation |
| --- | --- | --- | --- |
| R1 | Train/test leakage from splitting windows randomly | Metrics look great, deployment fails | Leave-one-session-out only; no random window split ever |
| R2 | `static_presence` mistaken for empty room | The core claim fails | Keep 3 classes; report static recall separately; tune decision threshold on validation sessions only |
| R3 | Fan / curtain / corridor movement read as a person | False alarms, user turns it off | Dedicated stress sessions, reported as a separate table, not hidden in one average |
| R4 | Data lives on one laptop, not in the repo | Nobody can reproduce | Validated export + manifest committed; `.npz` committed if size allows |
| R5 | Inherited ESPectre training code does not run standalone | Wasted days | Our pipeline is self-contained in `tools/`; upstream code is reference only |
| R6 | No interviews yet | Problem statement is partly assumed | 3 interviews in week 1; assumptions labelled in this document until then |

## 9. Open questions for the mentor

1. Is one device pair acceptable for the MVP, or is multi-link fusion required
   already in the first review?
2. Which interference class matters most to the lab — in-room appliances,
   through-wall, or external Wi-Fi traffic?
3. Is there an existing room/floor plan we should test in, or do we build our own
   test corner?

---

## Appendix A — Interview guide (not yet conducted)

Ask, do not lead. Record the answer, not the interpretation.

1. How do you currently decide when to turn off lights/AC in a room? Who sets it?
2. When was the last time that rule was wrong, and what did it cost?
3. Have you tried a presence sensor? What made you keep it or remove it?
4. If a sensor said "occupied" when the room was empty, how many times per day
   would be too many?
5. Who would have to approve putting a Wi-Fi-based sensor in this room?

**Status of interviews: 0 / 3 completed.** Results will be appended as
`docs/research/interview-notes.md` with date, role and verbatim quotes.
