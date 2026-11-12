# MEMORY.md — project facts worth not re-deriving

Keep this short. Facts only, with the thing that proves them.

## Project
- Course 1105, project #4 "Wi-Fi 设备存在检测抗干扰", Huawei 2012 Wireless Lab, mentor 龚政.
- Brief constraints: no hardware modification, low measurement rate, still-person
  detection, three interference classes, multi-link fusion, deliver dataset +
  prototype + evaluation report.
- MVP scope: one room, one ESP32-C6, one laptop, 3 classes → binary occupancy.

## Data
- 24 pilot sessions on a **separate machine**: 8 `idle`, 8 `static_presence`,
  8 `motion`. Not yet in this repo.
- Pilot format: `.npz` with `csi_data` (float, frames × subcarriers) and `label`.
- Rate ~10 packets/s; pilot files ≈ 600 packets (≈ 60 s). New target 300 s.
- Pilot totals: 4803 packets across files.
- Contract: `docs/TechDesign-ESpectre-MVP-v1.0.md` §3; validated by
  `tools/validate_sessions.py`.

## Numbers from the earlier experiment (historical, not current results)
- MLP 8-24-12-1, 8 subband features, `log1p_standard`, FP weight 1.75.
- 3-fold grouped CV: F1 76.3 %, recall 66.7 %, precision 89.6 %, FP 16.7 %.
- Deployment gates: paired recall 79.70 % / FP 8.59 % → FAIL;
  occupancy 70 % → recall 0.00 % → FAIL. No model exported.
- Why it is not quotable: different split, different gate definitions, no LOSO.

## Decisions
- LOSO instead of random splits — see `docs/ai-decision-log.md` D-001.
- Interference is a stress table, not part of the headline metric — D-004.
- Documents in English, chat in Chinese — D-006.

## Environment
- Windows 11, workspace `C:\Users\silve\Desktop\DeepSeek工作区`.
- Recording laptop is a different machine; data must be exported by hand.
- Console encoding bites on Chinese output; scripts keep stdout ASCII.

## Open
- Deadline and team split unconfirmed.
- 0 / 3 interviews done.
- No interference sessions recorded yet.
