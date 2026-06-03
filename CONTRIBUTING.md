# Contributing

## Dev setup

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install pytest pytest-cov ruff mypy "mutmut<3"
```

Requires Python 3.11+. The scripts are pure-stdlib and run directly (no install step);
the dependencies above are dev tooling only. `tests/conftest.py` puts `scripts/` on the
import path.

## The gates (all blocking in CI)

```bash
ruff check scripts/ tests/        # lint
mypy scripts/                     # strict static typing
pytest --cov=scripts --cov-report=term-missing   # tests + 100% coverage gate
```

All three must pass. Coverage is **100% of our own code** — declared exclusions only
(`# pragma: no cover` on `if __name__ == "__main__"` shells).

## Mutation testing

Mutation testing proves the tests *assert* behaviour, not just execute it.

```bash
mutmut run --paths-to-mutate "scripts/_paths.py,scripts/config.py"
mutmut results
```

The CI gate requires **zero surviving mutants** on the dependency-resolution and config
core. Note: `mutmut<3` does not yet run on Python 3.14 — use a 3.11–3.13 interpreter for
mutation runs. Presentational/template strings (e.g. the board's embedded HTML) are not
mutation-gated; they are covered by render assertions instead.

## Principles

- **Engine vs. config.** Anything user-specific is a value in `tasks.toml`, never code.
- **The briefs are the source of truth.** The board is a regenerated view; never hand-edit
  generated HTML, and never edit a brief's `status:` by hand — go through `transition.py`
  so the cross-process lock is respected.
- **Schema and `_template.md` change together.** Drift between them is the failure mode
  that kills these systems.
- **TDD.** Write the test first; for the string-heavy modules, assert against literal
  expected values, not the code's own constants (a tautology mutation testing will catch).

## Layout

```
scripts/    the engine (pure-stdlib Python; flat modules sharing top-level names)
tests/      pytest suite (conftest puts scripts/ on the path)
skills/     Claude Code skills (SKILL.md per skill)
commands/   slash commands (/tasks-init, /tasks-board)
docs/       design doc
```
