# AGENTS.md

Guidance for AI assistants (and humans) working in this repository.

## What this project is

ESPectre: detect whether a room is occupied from Wi-Fi CSI, including when the
person is **not moving**, and reject fan / curtain / through-wall / external-Wi-Fi
interference. One room, one ESP32-C6, one laptop. Course: 1105 Project-Based Course.
Mentor: 龚政 (Huawei 2012 Wireless Lab).

Read first: `docs/PRD-ESpectre-MVP-v1.0.md`, then `docs/TechDesign-ESpectre-MVP-v1.0.md`.

## Repo map

```
docs/        proposal, PRD, tech design, demo script, data plan, decision log
tools/       our own pipeline (validate_sessions.py is the only real script today)
data/        sessions: <label>/<session>.npz + .json, plus manifest.csv
results/     generated metrics + reports (never hand-edited)
```

## Commands

```bash
pip install -r requirements.txt
python tools/validate_sessions.py --data data --manifest data/manifest.csv
```

`tools/loso_eval.py`, `tools/capture_session.py` and `tools/live_dashboard.py` are
**specified but not written yet**. Do not reference them as if they exist.

## Rules that are not negotiable

1. **No random window splits.** Splitting windows instead of sessions leaks and
   invalidates every number. Leave-one-session-out, always.
2. **No invented data.** No made-up interviews, market numbers, accuracy figures or
   timings. If it was not measured, the text says "not measured".
3. **No fabricated results in `results/`.** Every file there is produced by a
   command recorded in the file itself.
4. **Stable IDs.** FR-01…FR-08 never get renumbered. Removed ⇒ mark `dropped`.
5. **Documents in English**, because the assessment guidelines are English. Chat
   with the team can be Chinese.
6. **Scope discipline.** If a feature is not in PRD §3 "In scope", it does not go
   into the MVP without a PRD change and a note in the decision log.
7. **Do not add a dependency** to solve a problem a 20-line function solves.

## Traps in this repo

| Trap | What happens | Do this instead |
| --- | --- | --- |
| `code/train_ml_model.py` from upstream ESPectre | Imports `tools.lib.*`, which does not exist here; fails instantly | Reference only. Write minimal training code in `tools/` |
| Duplicated `README.md` at root and in the nested `ESPectre_Experiment_Group1/` folder | Two sources of truth that drift | Keep one root README; delete the inner duplicate, do not sync it |
| Old metrics: CV F1 76.3 % vs deployment gate FAIL | Numbers came from a different split and a different gate | Do not quote them as current results; rerun LOSO and cite the JSON |
| Windows console + Chinese output | `UnicodeEncodeError` on redirected stdout | Scripts write ASCII to stdout; UTF-8 only to files |
| `.npz` label stored per frame | Mixed labels inside one session | Reject mixed-label sessions in the validator |

## Done means

A task is done when **all** of these hold:

- [ ] The command that produces the artefact is written down and was actually run.
- [ ] The artefact exists in the repo and its content matches the claim.
- [ ] `docs/traceability.md` says `implemented` or `changed`, with the file path.
- [ ] If a number is claimed, it names the data hash and the seed.
- [ ] If something does not work, the limitation is written where the reader will
      see it — not only in the commit message.

## Style

- Python: standard library + numpy/sklearn only, `argparse`, no frameworks.
- Markdown: one claim per line, tables over prose for comparisons, no emoji in
  submitted documents.
- Commit messages: `area: what changed and why`, e.g. `tools: add LOSO evaluator`.
