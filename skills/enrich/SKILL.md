---
name: enrich
description: Process the queue's inbox/ items into full ready/ briefs. Human-initiated (never automatic). For each item — dedup check, gather context, fill all frontmatter fields, write goal + criteria + context, commit to ready/, and archive the raw file to inbox/.processed/ (never delete — audit trail). MANDATORY cost discipline - enrichment subagents run on a cheap model (Sonnet/Haiku) not the top-tier model, in batches of 2-3, concurrency capped at 4, chunking inboxes of 20+ into sequential waves. Flag if the inbox grows past 20 items.
---

# enrich

Turns raw `inbox/` captures into executable `ready/` briefs. **Run on demand only** —
human-initiated, never automatic.

## Cost discipline (MANDATORY - read before any fan-out)

Enriching a large inbox by fanning out subagents is the one place this skill can run up a
surprising bill. A large fan-out (dozens of items) on the top-tier reasoning model, in
oversized batches, can run an account into its spend cap mid-run. The mechanism: each
subagent re-bills its whole (growing) context as cache_read on every turn, and a batch too
large to finish in one wave forces a redundant second wave of fresh agents. Keep fan-out
cheap and bounded:

- **Cheap model, not the top tier.** Dispatch every enrichment subagent with a cheap model
  (e.g. Sonnet or Haiku), never the top-tier reasoning model. Enrichment is mechanical
  (dedup grep, gather, fill a template); it does not need the expensive model. This is the
  single biggest cost lever (roughly 5x).
- **Batch 2-3 items per subagent**, never 5-12. Small batches finish in ONE wave, so no
  leftover items force a re-dispatch of fresh agents.
- **Cap concurrency at 4** subagents at once, so a burst cannot spike the spend rate.
- **Large inbox (>= 20 items): chunk into sequential waves.** Do not fan out all at once;
  process a capped number, commit, then the next wave. Warn the user the run is large.
- **Small runs (~6 items or fewer): do them INLINE** (no subagent fan-out at all). Fan-out
  only earns its overhead on a real backlog.

## When to run

- The user runs `/enrich` or says "enrich the inbox" / "clear the inbox".
- When `inbox/` has 5+ unprocessed items and there's a natural gap.

## Process (one item at a time)

For each file in `inbox/` (whether `raw: true` or partial frontmatter):

### 1. Dedup check first
```bash
grep -rl "<keyword>" "$CLAUDE_TASKS_DIR"/{inbox,ready,in-progress,done} 2>/dev/null
```
If a match exists, fold this capture's context into the existing brief and archive the
raw file — don't create a duplicate.

### 2. Gather context
Pull from every source available before enriching: linked repos/PRs/docs, related prior
briefs, the current session, anything the capture references. Don't ask the user for
context that's already discoverable.

### 3. Fill the brief fully

| Field | Guidance |
|---|---|
| `title` | Scannable one-liner, lead with the noun |
| `goal` | End state, not "do X" |
| `context` | Everything a zero-context agent needs (paths, repos, links, why) |
| `criteria` | Checkable conditions — if you can't check it, rewrite it |
| `importance` | 1–4 (default 3 unless clearly urgent/strategic) |
| `autonomy` | Honest: `full` ONLY if a future agent can complete end-to-end with zero user input |
| `estimated-effort` | xs / s / m / l / xl |
| `complexity` | **Always populate.** `mechanical` = deterministic work (scripted edits, dedup grep, data moves, fill-a-template) a cheap model can do reliably; `judgment` = needs top-tier reasoning (design, real ambiguity, multi-file architecture, client-facing judgement). Drives model routing in action-task (mechanical -> cheap model like Sonnet/Haiku, judgment -> top tier like Opus). When unsure, mark `judgment`. |
| `domain` | one of the domains in `tasks.toml` |
| `tags` | free-form labels (e.g. `depends:<other-id>`) |
| `requires-local` | `true` if the brief needs local-machine files or creds |
| `requires-repo` | repo slug if the brief needs a repo other than this queue |

### 4. Write to ready/
Use `add_task.py --ready`, or write directly to `ready/` with `status: ready` and commit.

### 5. Archive the raw file
```bash
mkdir -p "$CLAUDE_TASKS_DIR/inbox/.processed"
mv "$CLAUDE_TASKS_DIR/inbox/<file>.md" "$CLAUDE_TASKS_DIR/inbox/.processed/<file>.md"
```
**Never delete.** `.processed/` is the audit trail for where briefs originated.

## Inbox hygiene
- `inbox/` items are **not briefs** — never present them as the actionable queue.
- If inbox grows to 20+ items, flag it: "Inbox has N items — consider an enrich session."
- After enrichment, commit all new `ready/` briefs and the `.processed/` archives together.
