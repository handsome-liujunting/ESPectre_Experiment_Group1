# ESPectre — Demo Script (3 minutes)

**Goal of the demo:** prove one claim — *the system knows the room is occupied even
when the person is sitting still, and it does not fire when the room is empty.*

Rehearse it twice. Anything you cannot say in plain words is not understood yet.

---

## Before you start (5 minutes before)

- [ ] Laptop charged, dashboard already opened once (no first-run install in front of people).
- [ ] ESP32-C6 powered, associated, packet rate visible ≥ 8 pps.
- [ ] Terminal at repo root, font size ≥ 16.
- [ ] `results/LOSO-REPORT.md` open in a second tab.
- [ ] **Fallback ready:** a 60 s screen recording of a successful run, and
      `results/loso_metrics.json`. If live fails you switch to these in 5 seconds
      and say so — you do not debug in front of the audience.
- [ ] Room quiet, door state as in the recorded sessions.

## 0:00–0:20 — The problem, in one breath

> "Lighting and AC run on a schedule because we cannot measure occupancy cheaply.
> PIR fails the moment someone sits still. Cameras are refused in bedrooms.
> So we use the Wi-Fi that is already there: when a person is in the room, the
> channel changes — even when they are only breathing."

Show: the room, the two devices, the laptop. Nothing else on screen.

## 0:20–0:50 — What is running

> "One ESP32-C6 sends frames, the laptop reads CSI at ten packets a second.
> Every second we compute eight features, classify the second as empty, still, or
> moving, and then smooth that into a room state — occupied or not.
> The smoothing matters: a raw per-second answer flaps, and an operator will not
> trust it."

Show: architecture diagram in the Tech Design (zoom to the five boxes). 10 seconds, not 60.

## 0:50–2:10 — Live demonstration

State the expectation **before** each action, so the audience can judge it.

1. **Empty room** (20 s)
   > "Right now nobody is in the room. Expect: UNOCCUPIED, high confidence."
   Point at the state and the probability trace.

2. **Walk in** (15 s)
   > "I walk in. Expect OCCUPIED within two seconds."
   Say the number as it flips: *"one point four seconds."*

3. **Sit still, hands off the desk** (40 s) — this is the whole point
   > "Now I stop moving. This is where PIR loses me. The raw motion class drops,
   > but the still-presence class holds, so the state stays OCCUPIED."
   Do not talk over the trace; let them watch the probability stay up.

4. **Walk out, close the door** (20 s)
   > "I leave. Expect UNOCCUPIED after about ten seconds — deliberately slow,
   > so a person who pauses at the door does not switch the lights off."

Do not touch the keyboard during this. If state flips wrongly, **say it out loud**:
"That is a false clear, and it is the failure we are tracking" — do not hide it.

## 2:10–2:40 — The number

> "Twenty-four sessions, eight empty, eight still, eight walking, recorded the same
> way. We hold out whole sessions, never single seconds, so the test is honest.
> Presence recall is X, false-positive rate is Y, still-person recall is Z.
> Baseline logistic regression gets A; the small network gets B.
> Here is the command that reproduces it."

Show `results/LOSO-REPORT.md` — the table, then the command line at the bottom of
the file. One command, one JSON.

## 2:40–3:00 — What does not work yet

> "Three things are not done. Interference: a fan or a curtain still produces
> false alarms — we have the sessions and the table, the number is bad.
> Multi-person: not attempted. And this is one room, one device model.
> Next step is the interference set, not a bigger model."

Show `results/stress_metrics.json` even if it is ugly. An honest failure is worth
more marks than a hidden one.

---

## Questions you will be asked (prepare these answers)

| Question | Answer in one line |
| --- | --- |
| "Why not just PIR?" | PIR is motion-only; the brief explicitly requires still-person detection. |
| "Why not a camera?" | Privacy; the deployment target is bedrooms and hotel rooms. |
| "Isn't this just overfitting to your room?" | One room is the stated scope; sessions are held out whole, and the limitation is written down. |
| "What happens if two people?" | Not supported in v1; the label set has no multi-person class. |
| "How do you know 90 % recall isn't luck?" | 24 sessions, per-fold numbers in the JSON, fixed seed, rerun reproduces. |
| "Why the ten-second clear delay?" | Asymmetry is a product decision: a late clear wastes energy, a missed entry breaks the feature. |
| "What if the Wi-Fi is busy?" | Not measured yet — that is the external-interference case in the stress set. |

## Rules

1. Never show a number you cannot regenerate on the spot.
2. Never say "it works" without the metric name.
3. If something breaks, say what broke. Silence reads as not understanding.
