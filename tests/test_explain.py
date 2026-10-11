"""Offline ``explain <command>`` notes."""

import io
import os
import shutil
import sys
import tempfile
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from terminal_academy import explain  # noqa: E402
from terminal_academy.engine import LessonSession  # noqa: E402
from terminal_academy.lessons import load_lessons  # noqa: E402
from terminal_academy.progress import Progress  # noqa: E402
from terminal_academy.ui import UI  # noqa: E402


class ExplainTest(unittest.TestCase):
    def test_known_commands(self):
        for cmd in ("ls", "cd", "pwd", "grep", "chmod", "ssh-keygen", "|", ">"):
            with self.subTest(cmd=cmd):
                note = explain.lookup(cmd)
                self.assertIsInstance(note, str)
                self.assertTrue(note.strip())

    def test_full_command_line_uses_first_word(self):
        self.assertEqual(explain.lookup("ls -la /tmp"), explain.lookup("ls"))
        self.assertEqual(explain.lookup("/bin/ls"), explain.lookup("ls"))
        self.assertEqual(explain.lookup("  grep -i x  "), explain.lookup("grep"))

    def test_aliases(self):
        self.assertEqual(explain.lookup("bash"), explain.lookup("sh"))
        self.assertEqual(explain.lookup(">>"), explain.lookup(">"))
        self.assertEqual(explain.lookup("python"), explain.lookup("python3"))

    def test_unknown(self):
        self.assertIsNone(explain.lookup("frobnicate"))
        self.assertIsNone(explain.lookup(""))
        self.assertIsNone(explain.lookup("   "))

    def test_topics(self):
        topics = explain.topics()
        self.assertIn("ls", topics)
        self.assertEqual(topics, sorted(topics))


class ExplainInLessonTest(unittest.TestCase):
    """What the student sees when typing ``explain ...`` in a lesson."""

    def setUp(self):
        self.home = tempfile.mkdtemp(prefix="ta-explain-")
        lessons, _ = load_lessons()
        self.out = io.StringIO()
        self.session = LessonSession(
            lessons[0], self.home, Progress(os.path.join(self.home, "progress.json")),
            UI(out=self.out, color=False), input_func=lambda _p: "", use_tty=False,
        )

    def tearDown(self):
        self.session.shell.cleanup()
        shutil.rmtree(self.home, ignore_errors=True)

    def test_known(self):
        self.session._handle("explain ls")
        self.assertIn("ls lists what is in a folder", self.out.getvalue())

    def test_unknown_is_friendly(self):
        self.session._handle("explain frobnicate --now")
        text = self.out.getvalue()
        self.assertIn("I don't have a note about", text)
        self.assertIn("man frobnicate", text)

    def test_no_argument_lists_topics(self):
        self.session._handle("explain")
        self.assertIn("I have notes about these commands", self.out.getvalue())


if __name__ == "__main__":
    unittest.main()
