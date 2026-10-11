"""The fixed set of check types (see LESSONS_PLAN.md, section 2.5).

``evaluate(check, ctx)`` is a pure function: it only reads the sandbox and the
context, it never changes anything.
"""

from __future__ import annotations

import os
import re
import stat
from dataclasses import dataclass
from typing import Any, Dict

CHECK_TYPES = (
    "command_matches",
    "output_contains",
    "file_exists",
    "dir_exists",
    "path_missing",
    "file_contains",
    "file_mode",
    "cwd_is",
    "all",
)

# Parameters each check type needs (besides "type").
REQUIRED_PARAMS = {
    "command_matches": ("pattern",),
    "output_contains": ("text",),
    "file_exists": ("path",),
    "dir_exists": ("path",),
    "path_missing": ("path",),
    "file_contains": ("path", "text"),
    "file_mode": ("path", "mode"),
    "cwd_is": ("path",),
    "all": ("checks",),
}

STREAMS = ("stdout", "stderr", "both")


@dataclass
class Context:
    """What a check can look at after a command ran."""

    sandbox: str
    cwd: str
    command: str = ""
    stdout: str = ""
    stderr: str = ""


def _sandbox_path(ctx: Context, rel: str) -> str:
    if rel in ("", "."):
        return ctx.sandbox
    return os.path.join(ctx.sandbox, rel)


def evaluate(check: Dict[str, Any], ctx: Context) -> bool:
    """Return True if ``check`` passes for ``ctx``."""
    kind = check.get("type")

    if kind == "command_matches":
        return re.search(check["pattern"], ctx.command.strip()) is not None

    if kind == "output_contains":
        stream = check.get("stream", "stdout")
        if stream == "stdout":
            haystack = ctx.stdout
        elif stream == "stderr":
            haystack = ctx.stderr
        else:
            haystack = ctx.stdout + "\n" + ctx.stderr
        return check["text"] in haystack

    if kind == "file_exists":
        return os.path.isfile(_sandbox_path(ctx, check["path"]))

    if kind == "dir_exists":
        return os.path.isdir(_sandbox_path(ctx, check["path"]))

    if kind == "path_missing":
        return not os.path.lexists(_sandbox_path(ctx, check["path"]))

    if kind == "file_contains":
        path = _sandbox_path(ctx, check["path"])
        if not os.path.isfile(path):
            return False
        try:
            with open(path, encoding="utf-8", errors="replace") as fh:
                return check["text"] in fh.read()
        except OSError:
            return False

    if kind == "file_mode":
        path = _sandbox_path(ctx, check["path"])
        try:
            st = os.stat(path)
        except OSError:
            return False
        actual = "%03o" % (stat.S_IMODE(st.st_mode) & 0o777)
        return actual == str(check["mode"]).zfill(3)

    if kind == "cwd_is":
        want = os.path.realpath(_sandbox_path(ctx, check["path"]))
        return os.path.realpath(ctx.cwd) == want

    if kind == "all":
        return all(evaluate(sub, ctx) for sub in check["checks"])

    raise ValueError("unknown check type: %r" % (kind,))
