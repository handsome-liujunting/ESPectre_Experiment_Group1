# ESPectre — Demo Script (3 minutes, offline page)

**Goal of the demo:** prove one claim — *the system can see a person who is sitting
still, and it does not pretend the empty room is perfect.* The demo is a recorded
replay, not a live sensor: every curve on screen was computed from committed
captures before the session, so nothing can fail because of Wi-Fi, a board, or a
forgotten driver.

The page is `demo/index.html` (delivery copy: `demo-deliver/demo/`). Open it by
double-clicking. It needs no server and no network. Keep `demo-data.js` in the same
folder; the HTML alone will not load.

---

## Before you start (5 minutes before)

- [ ] Open `index.html` once, press F11 for full screen, and walk through all six
      steps with the arrow keys. Do not discover the layout in front of people.
- [ ] Have `results/v2-loso-reproduced.csv` open in a second window, and the command
      `python tools/v2_compare.py --data data/dorm-v2` already run once this session.
- [ ] **Fallback ready:** a 3-minute screen recording of the same walkthrough. If the
      laptop dies, switch to it in five seconds and say so.
- [ ] Close chat windows. The page is the only thing on screen.

## 0:00–0:20 — The problem, in one breath

> "Lighting and AC run on a schedule because we cannot measure occupancy cheaply.
> PIR fails the moment someone sits still. Cameras are refused in bedrooms. So we
> use the Wi-Fi that is already there: when a person is in the room, the channel
> changes — even when they are only breathing."

## 0:20–0:50 — What is running

> "This is an offline replay of eleven held-out captures: six for the headline, two
> balcony stress captures, three pilot captures. One ESP32-C6 recorded CSI at ten
> packets a second; each second becomes sixteen numbers, a logistic regression
> scores it, and a hysteresis state machine turns that into OCCUPIED, UNOCCUPIED or
> UNKNOWN. There is no live dashboard in this submission — the demo is the recording."

Point at the two files in the folder: `index.html` and `demo-data.js`. Say that the
page computes nothing; it only draws numbers produced by `demo/build_demo_data.py`.

## 0:50–2:30 — Six steps, arrow keys

State the point **before** pressing the arrow, so the audience can judge it.

1. **The mechanism** (`idle-02`). "A Wi-Fi link. When nobody moves the channel is
   still; a body absorbs and scatters it. That is the whole sensor."
2. **An empty room** (`idle-02`). "Ninety seconds, nobody in the room: 81 of 90
   windows decided UNOCCUPIED. The 83 false positives in the headline all come from
   a different empty capture, `idle-01` (83 of 90). One bad capture is the whole
   30.7 % — that is why the number is quoted with its denominator."
3. **Someone sitting still** (`static-presence-02`). "This is the hard case. PIR
   loses this person. The detector finds 85 of 90 windows."
4. **Where it fails** (`static-presence-01`). "Same label, different capture: 0 of
   90, 52 confidently empty, 38 unknown. This is not a demo bug; it is the 64.4 %
   headline. One seated capture in three does not look like the others."
5. **Someone moving** (`pilot-motion`). "Walking is easy, and that is why 98.3 % on
   the first campaign was misleading: motion dominates the features. The same first
   campaign, on the one seated capture the model had never seen, scored 2 of 60
   windows — and after hysteresis, 0 of 60. Quote all three or none."
6. **Through the balcony door** (`balcony-01`). "A person walking outside, door
   closed. The frozen model calls all 81 decided windows UNOCCUPIED. This is the only
   interference condition we recorded — a null result, not a pass."

## 2:30–3:00 — The number, and what is missing

Say the bad number first. It is the honest one, and leading with it stops the next
question from being "why did you hide it".

> "Six sessions, three empty, three seated, ninety seconds each, whole sessions held
> out. False positives **30.7 % — 83 of 270** empty windows called occupied. Seated
> recall **64.4 % — 174 of 270** seated windows found. Here is the command that
> reproduces both."

Show `results/v2-loso-reproduced.csv` and run the command on screen:

```bash
python tools/v2_compare.py --data data/dorm-v2 --output results/v2-loso-reproduced.csv
```

It prints the four numbers and exits non-zero if they drift.

Then name the limits, in one breath:

> "Three limits. One: every capture is 60 or 90 seconds against a 300-second
> acceptance target, so this is pilot-grade. Two: only the through-door interference
> condition was recorded; fan, curtain, corridor and external Wi-Fi are not measured,
> not passed. Three: one room, one device, and the capture and live-dashboard tools
> in the PRD were not built — the pipeline is offline only."

## Questions you will be asked (prepare these answers)

| Question | Answer in one line |
| --- | --- |
| "Why not just PIR?" | PIR is motion-only; the brief explicitly requires still-person detection. |
| "Why not a camera?" | Privacy; the deployment target is bedrooms and hotel rooms. |
| "Isn't this overfitting to your room?" | One room is the stated scope; sessions are held out whole, and the limitation is written down. |
| "What happens if two people?" | Not supported in v1; the label set has no multi-person class. |
| "How do you know 64 % recall isn't luck?" | Six sessions, per-fold numbers in the CSV, fixed seed 42, and the command reprints the same 174/270. It probably *is* noisy — that is why the number is quoted with its denominator. |
| "Why the ten-second clear delay?" | Asymmetry is a product decision: a late clear wastes energy, a missed entry breaks the feature. |
| "What if the Wi-Fi is busy?" | Not measured; external Wi-Fi is one of the interference conditions with zero sessions. |
| "Where is the live dashboard?" | Not built. The demo is a recorded replay, and saying so is cheaper than pretending. |

## Rules

1. Never show a number you cannot regenerate on the spot.
2. Never say "it works" without the metric name and its denominator.
3. If something breaks, say what broke. Silence reads as not understanding.
