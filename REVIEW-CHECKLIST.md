# Review checklist — before every push

Two minutes of checking beats an hour of explaining to the mentor.

## Claims
- [ ] Every number in `docs/` has a file in `results/` behind it.
- [ ] Every `results/` file names the command that produced it.
- [ ] No sentence says "works", "accurate", "real-time" without the metric name.
- [ ] Anything not measured is written as **not measured**, not estimated.
- [ ] No invented interview, market figure or user quote.

## Scope
- [ ] No feature outside PRD §3 "In scope" crept in.
- [ ] Anything cut is listed in PRD §3 "Out of scope" with a reason.
- [ ] `docs/traceability.md` status matches reality (`not started` is fine).

## Data
- [ ] `python tools/validate_sessions.py --data data` exits 0, or the failures are
      explained in the PR description.
- [ ] `data/manifest.csv` is regenerated and committed with the data it describes.
- [ ] No personal data, no MAC addresses of other people's devices, no camera frames.
- [ ] File names follow `<label>_<room>_<device>_<timestamp>`.

## Reproducibility
- [ ] Fresh clone + `pip install -r requirements.txt` + documented command works.
- [ ] Fixed seed; two runs produce identical `results/*.json`.
- [ ] No absolute local paths (`C:\Users\...`) in docs or scripts.

## Docs
- [ ] One root `README.md`; no duplicated copy in a nested folder.
- [ ] Links resolve (click them).
- [ ] English, no emoji, no placeholder like `[fill]` left in a submitted section.
- [ ] Page counts within the guideline: proposal 1–2, PRD 3–5, design 2–3.

## Git
- [ ] Commit message says what and why.
- [ ] No `__pycache__`, `.ipynb_checkpoints`, model blobs, or zip files committed.
- [ ] `.gitignore` covers the above.

## Demo (only when a demo is due)
- [ ] Ran it twice end to end on the demo laptop.
- [ ] Fallback recording exists and is one click away.
- [ ] Can answer the seven questions in `docs/DEMO-SCRIPT.md`.
