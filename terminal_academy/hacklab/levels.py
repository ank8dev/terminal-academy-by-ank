"""Load and validate Part 2 levels (the ethical-hacking lab).

A level is a folder under ``hacklab/levels/`` that holds:

- ``level.json``  — the level definition (story, objective, hints, which
  containers to build, where the flag goes, what the diagram watches).
- one or more ``Dockerfile.*`` — the container images.
- ``LEARN.md`` — the concept, the commands, and how defenders prevent the
  attack. Shown with ``academy hack learn <n>``.

This mirrors ``terminal_academy/lessons.py`` (Part 1): a strict validator so a
broken level fails loudly with a clear message instead of half-working.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

FORMAT_VERSION = 1
LEVELS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "levels")
ID_PATTERN = re.compile(r"^[0-9]{2}-[a-z0-9-]+$")
MODE_PATTERN = re.compile(r"^[0-7]{3}$")

DIAGRAM_TYPES = ("filesystem", "permissions", "network")
ROLES = ("player", "target")

TOP_FIELDS = {
    "format_version", "id", "title", "number", "summary", "story", "objective",
    "diagram", "hints", "containers", "flag_placements", "diagram_watch",
}
CONTAINER_FIELDS = {"name", "role", "dockerfile"}
PLACEMENT_FIELDS = {"container", "path", "mode", "owner"}
WATCH_FIELDS = {"root", "paths", "target", "port"}


@dataclass
class Container:
    name: str
    role: str
    dockerfile: str


@dataclass
class Level:
    id: str
    title: str
    number: int
    summary: str
    story: str
    objective: str
    diagram: str
    hints: List[str]
    containers: List[Container]
    flag_placements: List[Dict[str, Any]]
    diagram_watch: Dict[str, Any]
    directory: str = ""
    raw: Dict[str, Any] = field(default_factory=dict)

    def container(self, role: str) -> Optional[Container]:
        for c in self.containers:
            if c.role == role:
                return c
        return None

    @property
    def player(self) -> Container:
        c = self.container("player")
        assert c is not None  # the validator guarantees exactly one player
        return c

    @property
    def target(self) -> Optional[Container]:
        return self.container("target")

    @property
    def learn_path(self) -> str:
        return os.path.join(self.directory, "LEARN.md")


# ----- validation ------------------------------------------------------------

def _is_str(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _abs_path_ok(path: Any) -> bool:
    """Flag paths live inside the container, so they must be absolute and tidy."""
    return (
        isinstance(path, str)
        and path.startswith("/")
        and ".." not in path.split("/")
        and "\0" not in path
    )


def validate_level(data: Any, filename: str, directory: Optional[str] = None) -> List[str]:
    """Return a list of problems with a level (empty list = valid)."""
    errors: List[str] = []
    name = os.path.basename(os.path.dirname(filename)) or filename

    if not isinstance(data, dict):
        return ["%s: level.json must be a JSON object" % name]

    for key in data:
        if key not in TOP_FIELDS:
            errors.append("%s: unknown field %r" % (name, key))

    if data.get("format_version") != FORMAT_VERSION:
        errors.append("%s: format_version must be %d" % (name, FORMAT_VERSION))

    lid = data.get("id")
    if not isinstance(lid, str) or not ID_PATTERN.match(lid):
        errors.append("%s: id %r must look like '01-hidden-in-plain-sight'" % (name, lid))
    elif directory and os.path.basename(directory) != lid:
        errors.append("%s: id %r must match the folder name" % (name, lid))

    for strfield in ("title", "summary", "story", "objective"):
        if not _is_str(data.get(strfield)):
            errors.append("%s: %r must be a non-empty string" % (name, strfield))

    number = data.get("number")
    if not isinstance(number, int) or isinstance(number, bool) or number < 1:
        errors.append("%s: number must be a positive whole number" % name)

    if data.get("diagram") not in DIAGRAM_TYPES:
        errors.append("%s: diagram must be one of %s" % (name, ", ".join(DIAGRAM_TYPES)))

    hints = data.get("hints")
    if not isinstance(hints, list) or not hints or not all(_is_str(h) for h in hints):
        errors.append("%s: hints must be a non-empty list of strings" % name)

    _validate_containers(data, name, errors)
    _validate_placements(data, name, errors)

    if "diagram_watch" in data:
        watch = data["diagram_watch"]
        if not isinstance(watch, dict):
            errors.append("%s: diagram_watch must be an object" % name)
        else:
            for key in watch:
                if key not in WATCH_FIELDS:
                    errors.append("%s: unknown diagram_watch field %r" % (name, key))

    if directory and not os.path.isfile(os.path.join(directory, "LEARN.md")):
        errors.append("%s: missing LEARN.md" % name)

    return errors


def _validate_containers(data: dict, name: str, errors: List[str]) -> None:
    containers = data.get("containers")
    if not isinstance(containers, list) or not containers:
        errors.append("%s: containers must be a non-empty list" % name)
        return
    roles: List[str] = []
    names: List[str] = []
    for i, c in enumerate(containers):
        where = "%s: container[%d]" % (name, i)
        if not isinstance(c, dict):
            errors.append("%s must be an object" % where)
            continue
        for key in c:
            if key not in CONTAINER_FIELDS:
                errors.append("%s: unknown field %r" % (where, key))
        if not _is_str(c.get("name")):
            errors.append("%s: name must be a non-empty string" % where)
        else:
            names.append(c["name"])
        if c.get("role") not in ROLES:
            errors.append("%s: role must be one of %s" % (where, ", ".join(ROLES)))
        else:
            roles.append(c["role"])
        if not _is_str(c.get("dockerfile")):
            errors.append("%s: dockerfile must be a non-empty string" % where)
    if roles.count("player") != 1:
        errors.append("%s: there must be exactly one 'player' container" % name)
    if len(set(names)) != len(names):
        errors.append("%s: container names must be unique" % name)


def _validate_placements(data: dict, name: str, errors: List[str]) -> None:
    placements = data.get("flag_placements")
    if not isinstance(placements, list) or not placements:
        errors.append("%s: flag_placements must be a non-empty list" % name)
        return
    container_names = {
        c.get("name") for c in data.get("containers", []) if isinstance(c, dict)
    }
    for i, p in enumerate(placements):
        where = "%s: flag_placements[%d]" % (name, i)
        if not isinstance(p, dict):
            errors.append("%s must be an object" % where)
            continue
        for key in p:
            if key not in PLACEMENT_FIELDS:
                errors.append("%s: unknown field %r" % (where, key))
        if p.get("container") not in container_names:
            errors.append("%s: container %r is not one of this level's containers"
                          % (where, p.get("container")))
        if not _abs_path_ok(p.get("path")):
            errors.append("%s: path %r must be an absolute path without '..'"
                          % (where, p.get("path")))
        if "mode" in p and (not isinstance(p["mode"], str)
                            or not MODE_PATTERN.match(p["mode"])):
            errors.append("%s: mode must be 3 octal digits like \"644\"" % where)
        if "owner" in p and not _is_str(p["owner"]):
            errors.append("%s: owner must be a non-empty string" % where)


# ----- loading ---------------------------------------------------------------

def _to_level(data: dict, directory: str) -> Level:
    containers = [
        Container(name=c["name"], role=c["role"], dockerfile=c["dockerfile"])
        for c in data["containers"]
    ]
    return Level(
        id=data["id"],
        title=data["title"],
        number=int(data["number"]),
        summary=data["summary"],
        story=data["story"],
        objective=data["objective"],
        diagram=data["diagram"],
        hints=list(data["hints"]),
        containers=containers,
        flag_placements=list(data["flag_placements"]),
        diagram_watch=dict(data.get("diagram_watch", {})),
        directory=directory,
        raw=data,
    )


def load_level_dir(directory: str) -> Tuple[Optional[Level], List[str]]:
    path = os.path.join(directory, "level.json")
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError) as exc:
        return None, ["%s: cannot read level.json: %s" % (os.path.basename(directory), exc)]
    errors = validate_level(data, path, directory=directory)
    if errors:
        return None, errors
    return _to_level(data, directory), []


def load_levels(directory: Optional[str] = None) -> Tuple[List[Level], List[str]]:
    """Load every valid level, sorted by id. Also return a list of problems."""
    directory = directory or LEVELS_DIR
    levels: List[Level] = []
    problems: List[str] = []
    try:
        names = sorted(
            n for n in os.listdir(directory)
            if os.path.isdir(os.path.join(directory, n)) and not n.startswith(".")
        )
    except OSError as exc:
        return [], ["cannot open levels folder: %s" % exc]
    seen = set()
    for name in names:
        level, errors = load_level_dir(os.path.join(directory, name))
        problems.extend(errors)
        if level is not None:
            if level.id in seen:
                problems.append("%s: duplicate id %r" % (name, level.id))
                continue
            seen.add(level.id)
            levels.append(level)
    levels.sort(key=lambda l: l.id)
    return levels, problems


def find_level(levels: List[Level], key: str) -> Optional[Level]:
    """Find a level by number ("1"), id, or id without the number prefix."""
    key = key.strip()
    for level in levels:
        if level.id == key:
            return level
    if key.isdigit():
        for level in levels:
            if level.number == int(key):
                return level
    for level in levels:
        if level.id.startswith(key) or level.id[3:] == key:
            return level
    return None
