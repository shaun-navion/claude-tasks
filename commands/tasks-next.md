---
description: Show the prioritised, dependency-aware "what's next" view of the queue
argument-hint: "[--top N] [--actionable]"
---

Rank the queue and show what to do next.

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/prioritise.py" ${ARGUMENTS:---top 8}
```

Ranks the `ready/` briefs by due urgency + importance + quick-win + lead time + a bonus
for briefs that unblock others (dependency-aware: a brief stays blocked until its
dependencies are `done`). Flags show `⛔blocked`, `🙋needs-you`, `→N` (unblocks N others),
and `⏱lead` (must start now).

The script resolves the queue via `$CLAUDE_TASKS_DIR` → nearest `.tasks/` → `~/tasks`; if
it reports "No task queue", run `/tasks-init` first.

After it runs, state the top few back in plain language — id, title, why it ranks there,
and whether it's actionable now or blocked / waiting on the user. Pass `--actionable` to
show only what Claude can pick up and run end-to-end.
