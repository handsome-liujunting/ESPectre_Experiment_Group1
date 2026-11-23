# Demo walkthrough — what to say

Six steps, about five minutes. Press `→` for the next step, `Space` to replay the
current capture. The capture loads itself when you change step.

Two rules for the whole demo:

1. **Never say a number that is not on the screen.** They are all there, with
   provenance, so there is nothing to gain by improvising one.
2. **When something fails, say it failed.** Step 4 is a deliberate failure. If you
   flinch there you look like you are hiding it; if you own it you look like
   someone who measured it.

---

## Step 1 — The mechanism

> "Wi-Fi already fills this room. Every packet that travels between two devices
> carries 64 measurements of how the channel distorted it — that is Channel State
> Information. A wall distorts it in a way that never changes. A person distorts it
> in a way that does. That is the entire sensing mechanism: we are not adding a
> sensor, we are reading one that was already there."

Point at the subcarrier axis. Say 64 subcarriers, 2.4 GHz, right now.

---

## Step 2 — An empty room

> "Ninety seconds, empty dorm room, nothing moving. Flat band. The detector decides
> UNOCCUPIED for all 81 windows where it commits to an answer, and gives up on 9."

Press Space. The playhead sweeps left to right.

> "This is the baseline. If we cannot do this, nothing else matters, because a
> system that says someone is home when they are not is worse than no system."

---

## Step 3 — Someone sitting still

> "Same room. A person seated, reading a phone, not moving. Every motion detector
> on the market fails right here — there is no motion to detect."

Press Space, let them watch.

> "Look at the texture, not the brightness. The striping shifts and separates over
> three seconds. That is a body changing the multipath. We detect 85 of 90 windows."

Pause. This is the result you are proud of. Let it land before you ruin it.

---

## Step 4 — Where it fails

> "And this is the same kind of capture — a person seated still in the same room —
> and we miss it completely. Zero of ninety. Fifty-two windows we confidently call
> empty, thirty-eight we refuse to answer."

**Do not apologise. Do not explain it away.** Then:

> "That is why our headline is 64 %, not 98 %. One seated capture in three does not
> look like the others from this feature set. We know which one fails. We have not
> yet fixed it. That is the honest state of the work."

If someone asks why: the honest answer is that the feature is the standard deviation
of amplitude over one-second bands. A person who is very still produces a signal that
is genuinely smaller than the noise floor of that statistic in this room. Fixing it
needs either longer observation windows or a different feature, and both are what
the next session is for.

---

## Step 5 — Someone moving

> "For contrast, walking. 59 of 60. This is the easy case — and it is exactly why
> our first campaign looked like 98 %. Most of that number was us detecting motion."

This step exists to explain why the first result was misleading, not to impress.

---

## Step 6 — Through the balcony door

> "One of the interference conditions the brief asks for: a person on the balcony,
> door closed, walking. Their signal leaks through. The frozen model rejects it —
> 81 windows, none falsely occupied."

Then go to the table below, and read it out:

> "That is the one condition we recorded. Three others — curtain, corridor, external
> Wi-Fi — have zero sessions. The fan condition we dropped, because our lab has no
> fan and we will not invent one. The project title says anti-interference; right now
> we have evidence for one of four conditions. That is a scope gap we are reporting
> rather than papering over."

---

## Numbers panel — for questions

If someone asks where a number comes from, scroll to **Where the numbers come from**.
It has the commit, the dataset hash, the seed, the library versions, and the fact
that the classifier is logistic regression over 16 features, not a neural network.

If someone challenges the headline: `results/v2/CSI-feature-comparison.csv` is
regenerable by `tools/v2_compare.py`, and the demo's own numbers are computed by the
same feature and hysteresis functions, imported from the repository.

If someone challenges the 98.3 %: the panel above it already shows 2 of 60 at the
classifier and 0 of 60 after hysteresis on the unseen capture. You do not have to
defend anything, you have to point.

---

## Failure drill

Rehearse these three, they are the ones that actually happen:

1. **The page does not open.** Open it from the directory you tested, not from a
   shortcut. If it still fails, `demo/` has both files — copy `index.html` and
   `demo-data.js` together anywhere and open `index.html` directly.
2. **The examiner wants live data.** Say plainly: "This runs on recorded captures so
   the numbers match the report. A live stream would show a number we have not
   measured." That is the correct trade, and it is defensible.
3. **Someone asks why you did not use the upstream ESPectre visualiser.** Answer:
   "Stationary presence is planned upstream for v3.3.0 and not shipped. The
   visualiser would show their motion detector, not our contribution."

---

## What NOT to claim

- Do not say "we detect people sitting still". Say "we detect 64 % of seated
  captures held out".
- Do not say "interference-resistant". Say "one of four interference conditions
  tested".
- Do not say "real-time". The pipeline is offline: a 90-second capture analysed in
  under a second, but not a live stream.
- Do not say "ML". It is logistic regression, 16 features, and that is a strength
  if you say it plainly: it is small, fast, and auditable.
