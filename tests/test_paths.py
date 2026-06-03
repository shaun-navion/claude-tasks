"""Tests for _paths.py — resolving which queue directory the scripts operate on.

The scripts live in the plugin; the queue is the user's data elsewhere. resolve_root
decides where, from (1) an env var, (2) a project-local .tasks/ found by walking up, or
(3) the ~/tasks default. require_queue refuses to operate on an uninitialised directory.
"""
import _paths
import pytest


def test_public_constants_are_the_documented_contract():
    # These are the user-facing contract (env var, marker dir, default location, config
    # filename, lifecycle folders). Pin them to literals so a change can't slip through.
    assert _paths.ENV_VAR == "CLAUDE_TASKS_DIR"
    assert _paths.PROJECT_MARKER == ".tasks"
    assert _paths.DEFAULT_ROOT == "~/tasks"
    assert _paths.CONFIG_FILE == "tasks.toml"
    assert _paths.TASK_DIRS == ("inbox", "ready", "in-progress", "done", "parked")


def test_env_var_wins(tmp_path):
    target = tmp_path / "somewhere"
    root = _paths.resolve_root(env={_paths.ENV_VAR: str(target)}, cwd=tmp_path)
    assert root == target


def test_env_var_expands_user():
    root = _paths.resolve_root(env={_paths.ENV_VAR: "~/myqueue"}, cwd="/tmp")
    assert root == _paths.pathlib.Path("~/myqueue").expanduser()


def test_walks_up_to_project_marker(tmp_path):
    (tmp_path / _paths.PROJECT_MARKER).mkdir()
    deep = tmp_path / "a" / "b" / "c"
    deep.mkdir(parents=True)
    root = _paths.resolve_root(env={}, cwd=deep)
    assert root == tmp_path / _paths.PROJECT_MARKER


def test_marker_in_cwd_itself(tmp_path):
    (tmp_path / _paths.PROJECT_MARKER).mkdir()
    root = _paths.resolve_root(env={}, cwd=tmp_path)
    assert root == tmp_path / _paths.PROJECT_MARKER


def test_falls_back_to_default(tmp_path):
    # nothing in env, no .tasks/ anywhere up the tree → the ~/tasks default
    root = _paths.resolve_root(env={}, cwd=tmp_path)
    assert root == _paths.pathlib.Path(_paths.DEFAULT_ROOT).expanduser()


def test_empty_env_var_ignored(tmp_path):
    # an empty string must not be treated as a real override
    root = _paths.resolve_root(env={_paths.ENV_VAR: ""}, cwd=tmp_path)
    assert root == _paths.pathlib.Path(_paths.DEFAULT_ROOT).expanduser()


def test_is_queue_true_when_config_present(tmp_path):
    (tmp_path / _paths.CONFIG_FILE).write_text("name = 'x'\n")
    assert _paths.is_queue(tmp_path) is True


def test_is_queue_false_when_absent(tmp_path):
    assert _paths.is_queue(tmp_path) is False


def test_require_queue_returns_root_when_initialised(tmp_path):
    (tmp_path / _paths.CONFIG_FILE).write_text("name = 'x'\n")
    assert _paths.require_queue(tmp_path) == tmp_path


def test_require_queue_raises_with_guidance(tmp_path):
    with pytest.raises(SystemExit) as exc:
        _paths.require_queue(tmp_path)
    msg = str(exc.value)
    assert msg.startswith("No task queue at")  # names the missing queue
    assert msg.rstrip().endswith("to create one.")  # points at the fix
    assert "/tasks-init" in msg
