# MEMORY.md — project facts worth not re-deriving

Keep this short. Facts only, with the thing that proves them.

## Project
- Course 1105, project #4 "Wi-Fi 设备存在检测抗干扰", Huawei 2012 Wireless Lab, mentor 龚政.
- Brief constraints: no hardware modification, low measurement rate, still-person
  detection, three interference classes, multi-link fusion, deliver dataset +
  prototype + evaluation report.
- MVP scope: one room, one ESP32-C6, one laptop, 3 classes → binary occupancy.

## Data (all in this repo)
- `data/pilot-20261029/`: 24 sessions, 60 s, 8 idle / 8 static / 8 motion.
  Source roles: 18 train, 4 holdout, 2 exclude.
- `data/dorm-v2/`: 8 sessions, 90 s, 3 idle / 3 static / 2 balcony (through-door).
  Layout `<label>-NN-raw.npz` + `.json`; read by `tools/presence_v2.py`.
- Both sets: 64 amplitude columns, `timestamps`, 10.02 pps after decimation,
  channel 11, RSSI about -32 dBm.
- Validator: PASS at 500 packets (pilot floor), `SHORT` below that and against the
  300 s / 3000-packet acceptance target. Every capture here passes the floor and
  fails the target, so no number here is acceptance evidence.

## Current numbers (these are the ones to quote)
- v2 LOSO on the six `dorm-v2` clean sessions: **30.7 % idle false positives
  (83/270), 64.4 % seated recall (174/270)**.
- v2 frozen model on the two balcony sessions: 0 occupied, 81 unoccupied, 9 unknown
  per session.
- Everything else in `results/pilot-20261029/` is pilot-grade.

## Numbers from the earlier experiment (historical, not current results)
- MLP 8-24-12-1, 8 subband features, `log1p_standard`, FP weight 1.75.
- 3-fold grouped CV: F1 76.3 %, recall 66.7 %, precision 89.6 %, FP 16.7 %.
- Deployment gates: paired recall 79.70 % / FP 8.59 % → FAIL;
  occupancy 70 % → recall 0.00 % → FAIL. No model exported.
- Why it is not quotable: different split, different gate definitions, no LOSO.

## Trap worth remembering
- Pilot LOSO reports 98.3 % static recall at 0 % FP. It is **not** generalisation:
  18 folds, one evening, one room, identical state sequences, zero flips. The one
  independent seated session scored 3.3 %. Never quote 98.3 % without 3.3 %.

## Decisions
- LOSO instead of random splits — `docs/ai-decision-log.md` D-001.
- Interference is a stress table, not part of the headline metric — D-004.
- Documents in English, chat in Chinese — D-006.
- v2 result is the headline, pilot result is historical — 2026-11-17.

## Environment
- Windows 11, workspace `C:\Users\silve\Desktop\DeepSeek工作区`.
- Recording laptop is a different machine.
- Console encoding bites on Chinese output; scripts keep stdout ASCII.

## Open
- Deadline and team split unconfirmed.
- 0 / 3 interviews done.
- Fan condition dropped (no fan available); curtain and external Wi-Fi never recorded.
- `results/pilot-20261029/loso_metrics.json` predates `source_commit` in
  `loso_eval.py`; one rerun fixes it. Do not hand-edit the JSON.
