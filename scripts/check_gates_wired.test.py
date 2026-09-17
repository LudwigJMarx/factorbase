#!/usr/bin/env python3
"""Tests for check_gates_wired.py.

── WHY THE SECOND HALF ─────────────────────────────────────────────────────

The first block drives `analyse` with made-up inputs. That is convenient and it
covers the decision, and it is exactly where ifc-lite PR #4900 went wrong: both
halves of the change took an injected "does this exist?" function, every test
handed in a stand-in, the stand-in was correct and the real function was not.
No test could fail.

So the second block runs the script itself against a real tree built in a
temporary directory. It covers precisely what the stand-in replaces in the
first block: finding files, reading workflows, parsing package.json, setting an
exit code.

Usage:  python3 scripts/check_gates_wired.test.py
        (not through `-m unittest`: this file is not importable as a module name)
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "check_gates_wired.py"

_spec = importlib.util.spec_from_file_location("check_gates_wired", SOURCE)
module = importlib.util.module_from_spec(_spec)
assert _spec and _spec.loader
_spec.loader.exec_module(module)


class Decision(unittest.TestCase):
    """The pure part: who counts as wired."""

    def test_named_in_a_workflow_counts_as_wired(self):
        result = module.analyse(
            ["check-a.py"],
            "run: python3 scripts/check-a.py",
            {},
            {"check-a.py": ""},
        )
        self.assertEqual(result["reached"], ["check-a.py"])
        self.assertEqual(result["open"], [])

    def test_through_a_package_script_the_ci_calls(self):
        result = module.analyse(
            ["check-a.py"],
            "run: npm run checks",
            {"checks": "python3 scripts/check-a.py"},
            {"check-a.py": ""},
        )
        self.assertEqual(result["open"], [])

    def test_a_package_script_nobody_calls_wires_nothing(self):
        # The lesson from ifc-lite #3062: an entry in package.json that no
        # workflow ever starts runs as often as no entry at all.
        result = module.analyse(
            ["check-a.py"],
            "run: npm run build",
            {"checks": "python3 scripts/check-a.py"},
            {"check-a.py": ""},
        )
        self.assertEqual(result["open"], ["check-a.py"])

    def test_a_reached_checker_pulls_in_the_one_it_calls(self):
        result = module.analyse(
            ["check-a.py", "check-b.py"],
            "run: python3 scripts/check-a.py",
            {},
            {
                "check-a.py": "subprocess.run(['python3', 'scripts/check-b.py'])",
                "check-b.py": "",
            },
        )
        self.assertEqual(result["open"], [])
        self.assertIn("check-b.py", result["reached"])

    def test_the_chain_terminates_instead_of_looping(self):
        # Two checkers naming each other must not spin.
        result = module.analyse(
            ["check-a.py", "check-b.py"],
            "run: python3 scripts/check-a.py",
            {},
            {"check-a.py": "scripts/check-b.py", "check-b.py": "scripts/check-a.py"},
        )
        self.assertEqual(result["open"], [])

    def test_an_exemption_is_listed_rather_than_hidden(self):
        result = module.analyse(
            ["check-a.py"],
            "",
            {},
            {"check-a.py": "# @not-in-ci reads the developer's clock, not the repository\n"},
        )
        self.assertEqual(result["open"], [])
        self.assertEqual(
            result["exempt"],
            {"check-a.py": "reads the developer's clock, not the repository"},
        )

    def test_prose_about_the_exemption_excuses_nothing(self):
        # On its first run against itself the script excused itself: its own
        # header EXPLAINS the marker, and the detection saw it mid-sentence.
        result = module.analyse(
            ["check-a.py"],
            "",
            {},
            {"check-a.py": "# Write `@not-in-ci <reason>` in the header if you must.\n"},
        )
        self.assertEqual(result["exempt"], {})
        self.assertEqual(result["open"], ["check-a.py"])

    def test_a_placeholder_reason_does_not_count(self):
        result = module.analyse(["check-a.py"], "", {}, {"check-a.py": "# @not-in-ci <reason>\n"})
        self.assertEqual(result["exempt"], {})

    def test_an_unwired_checker_is_reported(self):
        result = module.analyse(["check-a.py"], "", {}, {"check-a.py": ""})
        self.assertEqual(result["open"], ["check-a.py"])


class AgainstARealTree(unittest.TestCase):
    """The seam: finding files, reading workflows, setting an exit code.

    The block above cannot see any of this. There, every one of those answers
    was handed in by hand.
    """

    def build(self, directory: Path, files: dict[str, str]) -> None:
        for path, content in files.items():
            target = directory / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")

    def run_script(self, root: Path) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(SOURCE), "--root", str(root)],
            capture_output=True,
            text=True,
        )

    def test_finds_the_unwired_checker_and_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.build(
                root,
                {
                    "scripts/check-a.py": "print('a')\n",
                    "scripts/deep/check-b.py": "print('b')\n",
                    ".github/workflows/checks.yml": (
                        "jobs:\n  c:\n    steps:\n      - run: python3 scripts/check-a.py\n"
                    ),
                },
            )
            run = self.run_script(root)

            self.assertEqual(run.returncode, 1)
            self.assertIn("check-b.py", run.stdout)
            tail = run.stdout.split("Nothing calls these")[-1]
            self.assertNotIn("scripts/check-a.py\n", tail)

    def test_green_when_everything_is_wired(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.build(
                root,
                {
                    "scripts/check-a.py": "print('a')\n",
                    "package.json": json.dumps(
                        {"scripts": {"checks": "python3 scripts/check-a.py"}}
                    ),
                    ".github/workflows/ci.yml": "steps:\n  - run: npm run checks\n",
                },
            )
            run = self.run_script(root)

            self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
            self.assertIn("1 checker(s), 1 wired", run.stdout)

    def test_no_checker_found_says_so_instead_of_reporting_green(self):
        # "0 problems" is also what a checker reports that looked at nothing.
        # The two cases have to stay distinguishable.
        with tempfile.TemporaryDirectory() as tmp:
            run = self.run_script(Path(tmp))

            self.assertEqual(run.returncode, 0)
            self.assertIn("no checker found", run.stdout)

    def test_test_files_do_not_count_as_checkers(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.build(root, {"scripts/check-a.test.py": "pass\n"})
            run = self.run_script(root)

            self.assertEqual(run.returncode, 0)
            self.assertIn("no checker found", run.stdout)


if __name__ == "__main__":
    unittest.main()
