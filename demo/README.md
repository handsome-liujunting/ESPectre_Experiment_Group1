# ESPectre demo — offline replay page

## What it is

One HTML file plus one data file, opened from disk. It replays eleven recorded
captures and shows what the detector did on each one. No board, no server, no
network call, no build step.

The page computes nothing. Every curve, count and number was produced in advance by
`build_demo_data.py` from the committed captures, so the page cannot show a result
that is not in the repository.

## Why an offline replay, not a live dashboard

- `tools/live_dashboard.py` was specified but never written (PRD FR-05, D-012).
- Upstream ESPectre's live tools need the board flashed and on the same network at
  the moment of the demo; in a lecture theatre that is the first thing to break.
- Upstream stationary presence is not shipped (its roadmap lists it as planned for
  v3.3.0), so a live page would demonstrate upstream's motion detector, not this
  project's contribution.
- The evidence is `results/`, produced from recorded sessions. A live demo would
  show a number that is not in any report.

## What it shows

Eleven captures, each scored held-out by a model that never saw that capture — the
same protocol as the headline.

| Step | Capture | What it demonstrates |
| --- | --- | --- |
| 1 | `idle-02` | 64 subcarriers of CSI amplitude; an empty room is a flat band |
| 2 | `idle-02` | an empty room reads `UNOCCUPIED`; the 83 false positives all come from `idle-01` |
| 3 | `static-presence-02` | a seated person detected, 85 of 90 windows |
| 4 | `static-presence-01` | the failure that produces 64.4 %: 0 of 90 |
| 5 | `pilot-motion` | walking is easy; 98.3 % on the pilot is motion-driven |
| 6 | `balcony-01` | through-door movement rejected: 0 occupied of 81 decided |

The pilot trap (98.3 % LOSO vs 2/60 classifier and 0/60 stable on the unseen seated
capture) and the interference gap table are on the same screen, so neither can be
quoted alone.

## Run it

Double-click `index.html`. Arrow keys walk the six-step script, space replays the
current capture, the sidebar jumps to any capture.

The replay animation is a fixed 2.6 s regardless of the capture's real duration.
It is a replay, not a real-time view.

## Rebuild the data file

From the repository root, with numpy and scikit-learn installed:

```bash
python demo/build_demo_data.py   # writes demo/demo-data.js
python demo/check_page.py        # static checks; prints OK
```

`build_demo_data.py` reads the captures from `data/`, the metrics from `results/`,
and imports `presence.py` / `presence_v2.py` from `tools/`. It does not reimplement
the features or the hysteresis, so the demo cannot drift away from the pipeline it
demonstrates.

## Files

```
demo/index.html          the page — open this
demo/demo-data.js        1.6 MB of capture data and results
demo/build_demo_data.py  regenerates demo-data.js
demo/check_page.py       consistency checks (ids, counts, headline attribution)
demo/WALKTHROUGH.md      what to say, in order
```
