# Changelog

## 0.1.0 — initial release

First generic, open-sourceable extraction of a personal task-queue system into a Claude
Code plugin.

### Added
- **Engine** (pure-stdlib Python): git-backed brief lifecycle with cross-process locking
  (`_concurrency.py`), serialised commits (`git_sync.py`), queue-root resolution
  (`_paths.py`), per-queue config (`config.py`), and queue scaffolding (`init_queue.py`).
- **Scripts**: `add_task.py` (mint a brief), `raw_capture.py` (inbox dump),
  `transition.py` (resolve + move briefs through the lifecycle), `build_board.py`
  (self-contained HTML board).
- **Skills**: `queue-task`, `raw-capture`, `enrich`, `action-task`, `handoff`, `recap`.
- **Commands**: `/tasks-init`, `/tasks-board`.
- **Quality**: ruff, `mypy --strict`, 100% test coverage (110 tests), and mutation testing
  (zero surviving mutants on the resolution/config core) — all gated in CI.

### Notes
- Root resolution: `$CLAUDE_TASKS_DIR` → nearest `.tasks/` → `~/tasks`.
- Config (`tasks.toml`) is the only per-user surface; the engine is identical for everyone.

See [docs/design.md](docs/design.md) for the design and what was deferred to later add-ons.
