#!/usr/bin/env python3
"""Self-test for check_version_against_tag.py.

A gate that always returns 0 is indistinguishable from a satisfied gate, so
most of what is checked here is that it can refuse at all.
"""

from __future__ import annotations

import importlib.util
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    "check_version_against_tag", HERE / "check_version_against_tag.py"
)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def tree(version: str | None) -> Path:
    folder = Path(tempfile.mkdtemp())
    if version is not None:
        (folder / "pyproject.toml").write_text(
            f'[project]\nname = "x"\nversion = "{version}"\n', encoding="utf-8"
        )
    return folder


def main() -> int:
    cases: list[tuple[str, str, str | None, int]] = [
        ("equal", "v0.1.1", "0.1.1", 0),
        ("tag ahead", "v0.2.0", "0.1.1", 1),
        ("package ahead", "v0.1.1", "0.2.0", 1),
        ("no v", "0.1.1", "0.1.1", 2),
        ("only v", "v", "0.1.1", 2),
        ("no pyproject.toml", "v0.1.1", None, 2),
    ]
    failures = 0
    for name, tag, version, expected in cases:
        code, message = module.compare(tag, tree(version))
        if code != expected:
            print(f"MISSED: {name}: exit {code}, expected {expected} ({message})")
            failures += 1

    # Counter-check against the real tree: its own version has to pass.
    root = HERE.parent
    own = module.version_in_package(root)
    code, _ = module.compare(f"v{own}", root)
    if code != 0:
        print(f"MISSED: the real tree is rejected for v{own}")
        failures += 1

    print(f"check_version_against_tag: {len(cases) + 1} cases, {failures} failed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
