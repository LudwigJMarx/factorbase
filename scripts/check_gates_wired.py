#!/usr/bin/env python3
"""Check that every checker in this project is actually run by something.

── WHY THIS EXISTS ─────────────────────────────────────────────────────────

A checker nobody starts cannot be told apart from a checker that found
nothing. Both report silence. Both look like order.

That happened in the ifc-lite repository, their #3062: a gate script was
committed together with its test, with no CI step, no package.json entry and
no build task. Nobody noticed, because a checker that never runs produces the
same quiet as a satisfied one. Their conclusion, in their words: an entry in
package.json that no workflow ever calls runs exactly as often as no entry at
all.

This script is the checker for that. It is deliberately the only one here that
concerns itself with other checkers; everything else belongs inside the
checkers themselves.

── WHAT COUNTS AS A CHECKER ────────────────────────────────────────────────

Any file under `scripts/`, at any depth, whose name begins with `check`,
`verify` or `gate`, with the extension .py, .sh, .mjs, .js or .ts. The naming
convention is the registration: a checker called something else has not
registered and will not be missed here. That is the known gap, not an
oversight.

── WHAT COUNTS AS BEING RUN ────────────────────────────────────────────────

1. The file name appears in a workflow under `.github/workflows/`.
2. The file name appears in a script in `package.json` or `pyproject.toml`,
   and that script's own name appears in a workflow. One level of indirection
   and no more; deeper chains are rare and the extra imprecision is not worth
   it.
3. A checker already reached by 1 or 2 names this file, and so calls or
   imports it.

── AN EXEMPTION THAT STAYS VISIBLE ─────────────────────────────────────────

A script that is deliberately not meant to run in CI carries
`@not-in-ci <reason>` within its first 40 lines. It is then listed rather than
hidden. An exemption without a reason is an error, because otherwise it would
be a silent hole.

Usage:  python3 scripts/check_gates_wired.py [--root PATH]
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

PREFIXES = ("check", "verify", "gate")
EXTENSIONS = (".py", ".sh", ".mjs", ".js", ".ts")
SKIP = {"node_modules", "dist", "build", ".git", ".venv", "__pycache__", "target"}

# The marker has to be the WHOLE comment line, and its reason must not be a
# placeholder. The first version searched for it anywhere in the line, and so
# excused this very script, whose own header explains the marker. A tool that
# mistakes its own documentation for a finding is precisely the trap it was
# built to catch.
EXEMPTION = re.compile(r"^\s*(?:#|//|\*)?\s*@not-in-ci\s+(?!<)(.+?)\s*$")


def is_checker(path: Path) -> bool:
    name = path.name.lower()
    if name.endswith(".test.py") or ".test." in name or ".spec." in name:
        return False
    return name.startswith(PREFIXES) and path.suffix in EXTENSIONS


def collect_checkers(root: Path) -> list[Path]:
    scripts = root / "scripts"
    if not scripts.is_dir():
        return []
    return sorted(
        p
        for p in scripts.rglob("*")
        if p.is_file() and not SKIP & set(p.relative_to(root).parts) and is_checker(p)
    )


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def exemption_reason(content: str) -> str | None:
    for line in content.splitlines()[:40]:
        found = EXEMPTION.search(line)
        if found:
            return found.group(1).strip()
    return None


def analyse(
    checkers: list[str],
    ci_text: str,
    package_scripts: dict[str, str],
    contents: dict[str, str],
) -> dict:
    """The decision itself, kept pure so the test can drive it without a tree.

    The test then additionally runs the whole script against a real directory,
    because otherwise only the stand-in would be under test and not the seam
    where it is replaced by the real thing.

    `checkers`         file names, without their paths
    `ci_text`          all workflow text, concatenated
    `package_scripts`  name -> command line, from package.json or pyproject.toml
    `contents`         file name -> the checker's own text
    """
    direct = {c for c in checkers if c in ci_text}

    via_package = set()
    for name, command in package_scripts.items():
        if not any(c in command for c in checkers):
            continue
        if name in ci_text:
            via_package |= {c for c in checkers if c in command}

    reached = direct | via_package
    # A checker that is reached and calls another reaches that one too.
    for _ in range(len(checkers)):
        grown = set(reached)
        for name in reached:
            text = contents.get(name, "")
            grown |= {other for other in checkers if other != name and other in text}
        if grown == reached:
            break
        reached = grown

    exempt = {c: reason for c in checkers if (reason := exemption_reason(contents.get(c, "")))}
    open_gates = [c for c in checkers if c not in reached and c not in exempt]
    return {"reached": sorted(reached), "exempt": exempt, "open": sorted(open_gates)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", default=".", type=Path)
    arguments = parser.parse_args()
    root = arguments.root.resolve()

    paths = collect_checkers(root)
    if not paths:
        # Finding no checker does not mean everything is wired. It means either
        # that there are none or that the search looked in the wrong place, and
        # those two must not print the same thing.
        print(f"check_gates_wired: no checker found under {root}/scripts.")
        print("  Either there are none here, or the naming convention does not match")
        expected = f"name starts with {'/'.join(PREFIXES)}, extension in {', '.join(EXTENSIONS)}"
        print(f"  (expected: {expected}).")
        return 0

    workflow_directory = root / ".github" / "workflows"
    workflows = sorted(workflow_directory.glob("*.y*ml")) if workflow_directory.is_dir() else []
    ci_text = "\n".join(read(p) for p in workflows)

    package_scripts: dict[str, str] = {}
    package = root / "package.json"
    if package.is_file():
        import json

        try:
            package_scripts.update(json.loads(read(package)).get("scripts") or {})
        except json.JSONDecodeError:
            print(f"check_gates_wired: {package} is not valid JSON.", file=sys.stderr)
            return 1

    pyproject = root / "pyproject.toml"
    if pyproject.is_file():
        # Deliberately lexical rather than through a TOML parser: depending on
        # the tool, tasks live under [tool.poe.tasks], [tool.hatch.envs...] or
        # somewhere else, and a line `name = "...check-x.py..."` catches them all.
        for line in read(pyproject).splitlines():
            found = re.match(r'\s*([\w.-]+)\s*=\s*["\'](.+)["\']\s*$', line)
            if found:
                package_scripts.setdefault(found.group(1), found.group(2))

    contents = {p.name: read(p) for p in paths}
    result = analyse([p.name for p in paths], ci_text, package_scripts, contents)

    by_name = {p.name: p.relative_to(root).as_posix() for p in paths}

    print(
        f"check_gates_wired: {len(paths)} checker(s), "
        f"{len(result['reached'])} wired, "
        f"{len(result['exempt'])} exempt, "
        f"{len(result['open'])} unreachable "
        f"({len(workflows)} workflow file(s) read)."
    )
    for name, reason in sorted(result["exempt"].items()):
        print(f"  no CI gate, by declaration: {by_name[name]} - {reason}")

    if result["open"]:
        print()
        print("Nothing calls these. They run as often as files that do not exist:")
        for name in result["open"]:
            print(f"  {by_name[name]}")
        print()
        print("Fix: add a step in .github/workflows/, or a script in")
        print("package.json / pyproject.toml that a workflow calls - or put the line")
        print("`@not-in-ci <reason>` in the file's header if that is the intention.")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
