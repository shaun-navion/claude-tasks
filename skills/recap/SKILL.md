---
name: recap
description: Use when the user asks what has been discussed, wants a quick status check, says "recap", "remind me what we've done", "what's outstanding", "where are we", or any variation of wanting a mid-session or end-of-session summary in the chat. Trigger immediately — do not ask clarifying questions first. This is a quick in-chat summary, NOT a file write.
---

# recap

Produce a concise, structured in-chat summary of the current conversation. No files
written. No preamble — go straight to the summary.

## Output format

Use this structure, omitting any section that has nothing to put in it:

```
**Topics covered**
- [Brief bullet per topic]

**Decisions made**
- [Decision + one-line reasoning if relevant]

**Actions taken**
- [Specific things done — file changes, PRs opened (with links), commands run, etc.]

**Outstanding**
- [Anything unresolved, deferred, or still to do — be specific and actionable]
```

## What to include

- **Topics covered**: every distinct subject discussed, even briefly.
- **Decisions made**: anything the user chose between, or agreed to a course of action.
- **Actions taken**: concrete outputs — files written, PRs opened, commands run. Include
  URLs if they came up.
- **Outstanding**: open PRs awaiting review, deferred decisions, anything the user would
  need to pick up cold. If the queue has relevant open briefs, you may mention them.

## What to omit

- Tool-call details and intermediate steps — summarise the outcome, not the process.
- Anything fully resolved with no follow-up needed.
- Filler phrases and meta-commentary.

## Tone

Short. Scannable. Bullets over prose. If a section is empty, skip it entirely rather than
writing "None".
