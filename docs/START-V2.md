# ESPectre occupancy pilot v2

**This is the headline result of the project.** Six `dorm-v2` sessions, LOSO:
30.7 % idle false positives (83/270) and 64.4 % seated recall (174/270). The
October pilot in `docs/PILOT-20261029.md` is superseded and must not be quoted
without this number.

Requires Python and NumPy for replay. Open PowerShell in the extracted folder.

```powershell
python -m pip install numpy
python tools/presence_v2.py replay --model results/v2/presence-v2.json --input data/dorm-v2/balcony-01-raw.npz
```

The CSV reports one decision per second. The values are OCCUPIED, UNOCCUPIED
and UNKNOWN. A balcony capture replay should report 9 initial UNKNOWN windows
and 81 UNOCCUPIED windows.

For another replay, select a raw capture from data/dorm-v2/. The six idle and seated
captures are training examples. They can demonstrate the interface and should
not be treated as independent acceptance data for the exported model.

The exploratory feature comparison used leave-one-session-out on three empty
and three seated recordings. The selected feature produced 83 false positive
windows out of 270 empty windows, and detected 174 of 270 seated windows.
The exported model was fitted to all six clean recordings. The two balcony
recordings were held out of fitting. Each produced 0 occupied, 81 unoccupied
and 9 unknown decisions. Fan, curtain, live transitions and fresh independent
room recordings remain unverified.

To regenerate the model, install scikit-learn in addition to NumPy, then run
`python tools/presence_v2.py train --help` for the three input arguments.
