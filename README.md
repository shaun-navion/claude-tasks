# claude-tasks

A **git-backed task queue that Claude can capture into, structure, see, execute, and hand
off.** Each task is a self-contained markdown *brief* — rich enough that an agent can act
on it with zero prior context.

Installed as a [Claude Code](https://claude.com/claude-code) plugin. Your queue is a plain
git repo of markdown files: greppable, diffable, syncable, and yours.

> Status: **v1**. The core capture → structure → see → execute → hand-off loop is here,
> fully tested. See [Roadmap](#roadmap) for what's deliberately deferred.

## Why briefs, not to-dos

Most task tools store a title and a due date — too thin for an agent to act on. The unit
here is a **brief**:

- **Goal** — the desired end state ("X exists / Y is true"), not "do X".
- **Context** — everything a zero-context agent needs: repos, paths, links, why.
- **Success criteria** — the checkable contract for "done".
- plus constraints, notes, and an execution log.

Two actors share one queue: you drop ideas in; Claude captures its own follow-ups,
enriches raw notes into briefs, executes the ones it can do end-to-end, and hands a
session's loose ends back when it stops.

## Install

```
/plugin marketplace add <owner>/claude-tasks
/plugin install claude-tasks
```

(Or point your plugin config at this repo.) Then create your queue:

```
/tasks-init ~/tasks --name "My Queue"
```

That scaffolds the lifecycle folders, a `tasks.toml`, and a brief template, and tells you
how the scripts will find it.

## The loop

| You say… | Skill | What happens |
|---|---|---|
| "remember to…" / Claude spots a follow-up | **queue-task** | a full brief is minted |
| "capture this" (mid-flow) | **raw-capture** | a raw note lands in `inbox/` |
| "enrich the inbox" | **enrich** | raw notes become structured briefs |
| "action the X task" | **action-task** | Claude executes a brief end-to-end |
| "show the board" / `/tasks-board` | — | regenerates `view/board.html` |
| "I'm done, hand off" | **handoff** | the session's open work flows to the queue |
| "recap" | **recap** | a quick in-chat status summary |

## The queue

```
inbox/        raw, un-enriched captures (pre-briefs)
ready/        enriched, executable briefs
in-progress/  briefs being worked
done/         completed briefs (kept — they are the record)
parked/       suspended briefs
view/         generated board.html (read-only; never hand-edited)
tasks.toml    per-queue config (name, domains, timezone)
_template.md  the brief schema
```

A brief's `status:` always matches its folder. The board is a *view*, regenerated from the
briefs — the briefs are the source of truth.

### Where the queue lives (root resolution)

The scripts ship in the plugin; your queue is your data, elsewhere. The root is resolved
in order:

1. `$CLAUDE_TASKS_DIR`, if set — a global personal queue.
2. The nearest ancestor `.tasks/` directory (walk up, like git's `.git`) — project-scoped
   queues you can check into a repo.
3. `~/tasks` — the default.

## Configuration

Everything user-specific is a *value*, not code. `tasks.toml` at the queue root:

```toml
name = "My Queue"           # shown in the board title
domains = ["work", "home"]  # the allowed set for a brief's `domain:`
timezone = "UTC"
```

The engine (scripts, skills, board) is identical for everyone; only the config differs.

## Quality

Every change is gated in CI, blocking:

- **ruff** — lint
- **mypy --strict** — full static typing
- **pytest** with a **100%-coverage gate** on our own code
- **mutmut** — mutation testing on the resolution/config core (zero surviving mutants)

Line coverage proves code ran; mutation score proves the tests actually assert behaviour.

## Roadmap

Deliberately not in v1, designed to bolt on without changing the engine:

- **SessionEnd auto-capture** — a deterministic hook that parses the session transcript
  for open Task-API/TodoWrite items and files them (idempotent via a marker). Today the
  `handoff` skill does this model-driven, on demand.
- **session-browser** — browse/resume recent sessions; render one session as a board.
- **Strategic prioritisation** — rank the whole estate by a configurable leverage score.
- **External routing** — push real-world tasks to another task system.
- **Autonomous worker** — a scheduled loop that drains the `autonomy: full` queue.

## License

MIT — see [LICENSE](LICENSE).
