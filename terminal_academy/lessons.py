"""Load, validate and set up lessons (see LESSONS_PLAN.md, sections 2.1-2.6).

Also has ``run_solution_check()``: the lesson self-test from section 2.10
(setup, then for every step: the check fails before the solution and passes
after it).
"""

from __future__ import annotations

import json
import os
import re
import shutil
import stat
import sys
import tempfile
from typing import Any, Dict, List, Optional, Tuple

from terminal_academy import checks
from terminal_academy.shell import Shell

FORMAT_VERSION = 1
LESSONS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lessons")
ID_PATTERN = re.compile(r"^[0-9]{2}-[a-z0-9-]+$")
MODE_PATTERN = re.compile(r"^[0-7]{3}$")

TOP_FIELDS = {
    "format_version", "id", "title", "level", "minutes", "summary", "intro",
    "outro", "requires", "setup", "steps",
}
SETUP_FIELDS = {"path", "content", "dir", "mode"}
STEP_FIELDS = {
    "instruction", "hints", "check", "explain", "solution", "requires", "optional",
}

Lesson = Dict[str, Any]


# ----- validation ------------------------------------------------------------

def _is_str_list(value: Any, allow_empty: bool = True) -> bool:
    return (
        isinstance(value, list)
        and all(isinstance(v, str) for v in value)
        and (allow_empty or len(value) > 0)
    )


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def safe_relative_path(path: Any) -> bool:
    """True if ``path`` is a non-empty relative path without ``..``."""
    if not isinstance(path, str) or not path.strip():
        return False
    if path.startswith("/") or path.startswith("~") or "\\" in path or "\0" in path:
        return False
    return ".." not in path.split("/")


def _validate_check(check: Any, where: str, errors: List[str]) -> None:
    if not isinstance(check, dict):
        errors.append("%s: check must be an object" % where)
        return
    kind = check.get("type")
    if kind not in checks.CHECK_TYPES:
        errors.append("%s: unknown check type %r" % (where, kind))
        return
    for param in checks.REQUIRED_PARAMS[kind]:
        if param not in check:
            errors.append("%s: check %r needs %r" % (where, kind, param))
    allowed = set(checks.REQUIRED_PARAMS[kind]) | {"type"}
    if kind == "output_contains":
        allowed.add("stream")
        if check.get("stream", "stdout") not in checks.STREAMS:
            errors.append("%s: stream must be one of %s" % (where, ", ".join(checks.STREAMS)))
    for key in check:
        if key not in allowed:
            errors.append("%s: unknown field %r in %r check" % (where, key, kind))
    if kind == "command_matches" and "pattern" in check:
        if not isinstance(check["pattern"], str):
            errors.append("%s: pattern must be a string" % where)
        else:
            try:
                re.compile(check["pattern"])
            except re.error as exc:
                errors.append("%s: bad regex %r: %s" % (where, check["pattern"], exc))
    if "text" in check and not isinstance(check["text"], str):
        errors.append("%s: text must be a string" % where)
    if "path" in check:
        if kind == "cwd_is" and check["path"] == ".":
            pass
        elif not safe_relative_path(check["path"]):
            errors.append("%s: path %r must be relative, without '..'" % (where, check["path"]))
    if kind == "file_mode" and "mode" in check:
        if not isinstance(check["mode"], str) or not MODE_PATTERN.match(check["mode"]):
            errors.append("%s: mode must be 3 octal digits like \"644\"" % where)
    if kind == "all" and "checks" in check:
        if not isinstance(check["checks"], list) or not check["checks"]:
            errors.append("%s: 'all' needs a non-empty list of checks" % where)
        else:
            for i, sub in enumerate(check["checks"]):
                _validate_check(sub, "%s.checks[%d]" % (where, i), errors)


def validate_lesson(data: Any, filename: str) -> List[str]:
    """Return a list of problems with a lesson (empty list = valid)."""
    errors: List[str] = []
    name = os.path.basename(filename)
    if not isinstance(data, dict):
        return ["%s: the lesson must be a JSON object" % name]

    def need(field: str) -> bool:
        if field not in data:
            errors.append("%s: missing field %r" % (name, field))
            return False
        return True

    for key in data:
        if key not in TOP_FIELDS:
            errors.append("%s: unknown field %r" % (name, key))

    if need("format_version") and data["format_version"] != FORMAT_VERSION:
        errors.append("%s: format_version must be %d" % (name, FORMAT_VERSION))
    if need("id"):
        lid = data["id"]
        if not isinstance(lid, str) or not ID_PATTERN.match(lid):
            errors.append("%s: id %r must look like '01-first-steps'" % (name, lid))
        elif name.endswith(".json") and name[:-5] != lid:
            errors.append("%s: id %r must match the file name" % (name, lid))
    for field in ("title", "summary", "intro"):
        if need(field) and (not isinstance(data[field], str) or not data[field].strip()):
            errors.append("%s: %r must be a non-empty string" % (name, field))
    if need("level") and (not _is_int(data["level"]) or not 1 <= data["level"] <= 5):
        errors.append("%s: level must be a whole number from 1 to 5" % name)
    if "minutes" in data and (not _is_int(data["minutes"]) or data["minutes"] < 1):
        errors.append("%s: minutes must be a positive whole number" % name)
    if "outro" in data and not isinstance(data["outro"], str):
        errors.append("%s: outro must be a string" % name)
    if "requires" in data and not _is_str_list(data["requires"]):
        errors.append("%s: requires must be a list of strings" % name)

    if need("setup"):
        if not isinstance(data["setup"], list):
            errors.append("%s: setup must be a list" % name)
        else:
            for i, entry in enumerate(data["setup"]):
                where = "%s: setup[%d]" % (name, i)
                if not isinstance(entry, dict):
                    errors.append("%s must be an object" % where)
                    continue
                for key in entry:
                    if key not in SETUP_FIELDS:
                        errors.append("%s: unknown field %r" % (where, key))
                if not safe_relative_path(entry.get("path")):
                    errors.append("%s: path %r must be relative, without '..'"
                                  % (where, entry.get("path")))
                if "content" in entry and not isinstance(entry["content"], str):
                    errors.append("%s: content must be a string" % where)
                if "dir" in entry and not isinstance(entry["dir"], bool):
                    errors.append("%s: dir must be true or false" % where)
                if "mode" in entry and (not isinstance(entry["mode"], str)
                                        or not MODE_PATTERN.match(entry["mode"])):
                    errors.append("%s: mode must be 3 octal digits like \"644\"" % where)

    if need("steps"):
        if not isinstance(data["steps"], list) or not data["steps"]:
            errors.append("%s: steps must be a non-empty list" % name)
        else:
            for i, step in enumerate(data["steps"]):
                where = "%s: step %d" % (name, i + 1)
                if not isinstance(step, dict):
                    errors.append("%s must be an object" % where)
                    continue
                for key in step:
                    if key not in STEP_FIELDS:
                        errors.append("%s: unknown field %r" % (where, key))
                for field in ("instruction", "explain"):
                    if not isinstance(step.get(field), str) or not step[field].strip():
                        errors.append("%s: %r must be a non-empty string" % (where, field))
                if not _is_str_list(step.get("hints"), allow_empty=False):
                    errors.append("%s: hints must be a list with at least one string" % where)
                if "check" not in step:
                    errors.append("%s: missing check" % where)
                else:
                    _validate_check(step["check"], where, errors)
                if "solution" in step and not isinstance(step["solution"], str):
                    errors.append("%s: solution must be a string" % where)
                if "requires" in step and not _is_str_list(step["requires"]):
                    errors.append("%s: requires must be a list of strings" % where)
                if "optional" in step and not isinstance(step["optional"], bool):
                    errors.append("%s: optional must be true or false" % where)
    return errors


# ----- loading ---------------------------------------------------------------

def load_lesson_file(path: str) -> Tuple[Optional[Lesson], List[str]]:
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError) as exc:
        return None, ["%s: cannot read JSON: %s" % (os.path.basename(path), exc)]
    errors = validate_lesson(data, path)
    return (None, errors) if errors else (data, [])


def load_lessons(directory: Optional[str] = None) -> Tuple[List[Lesson], List[str]]:
    """Load every valid ``*.json`` lesson, sorted by id. Also return problems."""
    directory = directory or LESSONS_DIR
    lessons: List[Lesson] = []
    problems: List[str] = []
    try:
        names = sorted(n for n in os.listdir(directory) if n.endswith(".json"))
    except OSError as exc:
        return [], ["cannot open lessons folder: %s" % exc]
    seen = set()
    for name in names:
        lesson, errors = load_lesson_file(os.path.join(directory, name))
        problems.extend(errors)
        if lesson is not None:
            if lesson["id"] in seen:
                problems.append("%s: duplicate id %r" % (name, lesson["id"]))
                continue
            seen.add(lesson["id"])
            lessons.append(lesson)
    lessons.sort(key=lambda l: l["id"])
    return lessons, problems


def lesson_number(lesson: Lesson) -> int:
    """The number shown in menus, from the id prefix ("03-..." -> 3)."""
    return int(lesson["id"][:2])


def find_lesson(lessons: List[Lesson], key: str) -> Optional[Lesson]:
    """Find a lesson by number ("3", "03") or id ("03-files-and-folders")."""
    key = key.strip()
    for lesson in lessons:
        if lesson["id"] == key:
            return lesson
    if key.isdigit():
        for lesson in lessons:
            if lesson_number(lesson) == int(key):
                return lesson
    for lesson in lessons:  # "03-files" or "files-and-folders"
        if lesson["id"].startswith(key) or lesson["id"][3:] == key:
            return lesson
    return None


def missing_tools(names: Optional[List[str]]) -> List[str]:
    return [n for n in (names or []) if shutil.which(n) is None]


def lesson_missing_tools(lesson: Lesson) -> List[str]:
    """Tools the lesson (or one of its steps) needs that are not installed."""
    wanted = list(lesson.get("requires", []))
    for step in lesson["steps"]:
        wanted.extend(step.get("requires", []))
    seen: List[str] = []
    for name in missing_tools(wanted):
        if name not in seen:
            seen.append(name)
    return seen


# ----- sandbox ---------------------------------------------------------------

def force_rmtree(path: str) -> None:
    """Delete a folder, even if the student removed permissions inside it."""
    if not os.path.lexists(path):
        return
    if os.path.islink(path) or not os.path.isdir(path):
        os.remove(path)
        return

    def onerror(func, p, _exc):
        # Make the parent writable, then try once more.
        try:
            os.chmod(os.path.dirname(p), stat.S_IRWXU)
            func(p)
        except OSError:
            pass

    # Make sure we can enter and change every folder first.
    try:
        os.chmod(path, stat.S_IRWXU)
    except OSError:
        pass
    for root, dirs, _files in os.walk(path):
        for d in dirs:
            full = os.path.join(root, d)
            if not os.path.islink(full):
                try:
                    os.chmod(full, stat.S_IRWXU)
                except OSError:
                    pass
    if sys.version_info >= (3, 12):
        shutil.rmtree(path, onexc=onerror)  # `onerror` is deprecated there
    else:
        shutil.rmtree(path, onerror=onerror)


def setup_sandbox(lesson: Lesson, sandbox: str) -> None:
    """Delete ``sandbox`` and create it again from the lesson's ``setup``."""
    sandbox = os.path.abspath(sandbox)
    if os.path.basename(sandbox) != lesson["id"]:
        # Safety net: never delete a folder that is not a lesson sandbox.
        raise ValueError("refusing to reset unexpected folder %r" % sandbox)
    force_rmtree(sandbox)
    os.makedirs(sandbox)
    os.chmod(sandbox, 0o755)
    for entry in lesson["setup"]:
        rel = entry["path"].strip("/")
        if not safe_relative_path(rel):
            raise ValueError("unsafe setup path %r" % entry["path"])
        target = os.path.join(sandbox, rel)
        parent = os.path.dirname(target)
        if not os.path.isdir(parent):
            os.makedirs(parent)
            # Parents get 755 explicitly, so the umask does not matter.
            p = parent
            while os.path.abspath(p) != sandbox:
                os.chmod(p, 0o755)
                p = os.path.dirname(p)
        if entry.get("dir"):
            os.makedirs(target, exist_ok=True)
            mode = entry.get("mode", "755")
        else:
            with open(target, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(entry.get("content", ""))
            mode = entry.get("mode", "644")
        os.chmod(target, int(mode, 8))


# ----- self-test (LESSONS_PLAN 2.10) -------------------------------------------

def run_solution_check(
    lesson: Lesson, workdir: Optional[str] = None, timeout: float = 10.0
) -> Tuple[List[str], List[str]]:
    """Play a lesson with its solutions. Return (problems, skipped_steps).

    For every step: the check must FAIL before the solution runs, and PASS
    after. Steps whose ``requires`` tools are missing are skipped. Steps
    without a solution are reported as problems.
    """
    problems: List[str] = []
    skipped: List[str] = []
    own_tmp = workdir is None
    base = tempfile.mkdtemp(prefix="ta-test-") if own_tmp else workdir
    try:
        sandbox = os.path.join(base, "sandbox", lesson["id"])
        os.makedirs(os.path.dirname(sandbox), exist_ok=True)
        setup_sandbox(lesson, sandbox)
        state = os.path.join(base, "state", lesson["id"])
        force_rmtree(state)
        sh = Shell(sandbox, state, timeout=timeout, use_tty=False)
        ctx = checks.Context(sandbox=sh.sandbox, cwd=sh.cwd)
        try:
            for i, step in enumerate(lesson["steps"], start=1):
                label = "%s step %d" % (lesson["id"], i)
                missing = missing_tools(step.get("requires"))
                if missing:
                    skipped.append("%s (missing: %s)" % (label, ", ".join(missing)))
                    continue
                solution = step.get("solution")
                if not solution:
                    problems.append("%s: no solution to test" % label)
                    continue
                if checks.evaluate(step["check"], ctx):
                    problems.append("%s: check already passes before the solution" % label)
                for line in solution.split("\n"):
                    if not line.strip():
                        continue
                    result = sh.run(line)
                    ctx = checks.Context(
                        sandbox=sh.sandbox,
                        cwd=result.cwd,
                        command=line,
                        stdout=result.stdout,
                        stderr=result.stderr,
                    )
                if not checks.evaluate(step["check"], ctx):
                    problems.append(
                        "%s: check does not pass after the solution "
                        "(stdout=%r, stderr=%r)" % (label, ctx.stdout[-200:], ctx.stderr[-200:])
                    )
        finally:
            sh.cleanup()
    finally:
        if own_tmp:
            force_rmtree(base)
    return problems, skipped
