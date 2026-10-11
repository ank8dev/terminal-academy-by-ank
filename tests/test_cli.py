"""The command line: ``./academy`` and ``python3 -m terminal_academy``.

Every test uses a temporary TERMINAL_ACADEMY_HOME, so your real
~/.terminal-academy is never touched.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from terminal_academy import __version__  # noqa: E402
from terminal_academy.lessons import load_lessons  # noqa: E402

LESSON_03 = [
    "help",
    "hint",
    "mkdir projects",
    "mkdir -p projects/game/levels",
    "touch projects/game/notes.txt",
    "cp projects/game/notes.txt projects/game/notes_backup.txt",
    "sudo rm -rf /",            # blocked, nothing happens
    "mv old_name.txt new_name.txt",
    "rm junk.txt",
    "rmdir empty_box",
]


class CliTest(unittest.TestCase):
    def setUp(self):
        self.home = tempfile.mkdtemp(prefix="ta-cli-")

    def tearDown(self):
        shutil.rmtree(self.home, ignore_errors=True)

    def env(self, allow_root=True):
        env = dict(os.environ)
        env["TERMINAL_ACADEMY_HOME"] = self.home
        env["NO_COLOR"] = "1"
        env["PYTHONIOENCODING"] = "utf-8"  # same symbols on every machine
        env.pop("TERMINAL_ACADEMY_TIMEOUT", None)
        if allow_root:
            env["TERMINAL_ACADEMY_ALLOW_ROOT"] = "1"
        else:
            env.pop("TERMINAL_ACADEMY_ALLOW_ROOT", None)
        return env

    def run_app(self, args, stdin="", launcher=False, allow_root=True):
        cmd = ([os.path.join(REPO, "academy")] if launcher
               else [sys.executable, "-m", "terminal_academy"])
        return subprocess.run(
            cmd + list(args), cwd=REPO, env=self.env(allow_root),
            input=stdin, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            universal_newlines=True, timeout=60,
        )

    def test_version_module(self):
        r = self.run_app(["--version"])
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn(__version__, r.stdout)

    @unittest.skipIf(shutil.which("python3") is None, "the launcher needs python3 on PATH")
    def test_version_launcher(self):
        r = self.run_app(["--version"], launcher=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.strip(), "Terminal Academy " + __version__)

    @unittest.skipIf(shutil.which("python3") is None, "the launcher needs python3 on PATH")
    def test_launcher_works_from_another_folder(self):
        r = subprocess.run([os.path.join(REPO, "academy"), "--version"], cwd=self.home,
                           env=self.env(), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           universal_newlines=True, timeout=60)
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_help(self):
        r = self.run_app(["--help"])
        self.assertEqual(r.returncode, 0)
        for word in ("list", "start", "reset", "--no-color", "--home", "--version"):
            self.assertIn(word, r.stdout)

    def test_list_shows_lesson_titles(self):
        r = self.run_app(["list"])
        self.assertEqual(r.returncode, 0, r.stderr)
        lessons, _ = load_lessons()
        for lesson in lessons:
            self.assertIn(lesson["title"], r.stdout)
        self.assertNotIn("\033[", r.stdout)  # NO_COLOR works

    def test_list_with_home_option(self):
        other = os.path.join(self.home, "other")
        r = self.run_app(["list", "--home", other, "--no-color"])
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(os.path.isdir(other))

    def test_unknown_lesson(self):
        r = self.run_app(["start", "999"])
        self.assertEqual(r.returncode, 2)
        self.assertIn("Unknown lesson", r.stdout)

    def test_play_lesson_03_end_to_end(self):
        stdin = "\n".join(LESSON_03 + ["n", "q"]) + "\n"
        r = self.run_app(["start", "3"], stdin=stdin)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("Lesson complete: Files and Folders", r.stdout)
        self.assertIn("Hint 1/2", r.stdout)
        self.assertIn("Blocked:", r.stdout)
        self.assertIn("Step 6 of 6", r.stdout)
        with open(os.path.join(self.home, "progress.json"), encoding="utf-8") as fh:
            entry = json.load(fh)["lessons"]["03-files-and-folders"]
        self.assertEqual(entry["status"], "done")
        self.assertEqual(entry["step"], 6)
        self.assertEqual(entry["hints_used"], 1)
        self.assertEqual(entry["skipped"], [])
        sandbox = os.path.join(self.home, "sandbox", "03-files-and-folders")
        self.assertTrue(os.path.isfile(os.path.join(sandbox, "new_name.txt")))

        # `list` now shows the lesson as done, and `reset -y` forgets it.
        r = self.run_app(["list"])
        self.assertIn("✓  3", r.stdout.replace("\033", ""))
        r = self.run_app(["reset", "3", "-y"])
        self.assertEqual(r.returncode, 0, r.stderr)
        with open(os.path.join(self.home, "progress.json"), encoding="utf-8") as fh:
            self.assertNotIn("03-files-and-folders", json.load(fh)["lessons"])
        self.assertFalse(os.path.exists(sandbox))

    def test_skip_and_quit(self):
        stdin = "skip\ny\nquit\n"
        r = self.run_app(["start", "3"], stdin=stdin)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("mkdir projects", r.stdout)
        with open(os.path.join(self.home, "progress.json"), encoding="utf-8") as fh:
            entry = json.load(fh)["lessons"]["03-files-and-folders"]
        self.assertEqual(entry["status"], "in_progress")
        self.assertEqual(entry["step"], 1)
        self.assertEqual(entry["skipped"], [0])

    def test_ctrl_d_quits(self):
        r = self.run_app(["start", "1"], stdin="")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    @unittest.skipUnless(hasattr(os, "geteuid") and os.geteuid() == 0,
                         "only meaningful when the tests run as root")
    def test_root_is_refused(self):
        r = self.run_app(["list"], allow_root=False)
        self.assertEqual(r.returncode, 1)
        self.assertIn("root", r.stdout)
        r = self.run_app(["list", "--allow-root"], allow_root=False)
        self.assertEqual(r.returncode, 0, r.stderr)


if __name__ == "__main__":
    unittest.main()
