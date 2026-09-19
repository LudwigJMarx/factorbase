#!/usr/bin/env python3
"""Check that the tag and the version in the package say the same thing.

── WHY THIS EXISTS ─────────────────────────────────────────────────────────

Both numbers are set by hand, in two places, at two times. When they drift
apart nothing notices: the build builds whatever `pyproject.toml` says, `twine
check` checks the file and not its name, and PyPI accepts any version it does
not already know. The tag reads v0.2.0, 0.1.1 lands, and every gate is green.

This is the same defect class the catalogue is built to refuse elsewhere: two
statements about one thing, and nowhere that holds them against each other.

── WHAT COUNTS AS A MATCH ──────────────────────────────────────────────────

The tag is `v` followed by exactly the version string. No normalisation, no
prefix stripping beyond the `v`: a tag that needs interpreting is a tag that
will be interpreted differently by the next reader.

Usage:  python3 scripts/check_version_against_tag.py v0.1.1 [--root PATH]
"""

from __future__ import annotations

import argparse
import sys
import tomllib
from pathlib import Path


def version_in_package(root: Path) -> str:
    with (root / "pyproject.toml").open("rb") as handle:
        return str(tomllib.load(handle)["project"]["version"])


def compare(tag: str, root: Path) -> tuple[int, str]:
    """Return (exit code, message). No printing, so the test can read it."""
    if not tag.startswith("v"):
        return 2, f"tag {tag!r} does not start with 'v'; expected v<version>"
    from_tag = tag[1:]
    if not from_tag:
        return 2, "tag is just 'v', there is no version in it"
    try:
        from_package = version_in_package(root)
    except (OSError, KeyError, tomllib.TOMLDecodeError) as error:
        # Fail loudly. A read problem here otherwise looks like a match.
        return 2, f"cannot read the version from {root / 'pyproject.toml'}: {error}"
    if from_tag != from_package:
        return 1, (
            f"tag says {from_tag}, pyproject.toml says {from_package}. "
            "The version from pyproject.toml would be uploaded, under the tag's name"
        )
    return 0, f"tag and package both say {from_package}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tag", help="the tag being published, e.g. v0.1.1")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    arguments = parser.parse_args(argv)
    code, message = compare(arguments.tag, arguments.root)
    print(message, file=sys.stderr if code else sys.stdout)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
