---
description: Scaffold a new claude-tasks queue (lifecycle folders, config, brief template)
argument-hint: "[path] [--name <project-name>]"
---

Create a new task queue.

Run the init script, passing through whatever the user gave in `$ARGUMENTS` (a target
path and optional `--name`). If they gave no path, default to `~/tasks`:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/init_queue.py" ${ARGUMENTS:-~/tasks}
```

This creates the lifecycle folders (`inbox/ ready/ in-progress/ done/ parked/`), a
`view/` directory, a `tasks.toml` config, a `_template.md` brief template, and a
`.gitignore`. The presence of `tasks.toml` is what marks a directory as a queue.

After it runs:

1. Tell the user where the queue was created.
2. Explain how the scripts will find it (resolution order): the `$CLAUDE_TASKS_DIR`
   environment variable, else a `.tasks/` directory found by walking up from the working
   directory, else `~/tasks`. If they created it somewhere non-default, suggest they
   either set `CLAUDE_TASKS_DIR` or name the directory `.tasks` inside a project.
3. Offer to `git init` the queue if it isn't already under version control — the whole
   point is that the queue is greppable, diffable, and syncable.
4. Optionally open `tasks.toml` so they can set the project `name` and the list of
   `domains` their briefs can use.
