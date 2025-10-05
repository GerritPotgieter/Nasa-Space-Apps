"""Download the latest active satellite orbital elements from Celestrak
and store a structured JSON file (active.json) plus optional archival CSV.

Extended: also fetch TLE set for propagation and emit satellites_tle.json
(if --with-tle flag provided).

Source URLs:
    CSV: https://celestrak.org/NORAD/elements/gp.php?GROUP=active&FORMAT=csv
    TLE: https://celestrak.org/NORAD/elements/gp.php?GROUP=active&FORMAT=tle
"""

from __future__ import annotations
import csv, json, argparse, ssl, urllib.request, re
from pathlib import Path
from datetime import datetime, timezone

CELESTRAK_URL = "https://celestrak.org/NORAD/elements/gp.php?GROUP=active&FORMAT=csv"
CELESTRAK_TLE_URL = "https://celestrak.org/NORAD/elements/gp.php?GROUP=active&FORMAT=tle"
OUTPUT_JSON = "active.json"
OUTPUT_TLE_JSON = "satellites_tle.json"
DATA_DIR = Path("data")

# Columns per Celestrak GP CSV spec (subset we will keep)
# The CSV has many fields; we'll parse all then select a subset.
SELECT_FIELDS = [
    "OBJECT_NAME",
    "NORAD_CAT_ID",
    "OBJECT_TYPE",
    "RCS_SIZE",
    "COUNTRY_CODE",
    "LAUNCH_DATE",
    "EPOCH",
    "MEAN_MOTION",
    "ECCENTRICITY",
    "INCLINATION",
    "RA_OF_ASC_NODE",
    "ARG_OF_PERICENTER",
    "MEAN_ANOMALY",
    "SEMIMAJOR_AXIS",
    "PERIOD",
    "APOAPSIS",
    "PERIAPSIS",
    "DECAY_DATE",
]

TLE_LINE1_RE = re.compile(r"^1 (\d{5})")
TLE_LINE2_RE = re.compile(r"^2 (\d{5})")

def fetch_text(url: str) -> str:
    ctx = ssl.create_default_context()
    with urllib.request.urlopen(url, context=ctx, timeout=60) as resp:
        if resp.status != 200:
            raise RuntimeError(f"Failed to fetch data: HTTP {resp.status}")
        charset = resp.headers.get_content_charset() or "utf-8"
        return resp.read().decode(charset)

def parse_csv(csv_text: str):
    lines = csv_text.splitlines()
    reader = csv.DictReader(lines)
    return list(reader)

def transform(records: list[dict], limit: int | None = None):
    out = []
    for i, rec in enumerate(records):
        if limit is not None and i >= limit:
            break
        filtered = {k: rec.get(k) for k in SELECT_FIELDS}
        # Convert numeric fields where sensible
        numeric_keys = [
            "MEAN_MOTION","ECCENTRICITY","INCLINATION","RA_OF_ASC_NODE",
            "ARG_OF_PERICENTER","MEAN_ANOMALY","SEMIMAJOR_AXIS","PERIOD",
            "APOAPSIS","PERIAPSIS"
        ]
        for nk in numeric_keys:
            val = filtered.get(nk)
            if val in (None, ""):
                continue
            try:
                filtered[nk] = float(val)
            except ValueError:
                pass
        out.append(filtered)
    return out

def parse_tle_block(tle_text: str):
    """Parse concatenated TLE text (Name, L1, L2 repeating). Return list of dicts."""
    lines = [l.strip() for l in tle_text.splitlines() if l.strip()]
    out = []
    i = 0
    while i < len(lines) - 2:
        name = lines[i]
        l1 = lines[i+1]
        l2 = lines[i+2]
        if not (l1.startswith('1 ') and l2.startswith('2 ')):
            i += 1
            continue
        # Extract NORAD id from line 1/2 to double-check
        m1 = TLE_LINE1_RE.match(l1)
        m2 = TLE_LINE2_RE.match(l2)
        if not (m1 and m2 and m1.group(1) == m2.group(1)):
            i += 3
            continue
        norad_id = m1.group(1)
        out.append({
            "OBJECT_NAME": name,
            "NORAD_CAT_ID": norad_id,
            "TLE_LINE1": l1,
            "TLE_LINE2": l2,
        })
        i += 3
    return out

def write_json(records: list[dict], source_url: str, path: Path):
    meta = {
        "source": source_url,
        "fetched_utc": datetime.now(timezone.utc).isoformat(),
        "record_count": len(records),
        "fields": SELECT_FIELDS,
    }
    data = {"meta": meta, "satellites": records}
    path.write_text(json.dumps(data, indent=2))

def write_tle_json(merged: list[dict], path: Path):
    meta = {
        "source_csv": CELESTRAK_URL,
        "source_tle": CELESTRAK_TLE_URL,
        "fetched_utc": datetime.now(timezone.utc).isoformat(),
        "record_count": len(merged),
        "fields": SELECT_FIELDS + ["TLE_LINE1","TLE_LINE2"],
    }
    data = {"meta": meta, "satellites": merged}
    path.write_text(json.dumps(data, indent=2))

def maybe_archive(csv_text: str):
    DATA_DIR.mkdir(exist_ok=True)
    stamp = datetime.utcnow().strftime("%Y%m%d")
    archive_path = DATA_DIR / f"active-{stamp}.csv"
    if not archive_path.exists():
        archive_path.write_text(csv_text)
        return str(archive_path)
    return None

def main():
    parser = argparse.ArgumentParser(description="Update active satellite JSON from Celestrak")
    parser.add_argument("--no-archive", action="store_true", help="Do not save daily CSV archive copy")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of satellite records (testing)")
    parser.add_argument("--with-tle", action="store_true", help="Also fetch TLE set and produce satellites_tle.json")
    args = parser.parse_args()

    print("Fetching CSV ...", end="", flush=True)
    csv_text = fetch_text(CELESTRAK_URL)
    print(" done.")

    print("Parsing CSV ...", end="", flush=True)
    records = parse_csv(csv_text)
    print(f" {len(records)} rows.")

    print("Transforming records ...", end="", flush=True)
    transformed = transform(records, limit=args.limit)
    print(f" kept {len(transformed)}.")

    print("Writing JSON ...", end="", flush=True)
    write_json(transformed, CELESTRAK_URL, Path(OUTPUT_JSON))
    print(" done.")

    if args.with_tle:
        print("Fetching TLE ...", end="", flush=True)
        tle_text = fetch_text(CELESTRAK_TLE_URL)
        print(" done.")
        print("Parsing TLE ...", end="", flush=True)
        tle_records = parse_tle_block(tle_text)
        print(f" {len(tle_records)} TLE triplets.")
        # Merge on NORAD_CAT_ID
        tle_map = {r["NORAD_CAT_ID"]: r for r in tle_records}
        merged = []
        for rec in transformed:
            norad = str(rec.get("NORAD_CAT_ID"))
            t = tle_map.get(norad)
            if t:
                merged.append({**rec, "TLE_LINE1": t["TLE_LINE1"], "TLE_LINE2": t["TLE_LINE2"]})
        print(f"Merged {len(merged)} records with TLE.")
        print("Writing TLE JSON ...", end="", flush=True)
        write_tle_json(merged, Path(OUTPUT_TLE_JSON))
        print(" done.")

    if not args.no_archive:
        print("Archiving raw CSV ...", end="", flush=True)
        archived = maybe_archive(csv_text)
        if archived:
            print(f" saved {archived}")
        else:
            print(" already exists for today; skipped")

    print("Update complete.")

if __name__ == "__main__":
    main()
