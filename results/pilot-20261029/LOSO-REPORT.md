# ESPectre pilot evaluation

Command: `python tools/loso_eval.py --data data --output results`

Dataset SHA-256: `c83d53134a3c44c40c847dcf421fc347d6b75ffcd8521f279a7eba0b931e1693`. Seed: 42.

| Evaluation | Sessions | Presence recall | Static recall | Idle false-positive rate | Presence F1 | Known-state coverage |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Pilot LOSO | 18 | 98.3% | 98.3% | 0.0% | 99.2% | 94.6% |
| Original catalogue holdout | 4 | 49.2% | 0.0% | 0.0% | 65.9% | 75.8% |

Recall and F1 count UNKNOWN on occupied windows as misses. Empty UNKNOWN
windows remain in the false-positive-rate denominator. Read coverage alongside FPR.

LOSO fits the scaler and logistic regression anew in each training fold. The
exported model fits the original training recordings and evaluates the original
holdout separately. The original exclusions remain excluded. State thresholds
stay fixed at the values specified in the PRD.

The approximately 60-second recordings are SHORT and support a pilot estimate.
Full-duration LOSO acceptance, capture-to-display latency, transition latency,
CPU and memory, and live hardware verification are pending.

These recordings describe one device, one dorm environment and one collection
date. Whole-capture splitting leaves time-of-day and collection-order effects intact.

## Interference stress with frozen model

| Condition | Available sessions | Sessions short of minimum | False-positive rate |
| --- | ---: | ---: | ---: |
| interference_fan | 0 | 2 | not measured |
| interference_curtain | 0 | 2 | not measured |
| interference_corridor | 0 | 2 | not measured |
| interference_wifi | 0 | 2 | not measured |

See loso_metrics.json for per-capture outcomes and confusion matrices.
