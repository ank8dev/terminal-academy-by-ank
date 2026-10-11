"""Every lesson file is valid and can be solved with its own solutions.

The tests look at every ``*.json`` file in ``terminal_academy/lessons/``, so
new lessons are tested automatically (LESSONS_PLAN.md, section 2.10).
"""

import json
import os
import sys
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from terminal_academy import lessons  # noqa: E402


def lesson_files():
    return sorted(
        os.path.join(lessons.LESSONS_DIR, name)
        for name in os.listdir(lessons.LESSONS_DIR)
        if name.endswith(".json")
    )


class LessonFilesTest(unittest.TestCase):
    def test_there_are_lessons(self):
        self.assertTrue(lesson_files(), "no lesson files found")

    def test_only_json_files_in_lessons_folder(self):
        for name in os.listdir(lessons.LESSONS_DIR):
            with self.subTest(name=name):
                self.assertTrue(name.endswith(".json"), "unexpected file in lessons/")

    def test_every_lesson_validates(self):
        for path in lesson_files():
            name = os.path.basename(path)
            with self.subTest(lesson=name):
                with open(path, encoding="utf-8") as fh:
                    data = json.load(fh)  # fails loudly on bad JSON
                self.assertEqual(lessons.validate_lesson(data, path), [])
                self.assertEqual(data["id"], name[:-len(".json")])

    def test_ids_are_unique(self):
        ids = []
        for path in lesson_files():
            with open(path, encoding="utf-8") as fh:
                ids.append(json.load(fh).get("id"))
        self.assertEqual(len(ids), len(set(ids)), "duplicate lesson ids: %r" % ids)
        numbers = [i[:2] for i in ids]
        self.assertEqual(len(numbers), len(set(numbers)), "duplicate lesson numbers")

    def test_load_lessons_reports_no_problems(self):
        loaded, problems = lessons.load_lessons()
        self.assertEqual(problems, [])
        self.assertEqual(len(loaded), len(lesson_files()))
        self.assertEqual([l["id"] for l in loaded], sorted(l["id"] for l in loaded))

    def test_every_step_has_a_solution(self):
        for path in lesson_files():
            lesson, _ = lessons.load_lesson_file(path)
            for i, step in enumerate(lesson["steps"], start=1):
                with self.subTest(lesson=lesson["id"], step=i):
                    self.assertTrue((step.get("solution") or "").strip())


class LessonSolutionsTest(unittest.TestCase):
    """For every step: the check fails before the solution and passes after."""

    def test_solutions_pass(self):
        for path in lesson_files():
            name = os.path.basename(path)
            with self.subTest(lesson=name):
                lesson, errors = lessons.load_lesson_file(path)
                self.assertEqual(errors, [])
                problems, skipped = lessons.run_solution_check(lesson)
                self.assertEqual(problems, [])
                for note in skipped:
                    sys.stderr.write("\n  skipped (tool missing): %s " % note)


if __name__ == "__main__":
    unittest.main()
