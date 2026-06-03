"""Tests for build_board.py — rendering briefs into the read-only HTML board.

One rich fixture queue exercises the structural branches (epics, children, orphan
children, loose cards, empty columns, raw inbox items, progress bars), plus targeted
cases for the frontmatter/section parsers and the main() entrypoint.
"""
import build_board
import init_queue


def _write(root, folder, name, text):
    (root / folder / name).write_text(text)


def _brief(bid, *, title="T", status="ready", btype="todo", autonomy="full",
           importance="2", parent="", domain="", effort="", criteria=None, goal="A goal."):
    crit = "\n".join(criteria) if criteria else ""
    return f"""---
id: {bid}
title: {title}
status: {status}
type: {btype}
importance: {importance}
autonomy: {autonomy}
estimated-effort: {effort}
domain: {domain}
parent: {parent}
---

## Goal

{goal}

## Success criteria

{crit}
"""


# ── parse_frontmatter / section ───────────────────────────────────────────────

def test_parse_frontmatter_splits_body():
    fm, body = build_board.parse_frontmatter(_brief("x"))
    assert fm["id"] == "x"
    assert "## Goal" in body


def test_parse_frontmatter_no_frontmatter():
    fm, body = build_board.parse_frontmatter("just body")
    assert fm == {}
    assert body == "just body"


def test_parse_frontmatter_skips_lines_without_colon():
    fm, _ = build_board.parse_frontmatter("---\nid: x\nstray line no colon\n---\nbody")
    assert fm == {"id": "x"}  # the colon-less line is ignored, not crashed on


def test_section_extracts_and_stops_at_next_heading():
    _, body = build_board.parse_frontmatter(_brief("x", goal="Only this."))
    assert build_board.section(body, "Goal") == "Only this."
    assert build_board.section(body, "Nonexistent") == ""


# ── load_briefs ───────────────────────────────────────────────────────────────

def test_load_briefs_skips_non_inbox_file_without_id(tmp_path):
    root = init_queue.init_queue(tmp_path / "q", name="demo")
    _write(root, "ready", "no-id.md", "---\ntitle: headless\n---\n\nbody\n")
    ids = [b["id"] for b in build_board.load_briefs(root)]
    assert "no-id" not in ids


def test_load_briefs_synthesises_raw_inbox_item(tmp_path):
    root = init_queue.init_queue(tmp_path / "q", name="demo")
    _write(root, "inbox", "raw-thought.md", "---\nraw: true\n---\n\n# Raw thought\n\nsome body\n")
    briefs = {b["id"]: b for b in build_board.load_briefs(root)}
    assert "raw-thought" in briefs
    assert briefs["raw-thought"]["goal"].startswith("# Raw thought")


# ── build(): the structural fixture ───────────────────────────────────────────

def _rich_queue(tmp_path):
    root = init_queue.init_queue(tmp_path / "q", name="My Project")
    # an epic with a child in the same column (kids branch + progress bar)
    _write(root, "ready", "epic-a.md", _brief("epic-a", title="Epic A", btype="project"))
    _write(root, "ready", "child-1.md", _brief(
        "child-1", title="Child One", parent="epic-a", domain="work", effort="xs",
        criteria=["- [x] done bit", "- [ ] todo bit"]))
    # a loose card with non-checklist criteria text + an invalid importance + odd autonomy
    _write(root, "ready", "loose-1.md", _brief(
        "loose-1", title="Loose", autonomy="weird", importance="9",
        goal="# TODO", criteria=["free text criterion"]))
    # an orphan child whose parent epic lives in a DIFFERENT column
    _write(root, "ready", "orphan.md", _brief(
        "orphan", title="Orphan", parent="epic-b", autonomy="needs-input"))
    # the parent epic, in another column, with no children of its own → "no sub-tasks"
    _write(root, "in-progress", "epic-b.md", _brief(
        "epic-b", title="Epic B", status="in-progress", btype="project", autonomy="blocked"))
    return root


def test_build_writes_board_with_all_structures(tmp_path):
    root = _rich_queue(tmp_path)
    build_board.build(root, "My Project")
    page = (root / "view" / "board.html").read_text()
    assert "My Project" in page                 # project name in the title
    assert "Epic A" in page and "Child One" in page
    assert "no sub-tasks" in page               # epic-b has none in its column
    assert "Orphan" in page                     # orphan child still rendered
    assert "nothing here" in page               # done/ and parked/ are empty
    assert "1/2" in page                        # child-1 progress (1 of 2 criteria)
    assert "free text criterion" in page        # non-checklist criterion rendered


def test_build_counts_autonomy_in_header(tmp_path):
    root = _rich_queue(tmp_path)
    build_board.build(root, "My Project")
    page = (root / "view" / "board.html").read_text()
    # epic-a + child-1 are autonomy:full in ready → "Claude can do (2)"
    assert "Claude can do (2)" in page


def test_main_uses_resolver_and_config(tmp_path, monkeypatch):
    root = init_queue.init_queue(tmp_path / "q", name="Resolved Name")
    _write(root, "ready", "one.md", _brief("one", title="Just one"))
    monkeypatch.setenv("CLAUDE_TASKS_DIR", str(root))
    build_board.main()
    page = (root / "view" / "board.html").read_text()
    assert "Resolved Name" in page
    assert "Just one" in page
