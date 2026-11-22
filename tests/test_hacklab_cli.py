"""Part 2: the ``academy hack`` command wiring (no Docker needed).

These drive the real CLI as a subprocess, like test_cli.py. They avoid the
paths that need a Docker daemon (start/stop); 'list', 'learn' and 'submit'
work without one.
"""

import os
import shutil
import subprocess
import sys
import tempfile
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from terminal_academy.hacklab.levels import load_levels  # noqa: E402


class HackCliTest(unittest.TestCase):
    def setUp(self):
        self.home = tempfile.mkdtemp(prefix="ta-hackcli-")

    def tearDown(self):
        shutil.rmtree(self.home, ignore_errors=True)

    def run_app(self, args, stdin=""):
        env = dict(os.environ)
        env["TERMINAL_ACADEMY_HOME"] = self.home
        env["NO_COLOR"] = "1"
        env["TERMINAL_ACADEMY_ALLOW_ROOT"] = "1"
        return subprocess.run(
            [sys.executable, "-m", "terminal_academy", *args],
            cwd=REPO, env=env, input=stdin,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            universal_newlines=True, timeout=60,
        )

    def test_hack_list_shows_levels(self):
        r = self.run_app(["hack", "list"])
        self.assertEqual(r.returncode, 0, r.stderr)
        levels, _ = load_levels()
        for level in levels:
            self.assertIn(level.title, r.stdout)
        # The ethics note must be shown.
        self.assertIn("Never use these techniques", r.stdout)

    def test_hack_default_action_is_list(self):
        r = self.run_app(["hack"])
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("Ethical Hacking", r.stdout)

    def test_hack_learn_shows_defenses(self):
        r = self.run_app(["hack", "learn", "1"])
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("How defenders prevent this", r.stdout)

    def test_hack_learn_unknown_level(self):
        r = self.run_app(["hack", "learn", "99"])
        self.assertEqual(r.returncode, 2)
        self.assertIn("Unknown level", r.stdout)

    def test_hack_submit_without_run_fails_cleanly(self):
        # No level has started, so no flag hash is stored: submit must fail,
        # not crash.
        r = self.run_app(["hack", "submit", "1", "FLAG{whatever}"])
        self.assertEqual(r.returncode, 1)
        self.assertIn("not the flag", r.stdout)

    def test_help_mentions_hack(self):
        r = self.run_app(["--help"])
        self.assertEqual(r.returncode, 0)
        self.assertIn("hack", r.stdout)


if __name__ == "__main__":
    unittest.main()
