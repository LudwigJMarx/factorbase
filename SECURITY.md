# Security

## Reporting

Use GitHub's private vulnerability reporting on this repository ("Security"
tab, "Report a vulnerability"). Do not open a public issue.

Expect an acknowledgement within 72 hours and an assessment within 7 days. If
you have had no reply after 7 days, open a public issue saying only that you
are waiting on a private report, with no detail.

This is one person, not a team with a rota. Say so in the report if you have a
disclosure deadline, and it will be respected.

## What the attack surface actually is

factorbase is a library. It opens no socket, starts no server, reads no
credential and calls no remote service. Most of what a security policy usually
covers does not apply here, and saying so is more useful than implying
otherwise.

Two things are worth stating plainly.

**The catalogue is executable by reference.** An entry names its implementation
as text, `module:function`, and `factorbase.registry.resolve` imports that
module. Importing a Python module runs its top-level code. The catalogue
shipped in the package is trusted because it is part of the package, but
`FACTORBASE_CATALOG` points the loader at a directory of your choosing:

```python
# This imports whatever the YAML names, and importing runs code.
os.environ["FACTORBASE_CATALOG"] = "/somewhere/else"
```

So a catalogue directory is code, not data. Treat one you did not write the
way you would treat a Python file you did not write. Pointing that variable at
a directory someone else supplies is equivalent to running their code.

**The YAML itself is parsed safely.** Loading uses `yaml.safe_load`, which
constructs no arbitrary Python objects. A hostile YAML file can produce a
malformed catalogue, which the loader rejects with a `CatalogError`, but it
cannot execute anything by itself. The execution comes from the
`implementation` field described above, not from the parser.

## In scope

- Anything that makes the package execute code the caller did not name, other
  than through a catalogue directory they chose themselves.
- Path handling in `db.build`, which deletes and rewrites the file it is given.
- Anything that makes the loader accept a catalogue it should reject, since a
  rejected catalogue is the only thing standing between a malformed entry and
  a silently wrong number.

## Out of scope

- Pointing `FACTORBASE_CATALOG` at a directory you do not trust. That is
  documented above and is not a defect.
- A wrong number. That is a defect and matters more than most things here, but
  it is not a vulnerability. Report it as an issue, with the template that asks
  where your expected value came from.
- Resource use on a large frame. These are numeric routines over pandas
  objects; they are as fast or as slow as the arithmetic requires.

## Dependencies

Runtime: `pandas`, `numpy`, `PyYAML`. Nothing else, by design. The floors are
declared in `pyproject.toml` and exercised in CI against the lowest version
each one is allowed to be, so a claim about a minimum is measured rather than
assumed.
