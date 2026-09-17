#!/usr/bin/env python3
"""Render the catalogue into a SQLite file.

Not a checker by the naming convention, so check_gates_wired.py does not track
it, and it carries no exemption marker: the workflow does call it, as a build
step rather than as a gate.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from factorbase.catalog import load_catalog  # noqa: E402
from factorbase.db import build  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--out", type=Path, default=ROOT / "factorbase.sqlite3", help="where to write the file"
    )
    parser.add_argument(
        "--catalog", type=Path, default=ROOT / "catalog", help="which catalogue to read"
    )
    arguments = parser.parse_args()

    catalog = load_catalog(arguments.catalog)
    written = build(arguments.out, catalog)

    size = arguments.out.stat().st_size
    print(f"build_db: wrote {arguments.out} ({size:,} bytes) from {len(catalog.sources)} file(s)")
    for table, count in written.items():
        print(f"  {table:<14} {count:>5}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
