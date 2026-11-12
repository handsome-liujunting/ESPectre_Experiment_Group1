# Data Collection Plan — for the measurement laptop

This is the procedure to run on the machine that has the ESP32-C6 and the 24 pilot
sessions. Do the steps in order. If a step fails, stop and report the exact error
line — do not work around it silently.

---

## 0. What already exists

24 pilot sessions on that laptop: 8 `idle`, 8 `static_presence`, 8 `motion`,
10 packets/s, ~300 s each, one room, one device. **Do not re-record them.** Export
and validate first; only re-record a session that `validate_sessions.py` marks
`FAIL` for a reason you can fix (e.g. a packet gap).

Current estimate of file counts: ~600 packets per file at 10 pps ≈ 60 s. If the
validation report shows sessions of 60 s rather than 300 s, note it in the report —
300 s is the target for *new* sessions, not a reason to discard old ones.

## 1. Export the 24 sessions

1. Copy the 24 `.npz` files into the layout below (one folder per label). Keep the
   original names in the `notes` field if they do not follow the convention.
2. For each `.npz`, create the sidecar `.json` (template in §3). Fill it from the
   recording notebook, not from memory.
3. Copy the folder `tools/` from this repo onto that laptop, run the validator, and
   paste the full output back.

```
data/
  idle/               idle_labA_c6-01_20261028-1015.npz + .json
  static_presence/    static_presence_labA_c6-01_20261028-1030.npz + .json
  motion/             motion_labA_c6-01_20261028-1045.npz + .json
```

> If the original files are named `data_1.npz` … `data_8.npz`, rename them with the
> convention above **and** keep the old name inside `notes`. Renaming without a
> record breaks traceability.

## 2. Run the validator

```bash
pip install numpy
python tools/validate_sessions.py --data data --manifest data/manifest.csv
```

Send back, verbatim:

- the whole stdout table,
- `data/manifest.csv`,
- the exit code (`echo %ERRORLEVEL%` on Windows).

A session is usable only if it shows `PASS`. `DEGRADED` means usable but excluded
from the headline number. `FAIL` means re-record (§4).

## 3. Session metadata template

```json
{
  "session_id": "static_presence_labA_c6-01_20261112-1030",
  "label": "static_presence",
  "room": "labA",
  "device": "c6-01",
  "chip": "ESP32-C6",
  "rate_pps": 10.0,
  "duration_s": 300.0,
  "packets": 3000,
  "person": {"count": 1, "activity": "seated, typing, no arm movement"},
  "interference": [],
  "notes": "door closed, fan off, AC on low",
  "recorded_by": "name"
}
```

Rules: `label` must equal the folder name. `person.count` is `0` for `idle`.
`interference` lists what was running (`["ceiling_fan:low"]`), empty for clean
sessions. Any condition you would have to guess at later belongs in `notes`.

## 4. New sessions to record (in this order of value)

Each session: **300 s**, one label, one condition, same room, same device position.
Do not move the boards between sessions unless you write it in `notes`.

| # | Label | Condition | Why |
| --- | --- | --- | --- |
| 1–3 | `idle` | empty room, 3 different times of day | baseline drift |
| 4–6 | `static_presence` | seated still, phone reading, 3 times | the core claim |
| 7–9 | `motion` | walking in/out, page turning, chair shifting | the easy class |
| 10–11 | `interference_fan` | room empty, fan on low / high | false-alarm source |
| 12–13 | `interference_curtain` | room empty, curtain moving in draught | false-alarm source |
| 14–15 | `interference_corridor` | room empty, someone walks outside the door | through-wall rejection |
| 16–17 | `interference_wifi` | room empty, second AP / large download nearby | external RF |
| 18 | `static_presence` | person still **and** fan on | the hardest realistic case |

**Minimum for a usable stress table:** 2 sessions per interference class.
**Do not** add a `pet` or `robot vacuum` session unless one is actually available —
an unlabelled "pet" clip is worse than no clip.

## 5. Before / during / after checklist

**Before**
- [ ] Boards powered, associated, same firmware version (write it down).
- [ ] Packet rate ≥ 8 pps for 60 s before you start recording.
- [ ] Room in the documented state (door, window, fan, AC).
- [ ] Filename and sidecar JSON prepared *before* recording.

**During**
- [ ] Do not touch the laptop or the boards.
- [ ] Do not walk past the boards to "check" — that becomes a motion sample.
- [ ] For `static_presence`, the person must be in the room the whole time and must
      not leave for water. A 20 s absence silently labels an empty room as occupied.
- [ ] Note the wall-clock start time.

**After**
- [ ] Run the validator on the new file immediately.
- [ ] Fix the label now, not next week.

## 6. When a session is `FAIL`

| Reason | Action |
| --- | --- |
| `missing csi_data` | wrong file / wrong export — re-export, do not rename keys |
| `packets < 1000` | too short or capture died — re-record |
| `gap > 2 s` | Wi-Fi dropped — re-record, note the interference |
| `label mismatch` | fix the sidecar to match the folder, or move the file |
| `nan/inf in csi_data` | corrupt capture — re-record |

## 7. What to send back

One zip: `data/` (npz + json, no raw pcap), `data/manifest.csv`, validator stdout,
and a one-page note listing anything you changed, moved or guessed.

Then, and only then, we run the baseline. Numbers produced before the manifest is
clean are numbers we will have to throw away.
