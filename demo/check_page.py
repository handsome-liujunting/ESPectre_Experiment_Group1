"""Static checks on the demo page: nothing may reference something that is not there."""

import base64
import json
import pathlib
import re

OUT = pathlib.Path(__file__).resolve().parent
html = (OUT / "index.html").read_text(encoding="utf-8")
data = (OUT / "demo-data.js").read_text(encoding="utf-8")

problems = []

# 1. the data file must define the global the page reads
if not data.startswith("window.DEMO = "):
    problems.append("demo-data.js does not define window.DEMO")

payload = json.loads(data[len("window.DEMO = "):].rstrip().rstrip(";"))
print("payload keys      :", list(payload))
print("sessions          :", len(payload["sessions"]))
print("data file size    : %.1f KB" % (len(data.encode()) / 1024))

# 2. every id the script reaches for must exist in the markup
ids_in_html = set(re.findall(r'\bid="([A-Za-z0-9_-]+)"', html))
ids_in_js = set(re.findall(r'\$\("([A-Za-z0-9_-]+)"\)', html))
missing = sorted(ids_in_js - ids_in_html)
print("ids in markup     :", len(ids_in_html))
print("ids used by script:", len(ids_in_js))
if missing:
    problems.append("script references missing ids: %s" % missing)

unused = sorted(ids_in_html - ids_in_js)
if unused:
    print("ids with no script:", unused)

# 3. sessions named in the guided script must exist in the data
script_ids = re.findall(r'session:\s*"([^"]+)"', html)
known = {s["id"] for s in payload["sessions"]}
for sid in script_ids:
    if sid not in known:
        problems.append("script step points at unknown session %r" % sid)
print("script steps      :", len(script_ids), script_ids)

# 4. no leftover placeholder
for token in ("X/Y/Z", "A/B/C", "TODO", "undefined%", "TBD"):
    if token in html:
        problems.append("placeholder left in page: %r" % token)

# 5. stress keys the page expects must exist in the metrics
stress = payload["results"]["pilot"]["stress"]
print("stress keys       :", list(stress))
expected = {"interference_balcony", "interference_curtain",
            "interference_fan", "interference_corridor", "interference_wifi"}
absent = expected - set(stress)
if absent:
    print("stress rows absent:", sorted(absent))

# 6. every session must carry the arrays the page draws
for s in payload["sessions"]:
    if len(s["score"]) != s["windows"]:
        problems.append("%s: score length %d != windows %d"
                        % (s["id"], len(s["score"]), s["windows"]))
    if len(s["stable"]) != s["windows"]:
        problems.append("%s: stable length mismatch" % s["id"])
    if s["heat"]["w"] != 64:
        problems.append("%s: heat width %d" % (s["id"], s["heat"]["w"]))
    raw = base64.b64decode(s["heat"]["b64"])
    if len(raw) != s["heat"]["w"] * s["heat"]["h"]:
        problems.append("%s: heat payload %d bytes, expected %d"
                        % (s["id"], len(raw), s["heat"]["w"] * s["heat"]["h"]))
    if not set(s["stable"]) <= {"OCCUPIED", "UNOCCUPIED", "UNKNOWN"}:
        problems.append("%s: unknown state name" % s["id"])

# 7. the headline in the page must equal the published figure
v2 = payload["results"]["v2"]
print("headline          : %s / %s" % (v2["idle_false_positives"], v2["seated_detected"]))
if v2["idle_false_positive_rate_pct"] != 30.7:
    problems.append("headline FPR drifted")

# 8. the headline must be traceable to whole sessions, not a hand-picked slice
empty = [s for s in payload["sessions"] if s["label"] == "empty" and s["source"] == "dorm-v2"]
seated = [s for s in payload["sessions"] if s["label"] == "seated" and s["source"] == "dorm-v2"]
empty_occ = sum(s["counts"]["occupied"] for s in empty)
seated_occ = sum(s["counts"]["occupied"] for s in seated)
idle01 = next(s for s in empty if s["id"] == "idle-01")
if empty_occ != 83 or seated_occ != 174:
    problems.append("headline counts do not match session totals: %d / %d"
                    % (empty_occ, seated_occ))
if idle01["counts"]["occupied"] != empty_occ:
    problems.append("headline FPR is not entirely from idle-01")

# 9. the pilot sidebar must be the official held-out split, not manifest[0]
pilot = {s["id"]: s for s in payload["sessions"] if s["source"] == "pilot-20261029"}
want = {"pilot-idle": (0, 51, 9), "pilot-static_presence": (0, 21, 39),
        "pilot-motion": (59, 0, 1)}
for sid, (occ, unocc, unk) in want.items():
    got = pilot.get(sid)
    if not got:
        problems.append("missing pilot session %s" % sid)
        continue
    counts = got["counts"]
    if (counts["occupied"], counts["unoccupied"], counts["unknown"]) != (occ, unocc, unk):
        problems.append("%s counts %s != %s" % (sid, counts, (occ, unocc, unk)))
holdout = payload["results"]["pilot"].get("holdout_ids", {})
if holdout != {
        "idle": "idle_c6_64sc_dev9678a7495e996c21_20261029_201857_712677_0001",
        "static_presence": "static_presence_c6_64sc_dev9678a7495e996c21_20261029_193029_284115_0001",
        "motion": "motion_c6_64sc_dev9678a7495e996c21_20261029_194501_786240_0001"}:
    problems.append("pilot holdout ids drifted: %s" % holdout)

# 10. the stress table must use the newest (v2 balcony) replay, not the stale pilot block
balcony = payload["results"]["pilot"]["stress"]["interference_balcony"]
if balcony["sessions"] != 2 or balcony["decided_windows"] != 162:
    problems.append("balcony stress row is stale: %s" % balcony)
if balcony["false_positive_rate"] != 0.0:
    problems.append("balcony false-positive rate drifted")
for key in ("interference_fan", "interference_curtain",
            "interference_corridor", "interference_wifi"):
    if payload["results"]["pilot"]["stress"][key]["sessions"] != 0:
        problems.append("%s claims sessions but none were recorded" % key)

print()
if problems:
    print("PROBLEMS")
    for p in problems:
        print("  -", p)
else:
    print("OK: no problems found")
