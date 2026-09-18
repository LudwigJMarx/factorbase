#!/usr/bin/env python3
"""Check the metadata this package would actually upload with.

── WHY THIS EXISTS ─────────────────────────────────────────────────────────

On 18 September 2026 this project carried `license = "MIT"` as an SPDX
expression and the classifier `License :: OSI Approved :: MIT License` at the
same time. PEP 639 rules the two out together and PyPI rejects the combination
on upload.

Three things that were supposed to catch it did not:

- hatchling wrote both into the wheel without complaint.
- `twine check` passed both artifacts, before and after the fix.
- the test suite has nothing to say about packaging.

It surfaced only because a sibling project builds with setuptools 77, which
refuses outright and names the offending line. That is not a check, that is
luck, and luck does not run on every push.

── WHAT THIS LOOKS AT ──────────────────────────────────────────────────────

The METADATA file inside a freshly built wheel, not `pyproject.toml`. The
source states an intention; the metadata is what the index receives, and the
backend sits between the two. Checking the source would confirm that a string
exists, which is a different claim.

── WHAT IT DOES NOT COVER ──────────────────────────────────────────────────

It is not a substitute for `twine check`, which validates the long description
renders and the artifacts are well formed. It covers the rules twine has
nothing to say about. Both belong in CI.

It does not talk to PyPI. A name being free, a version being unused and the
account being allowed to upload are all questions this cannot answer.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
import zipfile
from dataclasses import dataclass
from email.parser import Parser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Finding:
    rule: str
    detail: str

    def __str__(self) -> str:
        return f"{self.rule}: {self.detail}"


def findings(metadata: str) -> list[Finding]:
    """Rules applied to one METADATA document.

    Separated from building so it can be exercised against documents that no
    backend here would produce. A checker whose logic only runs against a
    correct input has never been shown to fail.
    """
    parsed = Parser().parsestr(metadata)
    found: list[Finding] = []

    expression = parsed.get("License-Expression")
    license_classifiers = [
        value for value in parsed.get_all("Classifier", []) if value.startswith("License ::")
    ]

    if expression and license_classifiers:
        found.append(
            Finding(
                "PEP 639",
                f"License-Expression ({expression}) cannot be combined with "
                f"{len(license_classifiers)} license classifier(s): "
                f"{', '.join(license_classifiers)}. PyPI rejects this on upload",
            )
        )

    if not expression and not license_classifiers and not parsed.get("License"):
        found.append(Finding("licence", "the metadata states no licence at all, in any form"))

    if not parsed.get_payload().strip():
        found.append(
            Finding(
                "long description",
                "the metadata carries no long description, so the project page "
                "on PyPI would be empty. Set `readme` in pyproject",
            )
        )

    if not parsed.get("Summary"):
        found.append(Finding("summary", "the metadata carries no Summary"))

    return found


def build_wheel(into: Path) -> Path:
    """Build a wheel and return its path, failing loudly if the build fails."""
    result = subprocess.run(
        [sys.executable, "-m", "build", "--wheel", "--outdir", str(into)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        tail = "\n".join((result.stdout + result.stderr).strip().splitlines()[-12:])
        raise SystemExit(f"check_metadata: the wheel did not build:\n{tail}")

    wheels = sorted(into.glob("*.whl"))
    if len(wheels) != 1:
        raise SystemExit(
            f"check_metadata: expected exactly one wheel in {into}, found {len(wheels)}"
        )
    return wheels[0]


def metadata_of(wheel: Path) -> str:
    with zipfile.ZipFile(wheel) as archive:
        names = [n for n in archive.namelist() if n.endswith(".dist-info/METADATA")]
        if len(names) != 1:
            raise SystemExit(
                f"check_metadata: expected one METADATA in {wheel.name}, found {len(names)}"
            )
        return archive.read(names[0]).decode()


def main() -> int:
    with tempfile.TemporaryDirectory() as workspace:
        wheel = build_wheel(Path(workspace))
        metadata = metadata_of(wheel)
        problems = findings(metadata)

        parsed = Parser().parsestr(metadata)
        classifiers = len(parsed.get_all("Classifier", []))
        version = parsed.get("Metadata-Version", "?")

        # Say what was looked at. "0 problems" from a checker that examined
        # nothing reads the same as "0 problems" from one that examined
        # everything.
        print(
            f"check_metadata: {wheel.name}, Metadata-Version {version}, "
            f"{classifiers} classifier(s), {len(problems)} finding(s)"
        )
        for problem in problems:
            print(f"  {problem}")

    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
