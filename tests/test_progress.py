"""Saved progress (LESSONS_PLAN.md, section 2.8)."""

import datetime
import json
import os
import shutil
import sys
import tempfile
import unittest
from unittest import mock

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from terminal_academy import progress as progress_mod  # noqa: E402
from terminal_academy.progress import Progress  # noqa: E402


class ProgressTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="ta-progress-")
        self.path = os.path.join(self.tmp, "progress.json")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_new_file_is_empty(self):
        p = Progress(self.path)
        self.assertFalse(p.recovered_from_broken)
        self.assertEqual(p.status("01-first-steps"), "not_started")
        self.assertFalse(os.path.exists(self.path))  # nothing written yet

    def test_round_trip(self):
        p = Progress(self.path)
        p.start("01-first-steps")
        p.set_step("01-first-steps", 2)
        p.add_hint("01-first-steps")
        p.add_hint("01-first-steps")
        p.add_skipped("01-first-steps", 1)
        p.add_skipped("01-first-steps", 1)  # counted once
        p.start("03-files-and-folders")
        p.finish("03-files-and-folders", 6, now=datetime.datetime(2026, 10, 11, 15, 20, 0, 123))

        q = Progress(self.path)
        self.assertEqual(q.data, p.data)
        first = q.entry("01-first-steps")
        self.assertEqual(first["status"], "in_progress")
        self.assertEqual(first["step"], 2)
        self.assertEqual(first["hints_used"], 2)
        self.assertEqual(first["skipped"], [1])
        third = q.entry("03-files-and-folders")
        self.assertEqual(third["status"], "done")
        self.assertEqual(third["step"], 6)
        self.assertEqual(third["finished_at"], "2026-10-11T15:20:00")

        with open(self.path, encoding="utf-8") as fh:
            raw = json.load(fh)
        self.assertEqual(raw["version"], 1)
        self.assertIn("01-first-steps", raw["lessons"])

    def test_replaying_a_done_lesson_stays_done(self):
        p = Progress(self.path)
        p.start("01-first-steps")
        p.finish("01-first-steps", 5)
        p.start("01-first-steps")
        self.assertEqual(Progress(self.path).status("01-first-steps"), "done")

    def test_reset(self):
        p = Progress(self.path)
        p.start("01-first-steps")
        p.start("03-files-and-folders")
        p.reset("01-first-steps")
        q = Progress(self.path)
        self.assertEqual(q.status("01-first-steps"), "not_started")
        self.assertEqual(q.status("03-files-and-folders"), "in_progress")
        q.reset()
        self.assertEqual(Progress(self.path).data["lessons"], {})

    def test_save_is_atomic_and_leaves_no_temp_files(self):
        p = Progress(self.path)
        for i in range(5):
            p.set_step("01-first-steps", i)
        self.assertEqual(os.listdir(self.tmp), ["progress.json"])

    def test_failed_write_keeps_old_file(self):
        p = Progress(self.path)
        p.start("01-first-steps")
        with open(self.path, encoding="utf-8") as fh:
            before = fh.read()

        def broken_dump(*_args, **_kwargs):
            raise OSError("disk full")

        with mock.patch.object(progress_mod.json, "dump", broken_dump):
            with self.assertRaises(OSError):
                p.set_step("01-first-steps", 3)
        with open(self.path, encoding="utf-8") as fh:
            self.assertEqual(fh.read(), before)
        self.assertEqual(os.listdir(self.tmp), ["progress.json"])

    def test_broken_file_is_backed_up(self):
        with open(self.path, "w", encoding="utf-8") as fh:
            fh.write("{ this is not json")
        p = Progress(self.path)
        self.assertTrue(p.recovered_from_broken)
        self.assertEqual(p.data, {"version": 1, "lessons": {}})
        with open(self.path + ".bak", encoding="utf-8") as fh:
            self.assertEqual(fh.read(), "{ this is not json")
        # The fresh file is valid, so the warning shows only once.
        q = Progress(self.path)
        self.assertFalse(q.recovered_from_broken)

    def test_wrong_structure_is_treated_as_broken(self):
        for content in ('[]', '{"version": 99, "lessons": {}}',
                        '{"version": 1, "lessons": []}',
                        '{"version": 1, "lessons": {"01-first-steps": {"status": "??"}}}'):
            with self.subTest(content=content):
                with open(self.path, "w", encoding="utf-8") as fh:
                    fh.write(content)
                p = Progress(self.path)
                self.assertTrue(p.recovered_from_broken)
                self.assertTrue(os.path.exists(self.path + ".bak"))
                self.assertEqual(p.data["lessons"], {})


if __name__ == "__main__":
    unittest.main()
