#!/usr/bin/env python3
"""Tests for check_metadata.py.

── WHY THE SECOND HALF ─────────────────────────────────────────────────────

The first block drives `findings` with METADATA documents written by hand. It
covers the rules, and it would keep passing if `metadata_of` read the wrong
file out of the wheel, or if `build_wheel` handed back a stale artifact. The
rules would be right and the input wrong, and no test could fail. That is the
ifc-lite #4900 shape.

So the second block goes through the seam: it assembles a wheel-shaped zip on
disk and reads it back with the real `metadata_of`, and it runs the script
itself against this repository.

Usage:  python3 scripts/check_metadata.test.py
        (not through `-m unittest`: this file is not importable as a module name)
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("check_metadata", HERE / "check_metadata.py")
assert SPEC and SPEC.loader
check_metadata = importlib.util.module_from_spec(SPEC)
# Registered before executing: a dataclass resolves its field types through
# sys.modules, and loading this way without the entry fails inside
# dataclasses rather than anywhere that names the cause.
sys.modules["check_metadata"] = check_metadata
SPEC.loader.exec_module(check_metadata)


def document(*headers: str, body: str = "A long description.\n") -> str:
    return "\n".join(headers) + "\n\n" + body


CLEAN = (
    "Metadata-Version: 2.5",
    "Name: factorbase",
    "Version: 0.1.0",
    "Summary: A catalogue of screening factors",
    "License-Expression: MIT",
    "Classifier: Development Status :: 3 - Alpha",
)


class Rules(unittest.TestCase):
    def rules_hit(self, text: str) -> set[str]:
        return {f.rule for f in check_metadata.findings(text)}

    def test_a_clean_document_produces_nothing(self):
        self.assertEqual(self.rules_hit(document(*CLEAN)), set())

    def test_the_incident_is_caught(self):
        # Exactly what this repository shipped on 18 September 2026.
        text = document(*CLEAN, "Classifier: License :: OSI Approved :: MIT License")
        self.assertIn("PEP 639", self.rules_hit(text))

    def test_the_finding_names_the_offending_classifier(self):
        text = document(*CLEAN, "Classifier: License :: OSI Approved :: MIT License")
        detail = next(f for f in check_metadata.findings(text) if f.rule == "PEP 639").detail
        self.assertIn("License :: OSI Approved :: MIT License", detail)

    def test_several_licence_classifiers_are_all_named(self):
        text = document(
            *CLEAN,
            "Classifier: License :: OSI Approved :: MIT License",
            "Classifier: License :: OSI Approved :: Apache Software License",
        )
        detail = next(f for f in check_metadata.findings(text) if f.rule == "PEP 639").detail
        self.assertIn("2 license classifier(s)", detail)

    def test_the_old_style_alone_is_accepted(self):
        # A project that has not moved to PEP 639 yet is not in violation.
        headers = [h for h in CLEAN if not h.startswith("License-Expression")]
        text = document(*headers, "Classifier: License :: OSI Approved :: MIT License")
        self.assertEqual(self.rules_hit(text), set())

    def test_a_document_with_no_licence_at_all_is_a_finding(self):
        headers = [h for h in CLEAN if not h.startswith("License-Expression")]
        self.assertIn("licence", self.rules_hit(document(*headers)))

    def test_an_empty_long_description_is_a_finding(self):
        self.assertIn("long description", self.rules_hit(document(*CLEAN, body="   \n")))

    def test_a_missing_summary_is_a_finding(self):
        headers = [h for h in CLEAN if not h.startswith("Summary")]
        self.assertIn("summary", self.rules_hit(document(*headers)))

    def test_findings_are_independent_of_one_another(self):
        headers = [h for h in CLEAN if not h.startswith(("Summary", "License-Expression"))]
        self.assertEqual(
            self.rules_hit(document(*headers, body="\n")),
            {"licence", "long description", "summary"},
        )


class Seam(unittest.TestCase):
    """The part a hand-written document cannot cover."""

    def test_metadata_is_read_out_of_a_real_archive(self):
        with tempfile.TemporaryDirectory() as tmp:
            wheel = Path(tmp) / "thing-1.0-py3-none-any.whl"
            with zipfile.ZipFile(wheel, "w") as archive:
                archive.writestr("thing/__init__.py", "")
                archive.writestr("thing-1.0.dist-info/RECORD", "")
                archive.writestr("thing-1.0.dist-info/METADATA", document(*CLEAN))
            self.assertIn("License-Expression: MIT", check_metadata.metadata_of(wheel))

    def test_an_archive_without_metadata_fails_loudly(self):
        # Returning an empty string here would report zero findings, which is
        # the same output as a package with none.
        with tempfile.TemporaryDirectory() as tmp:
            wheel = Path(tmp) / "empty-1.0-py3-none-any.whl"
            with zipfile.ZipFile(wheel, "w") as archive:
                archive.writestr("empty/__init__.py", "")
            with self.assertRaises(SystemExit):
                check_metadata.metadata_of(wheel)

    def test_a_record_file_is_not_mistaken_for_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            wheel = Path(tmp) / "thing-1.0-py3-none-any.whl"
            with zipfile.ZipFile(wheel, "w") as archive:
                archive.writestr("thing-1.0.dist-info/METADATA", document(*CLEAN))
                archive.writestr("thing-1.0.dist-info/METADATA.txt", "not this one")
            self.assertIn("Name: factorbase", check_metadata.metadata_of(wheel))

    def test_the_script_passes_against_this_repository(self):
        # Slow: it builds. It is here because everything above would still pass
        # if the build step were broken.
        run = subprocess.run(
            [sys.executable, str(HERE / "check_metadata.py")],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertIn("0 finding(s)", run.stdout)
        self.assertIn("Metadata-Version", run.stdout)


if __name__ == "__main__":
    unittest.main()
