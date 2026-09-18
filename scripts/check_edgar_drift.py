#!/usr/bin/env python3
"""Has the EDGAR mapping drifted? Re-measure it against the live archive.

@not-in-ci needs a network request to data.sec.gov and a contact address the
repository does not own. Run it by hand when the mapping looks old.

── WHAT IT ANSWERS ─────────────────────────────────────────────────────────

For every concept the mapping names, the last fiscal year each filer actually
reported it on a 10-K. That number, not mere presence, is what decides whether
a tag is worth trying: `Revenues` is present in Apple's company facts and has
not been used since FY2018, and code that takes the first tag it finds returns
a seven-year-old figure as current.

── WHY IT IS NOT A CI GATE ─────────────────────────────────────────────────

Three reasons, in order of weight. The SEC's fair-access policy wants a
User-Agent naming the caller with a contact address; an undeclared client is
answered with HTTP 403 and a page titled "Your Request Originates from an
Undeclared Automated Tool". Putting an address in a workflow file means
choosing whose, and this package has no business choosing. Second, a company
facts document for a large filer runs to tens of megabytes, and seven of them
on every push is a poor way to treat a public archive. Third, a gate that fails
because a filer changed a tag would block a change that has nothing to do with
it.

So the evidence file is committed and dated, `check_edgar_mapping.py` holds the
mapping against it on every push, and this script is how the evidence gets
refreshed.

── USING IT ────────────────────────────────────────────────────────────────

    export EDGAR_CONTACT="Your Name your@address"
    python3 scripts/check_edgar_drift.py            # report the drift
    python3 scripts/check_edgar_drift.py --write    # update the evidence

Without `--write` it changes nothing and prints what moved since the committed
measurement. The exit status is 1 when anything moved, so it can be run from a
scheduled job that is allowed to fail loudly.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
MAPPING = ROOT / "catalog" / "mappings" / "edgar.yaml"
ENDPOINT = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"

# The SEC asks for no more than ten requests a second. One every two seconds is
# far below that and still finishes seven filers in under a minute.
PAUSE_SECONDS = 2.0


def contact() -> str:
    value = os.environ.get("EDGAR_CONTACT", "").strip()
    if not value:
        raise SystemExit(
            "EDGAR_CONTACT is not set.\n\n"
            "The SEC's fair-access policy wants a User-Agent naming the caller and\n"
            "a way to reach them. Set it to something like\n\n"
            '    export EDGAR_CONTACT="Your Name your@address"\n\n'
            "This script will not invent one, and an undeclared request is answered\n"
            "with HTTP 403 rather than data."
        )
    return value


def fetch(cik: str, who: str) -> dict[str, Any]:
    request = urllib.request.Request(
        ENDPOINT.format(cik=cik),
        headers={
            "User-Agent": f"factorbase/0.1.0 ({who})",
            "Accept-Encoding": "gzip, deflate",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            raw = response.read()
    except urllib.error.HTTPError as error:
        raise SystemExit(
            f"CIK {cik}: HTTP {error.code}. "
            "403 usually means the User-Agent was not accepted; check EDGAR_CONTACT."
        ) from None
    if raw[:2] == b"\x1f\x8b":  # gzip, if urllib did not unwrap it
        import gzip

        raw = gzip.decompress(raw)
    return json.loads(raw)


def latest_annual(concept: dict[str, Any]) -> int | None:
    """The newest fiscal year this concept was reported on a 10-K.

    Only annual filings. A quarterly figure carries a different period and
    would make a tag look current when the annual statement stopped using it.
    """
    newest = 0
    for rows in concept.get("units", {}).values():
        for row in rows:
            if row.get("form") == "10-K" and isinstance(row.get("fy"), int):
                newest = max(newest, row["fy"])
    return newest or None


def measure(mapping: dict[str, Any], who: str) -> dict[str, Any]:
    wanted: dict[str, list[str]] = {
        entry["field"]: list(entry["concepts"]) + list(entry.get("historical", ()))
        for entry in mapping["fields"]
    }
    filers = {f["ticker"]: f["cik"] for f in mapping["filers_measured"]}

    facts: dict[str, dict[str, Any]] = {}
    for index, (ticker, cik) in enumerate(filers.items()):
        if index:
            time.sleep(PAUSE_SECONDS)
        print(f"  {ticker} ({cik}) ...", flush=True)
        document = fetch(cik, who)
        merged: dict[str, Any] = {}
        for taxonomy in ("us-gaap", "dei"):
            merged.update(document["facts"].get(taxonomy, {}))
        facts[ticker] = merged

    fields: dict[str, dict[str, list[dict[str, Any]]]] = {}
    for field, concepts in wanted.items():
        fields[field] = {}
        for ticker, merged in facts.items():
            rows = [
                {"tag": tag, "latest_annual_fy": latest_annual(merged[tag])}
                for tag in concepts
                if tag in merged
            ]
            fields[field][ticker] = rows
    return fields


def differences(old: dict[str, Any], new: dict[str, Any]) -> list[str]:
    moved: list[str] = []
    for field, per_filer in new.items():
        for ticker, rows in per_filer.items():
            before = {r["tag"]: r["latest_annual_fy"] for r in old.get(field, {}).get(ticker, [])}
            after = {r["tag"]: r["latest_annual_fy"] for r in rows}
            for tag in sorted(set(before) | set(after)):
                if before.get(tag, "absent") != after.get(tag, "absent"):
                    moved.append(
                        f"{field}/{ticker}/{tag}: "
                        f"{before.get(tag, 'absent')} -> {after.get(tag, 'absent')}"
                    )
    return moved


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="update the committed evidence file")
    arguments = parser.parse_args()

    mapping = yaml.safe_load(MAPPING.read_text(encoding="utf-8"))
    evidence_path = ROOT / mapping["evidence"]
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))

    who = contact()
    print(f"check_edgar_drift: {len(mapping['filers_measured'])} filer(s)")
    fresh = measure(mapping, who)

    moved = differences(evidence["fields"], fresh)
    print(
        f"\n  committed measurement: {evidence['measured_on']}; "
        f"{len(fresh)} field(s) re-measured, {len(moved)} difference(s)"
    )
    for line in moved:
        print(f"    {line}")

    if arguments.write:
        evidence["fields"] = fresh
        evidence["measured_on"] = time.strftime("%Y-%m-%d")
        evidence_path.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
        print(f"\n  wrote {evidence_path.relative_to(ROOT)}")
        print("  the mapping's own measured_on still needs updating by hand")
        return 0

    if moved:
        print("\n  Run again with --write to record this, then reread the notes:")
        print("  a tag that went stale usually means an entry's order is now wrong.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
