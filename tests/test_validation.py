"""Lesson validation catches broken lessons (LESSONS_PLAN.md, sections 2.2-2.5)."""

import copy
import json
import os
import shutil
import sys
import tempfile
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from terminal_academy import lessons  # noqa: E402

GOOD = {
    "format_version": 1,
    "id": "99-test-lesson",
    "title": "Test",
    "level": 1,
    "minutes": 3,
    "summary": "A lesson for tests.",
    "intro": "Hello.",
    "outro": "Bye.",
    "setup": [
        {"path": "a.txt", "content": "hi\n"},
        {"path": "box", "dir": True, "mode": "700"},
    ],
    "steps": [
        {
            "instruction": "Make a folder called x.",
            "hints": ["Type: mkdir x"],
            "check": {"type": "dir_exists", "path": "x"},
            "explain": "mkdir makes folders.",
            "solution": "mkdir x",
        },
        {
            "instruction": "List files.",
            "hints": ["Type: ls"],
            "check": {"type": "all", "checks": [
                {"type": "command_matches", "pattern": "^ls\\b"},
                {"type": "output_contains", "text": "a.txt", "stream": "both"},
            ]},
            "explain": "ls lists files.",
            "solution": "ls",
        },
    ],
}
NAME = "99-test-lesson.json"


def errors_for(lesson, name=NAME):
    return lessons.validate_lesson(lesson, name)


class ValidationTest(unittest.TestCase):
    def mutate(self, func):
        lesson = copy.deepcopy(GOOD)
        func(lesson)
        return errors_for(lesson)

    def assertInvalid(self, func, fragment):
        errs = self.mutate(func)
        self.assertTrue(errs, "expected an error")
        self.assertTrue(any(fragment in e for e in errs),
                        "no error mentions %r: %r" % (fragment, errs))

    def test_good_lesson_is_valid(self):
        self.assertEqual(errors_for(copy.deepcopy(GOOD)), [])

    def test_not_an_object(self):
        self.assertTrue(errors_for([]))

    def test_missing_fields(self):
        for field in ("format_version", "id", "title", "level", "summary", "intro",
                      "setup", "steps"):
            with self.subTest(field=field):
                self.assertInvalid(lambda l: l.pop(field), field)

    def test_missing_step_fields(self):
        for field in ("instruction", "hints", "check", "explain"):
            with self.subTest(field=field):
                self.assertInvalid(lambda l: l["steps"][0].pop(field), field)

    def test_unknown_field(self):
        self.assertInvalid(lambda l: l.update(colour="red"), "colour")

    def test_bad_ids(self):
        for bad in ("first-steps", "1-first", "01_first", "01-First", "", 1):
            with self.subTest(id=bad):
                lesson = copy.deepcopy(GOOD)
                lesson["id"] = bad
                self.assertTrue(errors_for(lesson))

    def test_id_must_match_file_name(self):
        errs = errors_for(copy.deepcopy(GOOD), "98-other.json")
        self.assertTrue(any("file name" in e for e in errs), errs)

    def test_bad_values(self):
        self.assertInvalid(lambda l: l.update(format_version=2), "format_version")
        self.assertInvalid(lambda l: l.update(level=6), "level")
        self.assertInvalid(lambda l: l.update(level=True), "level")
        self.assertInvalid(lambda l: l.update(minutes=0), "minutes")
        self.assertInvalid(lambda l: l.update(title="  "), "title")
        self.assertInvalid(lambda l: l.update(steps=[]), "steps")
        self.assertInvalid(lambda l: l["steps"][0].update(hints=[]), "hints")
        self.assertInvalid(lambda l: l["steps"][0].update(optional="yes"), "optional")

    def test_bad_check_type(self):
        self.assertInvalid(
            lambda l: l["steps"][0].update(check={"type": "file_is_cool", "path": "x"}),
            "unknown check type")

    def test_check_missing_param(self):
        self.assertInvalid(lambda l: l["steps"][0].update(check={"type": "file_exists"}),
                           "path")

    def test_bad_check_inside_all(self):
        def change(l):
            l["steps"][1]["check"]["checks"].append({"type": "nope"})
        self.assertInvalid(change, "checks[2]")

    def test_empty_all(self):
        self.assertInvalid(lambda l: l["steps"][0].update(check={"type": "all", "checks": []}),
                           "non-empty")

    def test_bad_stream(self):
        self.assertInvalid(lambda l: l["steps"][0].update(
            check={"type": "output_contains", "text": "x", "stream": "screen"}), "stream")

    def test_bad_mode(self):
        self.assertInvalid(lambda l: l["steps"][0].update(
            check={"type": "file_mode", "path": "a.txt", "mode": "999"}), "mode")
        self.assertInvalid(lambda l: l["setup"][0].update(mode="rwx"), "mode")

    def test_absolute_setup_path(self):
        self.assertInvalid(lambda l: l["setup"][0].update(path="/etc/passwd"), "relative")

    def test_dotdot_setup_path(self):
        self.assertInvalid(lambda l: l["setup"][0].update(path="../escape.txt"), "relative")
        self.assertInvalid(lambda l: l["setup"][0].update(path="a/../../b"), "relative")

    def test_home_setup_path(self):
        self.assertInvalid(lambda l: l["setup"][0].update(path="~/x"), "relative")

    def test_bad_check_path(self):
        self.assertInvalid(lambda l: l["steps"][0].update(
            check={"type": "file_exists", "path": "/etc/hosts"}), "relative")
        self.assertInvalid(lambda l: l["steps"][0].update(
            check={"type": "cwd_is", "path": ".."}), "relative")

    def test_cwd_is_dot_is_allowed(self):
        lesson = copy.deepcopy(GOOD)
        lesson["steps"][0]["check"] = {"type": "cwd_is", "path": "."}
        self.assertEqual(errors_for(lesson), [])

    def test_bad_regex(self):
        self.assertInvalid(lambda l: l["steps"][0].update(
            check={"type": "command_matches", "pattern": "^ls(("}), "bad regex")


class LoadingTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="ta-valid-")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def write(self, name, content):
        with open(os.path.join(self.tmp, name), "w", encoding="utf-8") as fh:
            fh.write(content if isinstance(content, str) else json.dumps(content))

    def test_broken_files_are_reported_not_loaded(self):
        self.write(NAME, GOOD)
        self.write("98-broken.json", "{ nope")
        bad = copy.deepcopy(GOOD)
        bad["id"] = "97-bad"
        bad["level"] = 9
        self.write("97-bad.json", bad)
        loaded, problems = lessons.load_lessons(self.tmp)
        self.assertEqual([l["id"] for l in loaded], ["99-test-lesson"])
        self.assertEqual(len(problems), 2)

    def test_solution_check_finds_check_that_already_passes(self):
        lesson = copy.deepcopy(GOOD)
        lesson["steps"][0]["check"] = {"type": "file_exists", "path": "a.txt"}
        problems, _ = lessons.run_solution_check(lesson)
        self.assertTrue(any("already passes" in p for p in problems), problems)

    def test_solution_check_finds_wrong_solution(self):
        lesson = copy.deepcopy(GOOD)
        lesson["steps"][0]["solution"] = "mkdir y"
        problems, _ = lessons.run_solution_check(lesson)
        self.assertTrue(any("does not pass" in p for p in problems), problems)

    def test_solution_check_skips_missing_tools(self):
        lesson = copy.deepcopy(GOOD)
        lesson["steps"][0]["requires"] = ["no-such-tool-ta-12345"]
        lesson["steps"][1]["solution"] = "mkdir x\nls"
        problems, skipped = lessons.run_solution_check(lesson)
        self.assertEqual(problems, [])
        self.assertEqual(len(skipped), 1)

    def test_setup_creates_files_with_modes(self):
        sandbox = os.path.join(self.tmp, GOOD["id"])
        lessons.setup_sandbox(GOOD, sandbox)
        with open(os.path.join(sandbox, "a.txt"), encoding="utf-8") as fh:
            self.assertEqual(fh.read(), "hi\n")
        self.assertEqual(os.stat(os.path.join(sandbox, "a.txt")).st_mode & 0o777, 0o644)
        self.assertEqual(os.stat(os.path.join(sandbox, "box")).st_mode & 0o777, 0o700)

    def test_setup_refuses_unexpected_folder(self):
        with self.assertRaises(ValueError):
            lessons.setup_sandbox(GOOD, os.path.join(self.tmp, "not-the-lesson-id"))


if __name__ == "__main__":
    unittest.main()
