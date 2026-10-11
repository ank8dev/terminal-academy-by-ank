"""Saved progress in ``~/.terminal-academy/progress.json`` (LESSONS_PLAN 2.8).

The file is written atomically (temp file + ``os.replace``), so a crash in
the middle of a write never leaves a half-written file. A broken file is kept
as ``progress.json.bak`` and we start fresh.
"""

from __future__ import annotations

import datetime
import json
import os
import shutil
import tempfile
from typing import Any, Dict, Optional

VERSION = 1
STATUSES = ("not_started", "in_progress", "done")


def _fresh_entry() -> Dict[str, Any]:
    return {"status": "not_started", "step": 0, "hints_used": 0, "skipped": []}


class Progress:
    def __init__(self, path: str) -> None:
        self.path = path
        self.data: Dict[str, Any] = {"version": VERSION, "lessons": {}}
        self.recovered_from_broken = False
        self.load()

    # ----- file -----------------------------------------------------------

    def load(self) -> None:
        if not os.path.exists(self.path):
            return
        try:
            with open(self.path, encoding="utf-8") as fh:
                data = json.load(fh)
            if (
                not isinstance(data, dict)
                or data.get("version") != VERSION
                or not isinstance(data.get("lessons"), dict)
            ):
                raise ValueError("unexpected structure")
            for entry in data["lessons"].values():
                if not isinstance(entry, dict) or entry.get("status") not in STATUSES:
                    raise ValueError("unexpected lesson entry")
        except (OSError, ValueError):
            try:
                shutil.copyfile(self.path, self.path + ".bak")
            except OSError:
                pass
            self.recovered_from_broken = True
            self.data = {"version": VERSION, "lessons": {}}
            try:
                self.save()  # so the warning is shown only once
            except OSError:
                pass
            return
        self.data = data

    def save(self) -> None:
        folder = os.path.dirname(os.path.abspath(self.path))
        os.makedirs(folder, exist_ok=True)
        fd, tmp = tempfile.mkstemp(prefix=".progress-", suffix=".tmp", dir=folder)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                json.dump(self.data, fh, indent=2, sort_keys=True)
                fh.write("\n")
                fh.flush()
                os.fsync(fh.fileno())
            os.replace(tmp, self.path)
        except BaseException:
            try:
                os.remove(tmp)
            except OSError:
                pass
            raise

    # ----- lessons --------------------------------------------------------

    def entry(self, lesson_id: str) -> Dict[str, Any]:
        """The saved entry (a fresh one if the lesson was never started)."""
        entry = self.data["lessons"].get(lesson_id)
        if entry is None:
            return _fresh_entry()
        merged = _fresh_entry()
        merged.update(entry)
        return merged

    def _set(self, lesson_id: str, entry: Dict[str, Any]) -> None:
        self.data["lessons"][lesson_id] = entry
        self.save()

    def status(self, lesson_id: str) -> str:
        return self.entry(lesson_id)["status"]

    def start(self, lesson_id: str) -> None:
        """Begin (or restart) a lesson at step 0.

        Playing a finished lesson again keeps it marked as done.
        """
        old = self.entry(lesson_id)
        entry = _fresh_entry()
        entry["status"] = "in_progress"
        if old["status"] == "done":
            entry["status"] = "done"
            if "finished_at" in old:
                entry["finished_at"] = old["finished_at"]
        self._set(lesson_id, entry)

    def set_step(self, lesson_id: str, step: int) -> None:
        entry = self.entry(lesson_id)
        entry["step"] = step
        if entry["status"] != "done":
            entry["status"] = "in_progress"
        self._set(lesson_id, entry)

    def add_hint(self, lesson_id: str) -> None:
        entry = self.entry(lesson_id)
        entry["hints_used"] = int(entry.get("hints_used", 0)) + 1
        self._set(lesson_id, entry)

    def add_skipped(self, lesson_id: str, step: int) -> None:
        entry = self.entry(lesson_id)
        skipped = list(entry.get("skipped", []))
        if step not in skipped:
            skipped.append(step)
        entry["skipped"] = sorted(skipped)
        self._set(lesson_id, entry)

    def finish(self, lesson_id: str, steps: int, now: Optional[datetime.datetime] = None) -> None:
        entry = self.entry(lesson_id)
        entry["status"] = "done"
        entry["step"] = steps
        entry["finished_at"] = (now or datetime.datetime.now()).replace(microsecond=0).isoformat()
        self._set(lesson_id, entry)

    def reset(self, lesson_id: Optional[str] = None) -> None:
        """Forget one lesson, or everything when ``lesson_id`` is None."""
        if lesson_id is None:
            self.data["lessons"] = {}
        else:
            self.data["lessons"].pop(lesson_id, None)
        self.save()
